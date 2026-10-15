"""Testes do deck de planning e gestao no GitLab (aulas/planning-gitlab.html).

Os testes genericos de deck (tres idiomas, travessao, referencias locais,
rodape, dia da semana) ja cobrem este deck via test_decks.py. Aqui ficam as
regras de conteudo do orientador e o estado final das animacoes (ADR-004).

Rodar a partir da raiz deste projeto:
    python3 -m pytest tools/tests/test_planning.py -v
"""
import json
import os
import re
import subprocess
import sys
import time

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DECK = os.path.join(RAIZ, "aulas", "planning-gitlab.html")
URL = "/aulas/planning-gitlab.html"
IDIOMAS = ("en", "pt", "fr")


def _html():
    with open(DECK, encoding="utf-8") as fh:
        return fh.read()


def _grupos():
    with open(os.path.join(RAIZ, "dados", "grupos.js"), encoding="utf-8") as fh:
        texto = fh.read()
    return json.loads(texto[texto.index("{"):texto.rindex("}") + 1])


# ---------------------------------------------------------------- conteudo
def test_tshirt_respeita_teto_e_regra_de_revisao():
    """(b, c, d) Tamanhos 15/30/60/120; tarefa P tem revisao P; acima disso a
    revisao e pelo menos metade da estimativa; o total escrito bate."""
    html = _html()
    barras = re.findall(
        r'<g class="barra" data-tarefa="(\d+)" data-revisao="(\d+)".*?'
        r'<text class="barra-total mono"[^>]*>(\d+) \+ (\d+) = (\d+) min</text>',
        html, flags=re.S)
    assert [int(b[0]) for b in barras] == [15, 30, 60, 120]
    for tarefa, revisao, t_txt, r_txt, total in barras:
        tarefa, revisao = int(tarefa), int(revisao)
        assert tarefa <= 120
        if tarefa == 15:
            assert revisao == 15
        else:
            assert revisao * 2 >= tarefa
        assert (int(t_txt), int(r_txt), int(total)) == (tarefa, revisao, tarefa + revisao)


def test_divisao_gera_tarefas_g_de_60():
    """(c) A tarefa acima de 120 min vira tarefas G de 60, cada uma com revisao."""
    html = _html()
    assert html.count('<g class="metade metade-') == 2
    assert html.count('G &middot; 60 min') == 2
    assert html.count('class="revisao-nova') == 2


def test_minimo_de_tarefas_bate_com_os_grupos_reais():
    """(f) 10 dias uteis - planning - review = 8; 8 x alunos do grupo."""
    html = _html()
    m = re.search(r'class="cartao-total" data-dias="(\d+)" data-alunos="(\d+)" data-tarefas="(\d+)"', html)
    dias, alunos, tarefas = map(int, m.groups())
    assert dias == 10 - 1 - 1
    assert tarefas == dias * alunos
    tamanhos = {len(v) for v in _grupos().values()}
    assert alunos == max(tamanhos)
    g03 = re.search(r'class="grupo-g03" data-alunos="(\d+)" data-tarefas="(\d+)"', html)
    assert int(g03.group(1)) == len(_grupos()["G03"])
    assert int(g03.group(2)) == dias * int(g03.group(1))
    assert html.count('<rect class="celula ') == dias * alunos


def test_checklist_cobre_todas_as_regras():
    """O checklist final tem um item por regra combinada: 1 de kickoff,
    7 de planning (com corte por valor e DoR/DoD), 6 de daily (com scrum
    master, WIP e throughput) e 5 de codigo (com a piramide de revisao)."""
    html = _html()
    tabela = html[html.index('class="data-table checklist-tabela"'):]
    tabela = tabela[:tabela.index("</table>")]
    linhas = re.findall(r'<th scope="row">.*?</tr>', tabela, flags=re.S)
    assert [l.count("<li>") for l in linhas] == [1, 7, 6, 5]


def test_links_de_referencia_do_code_review():
    html = _html()
    assert "https://about.gitlab.com/pt-br/topics/version-control/what-is-code-review/" in html
    assert "https://www.swarmia.com/blog/a-complete-guide-to-code-reviews/" in html


def test_marcadores_de_geracao_foram_substituidos():
    html = _html()
    for marcador in ("CELULAS", "QUADRO-DAILY", "ANEL"):
        assert "<!-- %s -->" % marcador not in html


