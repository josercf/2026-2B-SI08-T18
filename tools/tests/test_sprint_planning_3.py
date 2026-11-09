"""Testes do deck de Sprint Planning 3 e do quadro de post-its (ADR-006).

Os testes genericos de deck (tres idiomas, referencias locais, rodape, dia da semana, layout)
ja cobrem o deck via test_decks.py. Aqui ficam a coerencia do gerador, dos avisos, das
perguntas entre deck e quadro, a seguranca do SQL e o fluxo do quadro em modo de ensaio.

Rodar a partir da raiz deste projeto:
    python3 -m pytest tools/tests/test_sprint_planning_3.py -v
"""
import functools
import http.server
import os
import re
import sys
import threading

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "tools"))

import gerar_sprint_planning_3 as gen  # noqa: E402

DECK = os.path.join(RAIZ, "aulas", "sprint-planning-3.html")
QUADRO_JS = os.path.join(RAIZ, "assets", "js", "reflexao.js")
QUADRO_HTML = os.path.join(RAIZ, "quadro", "reflexao-sprint2.html")
SQL = os.path.join(RAIZ, "supabase", "reflexao.sql")


def _ler(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


# ------------------------------------------------------------------ deck
def test_deck_esta_atualizado_com_o_gerador():
    assert _ler(DECK) == gen.gerar()


def test_roteiro_soma_120_minutos_sem_buraco():
    fim_anterior = "14:00"
    for inicio, fim, _, _ in gen.ROTEIRO:
        assert inicio == fim_anterior, (inicio, fim_anterior)
        fim_anterior = fim
    assert fim_anterior == "16:00"


def test_estrutura_executiva_cabe_em_5_minutos():
    assert sum(e[3] for e in gen.ESTRUTURA) == 300
    assert [e[1] for e in gen.ESTRUTURA][:3] == ["Agenda", "Objetivo da sprint", "Status report"]


@pytest.mark.parametrize("trecho", [
    "18/11", "19/11", "20/11", "G01 10h", "G02 10h30", "G03 11h", "G04 11h30", "G05 16h20",
    "12/11, 23h59", "hoje, 16h", "2 por grupo",
])
def test_avisos_trazem_datas_e_horarios_combinados(trecho):
    assert trecho in _ler(DECK)


def test_sprint_3_soma_10_por_cento():
    assert "reúne 10% do peso do módulo em 2 entregas" in _ler(DECK)


@pytest.mark.parametrize("arquivo", [DECK, QUADRO_JS, QUADRO_HTML, SQL,
                                     os.path.join(RAIZ, "tools", "gerar_sprint_planning_3.py")])
def test_sem_travessao(arquivo):
    assert "—" not in _ler(arquivo)


# ------------------------------------------------------------------ perguntas
def _perguntas_js():
    js = _ler(QUADRO_JS)
    return re.findall(r"pt: '([^']+)'", js.split("var TEXTOS")[0])


def test_perguntas_do_deck_e_do_quadro_sao_as_mesmas():
    assert _perguntas_js() == [q[1] for q in gen.PERGUNTAS]


def test_sql_aceita_todas_as_perguntas():
    limite = int(re.search(r"pergunta between 1 and (\d+)", _ler(SQL)).group(1))
    assert len(gen.PERGUNTAS) <= limite


# ------------------------------------------------------------------ seguranca do SQL
def test_toda_tabela_refl_tem_rls_e_nenhuma_policy():
    sql = _ler(SQL)
    tabelas = re.findall(r"create table if not exists (refl_\w+)", sql)
    assert set(tabelas) == {"refl_tokens", "refl_membros", "refl_prazos", "refl_postits"}
    for t in tabelas:
        assert "alter table %s enable row level security" % t in sql, t
    assert "create policy" not in sql.lower()


def test_funcoes_publicas_sao_security_definer_e_internas_sem_grant():
    sql = _ler(SQL)
    funcoes = re.findall(r"create or replace function (refl_\w+)\(", sql)
    blocos = re.split(r"create or replace function ", sql)[1:]
    for b in blocos:
        assert "security definer set search_path = public, extensions" in b.split("$$")[0], b[:40]
    internas = {"refl_token_ok", "refl_checar_escrita"}
    for f in funcoes:
        concedida = re.search(r"grant execute on function %s\(" % f, sql)
        assert bool(concedida) == (f not in internas), f


def test_acoes_do_professor_exigem_a_chave():
    sql = _ler(SQL)
    for f in ("refl_links", "refl_prazo", "refl_painel"):
        corpo = sql.split("function %s(" % f)[1].split("end $$")[0]
        assert "quiz_chave_ok(p_chave)" in corpo, f


def test_escrita_do_grupo_passa_pela_checagem():
    sql = _ler(SQL)
    for f in ("refl_postar", "refl_editar", "refl_apagar"):
        corpo = sql.split("function %s(" % f)[1].split("end $$")[0]
        assert "refl_checar_escrita(" in corpo, f
    for f in ("refl_editar", "refl_apagar"):
        corpo = sql.split("function %s(" % f)[1].split("end $$")[0]
        assert "autor = p_autor" in corpo, f


def test_sem_chave_do_professor_no_repositorio():
    for raiz, _, arquivos in os.walk(RAIZ):
        if ".git" in raiz or "__pycache__" in raiz:
            continue
        for a in arquivos:
            if a.endswith((".js", ".html", ".py", ".sql", ".md")):
                assert not re.search(r"quiz-chave=[A-Za-z0-9_-]{6,}", _ler(os.path.join(raiz, a))), a


# ------------------------------------------------------------------ quadro em modo de ensaio
@pytest.fixture(scope="module")
def servidor():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=RAIZ)
    handler.log_message = lambda *a, **k: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield "http://127.0.0.1:%d" % srv.server_address[1]
    srv.shutdown()


@pytest.fixture(scope="module")
def navegador():
    pw = pytest.importorskip("playwright.sync_api")
    with pw.sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _abrir(navegador, servidor, query, largura=1280):
    pg = navegador.new_page(viewport={"width": largura, "height": 800})
    erros = []
    pg.on("pageerror", lambda e: erros.append(str(e)))
    # Sem rede para o CDN do Supabase: o modo de ensaio nao pode depender dele.
    pg.route("https://cdn.jsdelivr.net/**", lambda r: r.abort())
    pg.goto("%s/quadro/reflexao-sprint2.html?%s" % (servidor, query))
    return pg, erros


def test_quadro_pede_o_nome_e_mostra_um_bloco_por_integrante(navegador, servidor):
    pg, erros = _abrir(navegador, servidor, "g=G03&demo=1&lang=pt")
    pg.wait_for_selector(".refl-modal")
    assert pg.locator(".refl-nome").count() == 7
    pg.click(".refl-nome >> nth=0")
    assert pg.locator(".refl-bloco").count() == 7
    assert pg.locator(".refl-bloco.meu").count() == 1
    assert pg.locator(".refl-novo").count() == 1, "só o próprio bloco tem campo de escrita"
    assert not erros, erros


def test_post_it_sai_assinado_e_conta_na_aba(navegador, servidor):
    pg, erros = _abrir(navegador, servidor, "g=G01&demo=1&lang=pt")
    pg.wait_for_selector(".refl-modal")
    nome = pg.locator(".refl-nome >> nth=1 >> span >> nth=1").inner_text()
    pg.click(".refl-nome >> nth=1")
    pg.fill(".refl-bloco.meu .refl-novo textarea", "Objetivo: ingestão no ClickHouse")
    pg.click(".refl-colar")
    pg.wait_for_selector(".refl-postit.meu")
    assert nome in pg.locator(".refl-bloco.meu .refl-bloco-nome").inner_text()
    assert pg.locator(".refl-aba >> nth=0 >> .refl-aba-qtd").inner_text() == "1"
    pg.click(".refl-aba >> nth=1")
    assert pg.locator(".refl-postit").count() == 0, "post-it fica só na pergunta em que foi escrito"
    assert not erros, erros