def test_wip_lead_time_medio_bate_com_a_linha_do_tempo():
    """WIP 5 entrega tudo no dia 5; WIP 1 entrega nos dias 1 a 5, media 3."""
    html = _html()
    linhas = re.findall(r'data-wip="(\d)" data-primeira="(\d)" data-lead-medio="(\d)"', html)
    assert sorted(linhas) == [("1", "1", "3"), ("5", "5", "5")]
    n = 5
    assert sum(range(1, n + 1)) / n == 3
    assert html.count('class="wip-seq ') == n and html.count('class="wip-par ') == n


def test_lei_de_little_e_fichas_em_fluxo():
    """lead time = WIP / throughput, e o desenho tem exatamente WIP fichas."""
    html = _html()
    contas = re.findall(r'class="little-conta[^"]*"(?: data-fragment-index="\d")? data-wip="(\d+)" '
                        r'data-throughput="(\d+)" data-lead="(\d+)"', html)
    assert len(contas) == 2
    for wip, vazao, lead in contas:
        assert int(wip) / int(vazao) == int(lead)
    for cenario, wip in re.findall(r'<g class="fluxo-(a|b)" data-wip="(\d+)">', html):
        bloco = html.split('<g class="fluxo-%s"' % cenario)[1].split("</g>")[0]
        assert bloco.count('class="ficha ') == int(wip)
    meta = re.search(r'class="cartao-meta" data-tarefas="(\d+)" data-dias="(\d+)" data-throughput="(\d+)"', html)
    tarefas, dias, vazao = map(int, meta.groups())
    assert tarefas / dias == vazao
    total = re.search(r'class="cartao-total" data-dias="(\d+)" data-alunos="(\d+)" data-tarefas="(\d+)"', html)
    assert int(total.group(3)) == tarefas and int(total.group(1)) == dias


def test_dor_e_dod_tem_cinco_criterios_e_um_bloqueio():
    html = _html()
    for painel in ("painel-dor", "painel-dod"):
        bloco = html.split('class="dod-painel %s"' % painel)[1].split("</ul>")[0]
        assert bloco.count("<li") == 5, painel
    assert html.split('class="dod-painel painel-dor"')[1].split("</ul>")[0].count('class="falta"') == 1
    assert html.split('class="dod-painel painel-dod"')[1].split("</ul>")[0].count('class="falta"') == 0


def test_fatia_vertical_atravessa_todas_as_camadas():
    html = _html()
    assert html.count("na-fatia") == 4
    assert html.count("na-camada") == 6


def test_piramide_segue_morling_com_credito():
    """Cinco camadas, da base ao topo como no original, 3 perguntas cada,
    e o credito exigido pela licenca CC BY-SA 4.0."""
    html = _html()
    camadas = re.findall(r'<g class="camada camada-(\w+)" style="--o: (\d)">', html)
    assert [c for c, _ in camadas] == ["estilo", "testes", "docs", "implementacao", "api"]
    assert [int(o) for _, o in camadas] == [4, 3, 2, 1, 0]
    for nome, _ in camadas:
        bloco = html.split('<g class="perguntas" data-camada="%s"' % nome)[1].split("\n          </g>")[0]
        assert bloco.count('<text data-l="pt"') == 3, nome
    assert "https://www.morling.dev/blog/the-code-review-pyramid/" in html
    assert html.count("(2022), CC BY-SA 4.0") == 3


def test_scrum_master_tem_papel_e_tres_cenas_de_desvio():
    html = _html()
    assert html.count('<div class="cena fragment">') == 3
    assert html.count('class="sm-entra"') == 3
    assert html.count('class="sm-papel"') == 2
    assert "Guardião do rito" in html and "guardião do rito" in html
    exemplos = html.split('class="regras-num sm-exemplos"')[1].split("</ol>")[0]
    assert exemplos.count("<li>") == 6


def test_dicas_de_corte_contrastam_artefato_e_valor():
    html = _html()
    assert html.count('class="corte-artefato"') == 3
    assert html.count('class="corte-valor"') == 3


# ---------------------------------------------------------------- navegador
playwright = pytest.importorskip("playwright.sync_api")