def test_editar_e_apagar_o_proprio_post_it(navegador, servidor):
    pg, _ = _abrir(navegador, servidor, "g=G02&demo=1&lang=pt")
    pg.wait_for_selector(".refl-modal")
    pg.click(".refl-nome >> nth=0")
    pg.fill(".refl-bloco.meu .refl-novo textarea", "primeira versão")
    pg.click(".refl-colar")
    pg.wait_for_selector(".refl-postit.meu")
    pg.click(".refl-postit.meu .refl-mini >> nth=0")
    pg.fill(".refl-postit.meu textarea", "versão revista")
    pg.click(".refl-postit.meu .refl-mini")
    pg.wait_for_selector(".refl-postit.meu .refl-texto")
    assert pg.locator(".refl-postit.meu .refl-texto").inner_text() == "versão revista"
    pg.click(".refl-postit.meu .refl-mini >> nth=1")
    pg.wait_for_timeout(300)
    assert pg.locator(".refl-postit.meu").count() == 0


def test_link_sem_token_nao_abre_o_quadro(navegador, servidor):
    pg, _ = _abrir(navegador, servidor, "g=G09&demo=1&lang=pt")
    pg.wait_for_selector(".refl-erro.grande")
    assert pg.locator(".refl-bloco").count() == 0


def test_quadro_cabe_no_celular(navegador, servidor):
    pg, _ = _abrir(navegador, servidor, "g=G04&demo=1&lang=fr", largura=390)
    pg.wait_for_selector(".refl-modal")
    pg.click(".refl-nome >> nth=0")
    assert not pg.evaluate("document.documentElement.scrollWidth > window.innerWidth")


def test_seed_do_banco_tem_todo_integrante_com_o_nome_do_quadro():
    import json
    bruto = _ler(os.path.join(RAIZ, "dados", "grupos.js"))
    grupos = json.loads(bruto[bruto.index("{"):bruto.rindex("}") + 1])
    seed = _ler(os.path.join(RAIZ, "supabase", "reflexao_seed.sql"))
    linhas = re.findall(r"\('si08t18-sp3-2026-11-09', '(G\d\d)', '([^']+)', \d+\)", seed)
    apelidos = {"Giovanna Rodrigues": "Giovanna Neves", "Matheus Silva": "Matheus Scapolan",
                "Iris Roux": "Iris Le Roux"}  # nome pelo qual a turma conhece o aluno no Slack
    curto = lambda n: n.split()[0] + " " + n.split()[-1]  # noqa: E731
    esperado = sorted((g, apelidos.get(curto(n), curto(n))) for g, ns in grupos.items() for n in ns)
    assert sorted(linhas) == esperado
    assert "var SESSAO = 'si08t18-sp3-2026-11-09'" in _ler(QUADRO_JS)


def test_toda_foto_publicada_e_jpeg_pequeno_de_um_integrante():
    import json
    import unicodedata
    pasta = os.path.join(RAIZ, "assets", "img", "alunos")
    fotos = sorted(os.listdir(pasta))
    assert len(fotos) == 39
    for f in fotos:
        caminho = os.path.join(pasta, f)
        with open(caminho, "rb") as fh:
            assert fh.read(3) == b"\xff\xd8\xff", f
        assert os.path.getsize(caminho) < 40_000, f


# ------------------------------------------------------------------ plannings por grupo
PLANNINGS = os.path.join(RAIZ, "planning", "sprint3")
TAMANHO = {"S": 15, "M": 30, "L": 60, "XL": 120}
INTEGRANTES = {"G01": 8, "G02": 8, "G03": 7, "G04": 8, "G05": 8}


@pytest.mark.parametrize("grupo", sorted(INTEGRANTES))
def test_planning_do_grupo_tem_as_sete_secoes_e_cartoes_suficientes(grupo):
    texto = _ler(os.path.join(PLANNINGS, "planning-sprint3-%s.md" % grupo))
    assert "—" not in texto
    titulos = re.findall(r"^## (\d)\. ", texto, re.M)
    assert titulos == [str(i) for i in range(1, 8)], titulos
    ids = re.findall(r"^\| (S3-[A-Z]\d\d) \|", texto, re.M)
    assert len(ids) == len(set(ids)), "ID repetido"
    assert re.search(r"\| Members \| %d \|" % INTEGRANTES[grupo], texto)
    total = re.search(r"\| \*\*Total\*\* \| \*\*(\d+)\*\* \|", texto)
    assert total, "tabela de volume sem total"
    assert int(total.group(1)) >= 7 * INTEGRANTES[grupo]


def test_deck_aponta_para_as_cinco_plannings():
    html = _ler(DECK)
    for g in sorted(INTEGRANTES):
        assert "planning/sprint3/planning-sprint3-%s.md" % g in html