@pytest.fixture(scope="module")
def servidor():
    porta = 8792
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(porta), "--directory", RAIZ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    yield "http://127.0.0.1:%d" % porta
    proc.terminate()


@pytest.fixture(scope="module")
def navegador():
    with playwright.sync_playwright() as p:
        nav = p.chromium.launch()
        yield nav
        nav.close()


JS_TRANSLATE_X = """
sel => new DOMMatrix(getComputedStyle(document.querySelector(sel)).transform).e
"""


@pytest.mark.parametrize("lang", IDIOMAS)
def test_layout_cabe_em_1280x720_em_cada_idioma(lang):
    rel = "aulas/planning-gitlab.html?lang=" + lang
    r = subprocess.run(
        [sys.executable, os.path.join(RAIZ, "tools", "check_slides.py"), rel],
        cwd=RAIZ, capture_output=True, text=True, timeout=180,
    )
    assert r.returncode == 0, r.stdout[-2000:]


def test_passos_movem_o_card_pelo_quadro(servidor, navegador):
    """Cada fragment da legenda leva o card do ciclo para a coluna certa."""
    pg = navegador.new_page(viewport={"width": 1280, "height": 720})
    pg.goto(servidor + URL + "?lang=en#/2", wait_until="networkidle")
    esperado = {0: 12, 1: 248, 4: 484, 5: 720, 7: 956}
    for passo, x in esperado.items():
        pg.evaluate("n => Reveal.slide(2, 0, n - 1)", passo)
        pg.wait_for_timeout(900)
        assert pg.evaluate("document.querySelector('.ciclo').closest('section').dataset.passo") == str(passo)
        assert round(pg.evaluate(JS_TRANSLATE_X, ".ciclo .card-tarefa")) == x, passo
    pg.close()


def test_movimento_reduzido_mostra_o_estado_final(servidor, navegador):
    ctx = navegador.new_context(viewport={"width": 1280, "height": 720}, reduced_motion="reduce")
    pg = ctx.new_page()
    pg.goto(servidor + URL + "?lang=pt", wait_until="networkidle")
    assert pg.evaluate("document.documentElement.classList.contains('anim-final')")
    # Toda section com fragments recebe todos os passos.
    pares = pg.evaluate("""[...document.querySelectorAll('.reveal .slides > section')]
        .map(s => [s.querySelectorAll('.fragment').length, +(s.dataset.passo || 0)])""")
    assert all(n == p for n, p in pares), pares
    pg.evaluate("Reveal.slide(2)")
    assert round(pg.evaluate(JS_TRANSLATE_X, ".ciclo .card-tarefa")) == 956
    # Nenhuma animacao em curso: o contador ja mostra 64.
    pg.evaluate("Reveal.slide(8)")
    assert pg.evaluate("getComputedStyle(document.querySelector('.contador')).animationName") == "none"
    assert pg.evaluate(
        "getComputedStyle(document.querySelector('.contador')).getPropertyValue('--contagem').trim()") == "64"
    ctx.close()


def test_pdf_mostra_o_estado_final(servidor, navegador):
    pg = navegador.new_page(viewport={"width": 1280, "height": 720})
    pg.goto(servidor + URL + "?lang=fr&print-pdf", wait_until="networkidle")
    assert pg.evaluate("document.documentElement.classList.contains('anim-final')")
    assert round(pg.evaluate(JS_TRANSLATE_X, ".fluxo .novo")) == 248
    # DoR/DoD: card em Done e todas as marcas desenhadas.
    assert round(pg.evaluate(JS_TRANSLATE_X, ".portoes .card-portao")) == 946
    assert pg.evaluate("""[...document.querySelectorAll('.dod-lista .marca')]
        .every(m => parseFloat(getComputedStyle(m).strokeDashoffset) === 0)""")
    # Throughput: o cenario WIP 24 fica visivel.
    assert pg.evaluate("getComputedStyle(document.querySelector('.vazao .fluxo-b')).opacity") == "1"
    pg.close()


def test_total_de_slides(servidor, navegador):
    pg = navegador.new_page(viewport={"width": 1280, "height": 720})
    pg.goto(servidor + URL, wait_until="networkidle")
    assert pg.evaluate("Reveal.getTotalSlides()") == 22
    pg.close()
