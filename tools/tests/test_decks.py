"""Testes dos decks de orientacao do SI08 T18.

Rodar a partir da raiz deste projeto:
    python3 -m pytest tools/tests/ -v
"""
import glob
import html.parser
import os
import subprocess
import sys
import time

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "tools"))

import check_brand  # noqa: E402

IDIOMAS = {"en", "pt", "fr"}
DECKS = sorted(
    p for p in glob.glob(os.path.join(RAIZ, "aulas", "*.html"))
    if not os.path.basename(p).startswith("_")
)


class _Coletor(html.parser.HTMLParser):
    """Agrupa os data-l por elemento pai e guarda todo src/href local."""

    def __init__(self):
        super().__init__()
        self.pilha = []
        self.grupos = {}
        self.refs = []
        self.contador = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.pilha and "data-l" in a:
            pai = self.pilha[-1]
            self.grupos.setdefault(pai, []).append((a["data-l"], self.getpos()[0]))
        for chave in ("src", "href"):
            v = a.get(chave)
            if v and not v.startswith(("http://", "https://", "#", "mailto:")):
                self.refs.append(v)
        if tag in ("img", "meta", "link", "br", "hr", "input"):
            return
        self.contador += 1
        self.pilha.append(self.contador)

    def handle_endtag(self, tag):
        if tag in ("img", "meta", "link", "br", "hr", "input"):
            return
        if self.pilha:
            self.pilha.pop()


def _coletar(deck):
    c = _Coletor()
    with open(deck, encoding="utf-8") as fh:
        c.feed(fh.read())
    return c


def test_existe_ao_menos_um_deck():
    assert DECKS, "nenhum deck em aulas/"


@pytest.mark.parametrize("deck", DECKS, ids=os.path.basename)
def test_todo_texto_existe_nos_tres_idiomas(deck):
    grupos = _coletar(deck).grupos
    assert grupos, "deck sem nenhum data-l"
    for linhas in grupos.values():
        langs = [l for l, _ in linhas]
        assert sorted(langs) == sorted(IDIOMAS), (
            "grupo na linha %d tem %s, esperado en/pt/fr uma vez cada"
            % (linhas[0][1], langs)
        )


@pytest.mark.parametrize("deck", DECKS, ids=os.path.basename)
def test_sem_travessao(deck):
    with open(deck, encoding="utf-8") as fh:
        for n, linha in enumerate(fh, start=1):
            assert "—" not in linha and "&mdash;" not in linha, "travessao na linha %d" % n


@pytest.mark.parametrize("deck", DECKS, ids=os.path.basename)
def test_referencias_locais_existem(deck):
    base = os.path.dirname(deck)
    for ref in _coletar(deck).refs:
        alvo = os.path.normpath(os.path.join(base, ref.split("?")[0]))
        assert os.path.exists(alvo), "referencia quebrada: %s" % ref


def test_fidelidade_ao_brandbook():
    achados = check_brand.varrer(RAIZ)
    assert achados == [], achados


# ---------------------------------------------------------------- navegador
playwright = pytest.importorskip("playwright.sync_api")


@pytest.fixture(scope="module")
def servidor():
    porta = 8791
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(porta), "--directory", RAIZ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    yield "http://127.0.0.1:%d" % porta
    proc.terminate()


@pytest.fixture(scope="module")
def pagina():
    with playwright.sync_playwright() as p:
        nav = p.chromium.launch()
        pg = nav.new_page(viewport={"width": 1280, "height": 720})
        yield pg
        nav.close()


JS_VISIVEIS = """
() => [...document.querySelectorAll('[data-l]')]
  .filter(el => getComputedStyle(el).display !== 'none')
  .map(el => el.dataset.l)
"""


@pytest.mark.parametrize("lang", sorted(IDIOMAS))
def test_parametro_lang_mostra_so_um_idioma(servidor, pagina, lang):
    pagina.goto(servidor + "/aulas/onboarding.html?lang=" + lang, wait_until="networkidle")
    assert pagina.evaluate("document.documentElement.dataset.lang") == lang
    visiveis = set(pagina.evaluate(JS_VISIVEIS))
    assert visiveis == {lang}


def test_padrao_e_ingles_e_tecla_l_alterna(servidor, pagina):
    pagina.goto(servidor + "/aulas/onboarding.html", wait_until="networkidle")
    pagina.evaluate("localStorage.clear()")
    pagina.goto(servidor + "/aulas/onboarding.html", wait_until="networkidle")
    assert pagina.evaluate("document.documentElement.dataset.lang") == "en"
    sequencia = []
    for _ in range(3):
        pagina.keyboard.press("l")
        sequencia.append(pagina.evaluate("document.documentElement.dataset.lang"))
    assert sequencia == ["pt", "fr", "en"]


def test_botao_troca_idioma_e_persiste(servidor, pagina):
    pagina.goto(servidor + "/aulas/onboarding.html", wait_until="networkidle")
    pagina.click(".lang-switch button[data-lang='fr']")
    assert pagina.evaluate("document.documentElement.lang") == "fr"
    pagina.reload(wait_until="networkidle")
    assert pagina.evaluate("document.documentElement.dataset.lang") == "fr"
    pagina.evaluate("localStorage.clear()")


@pytest.mark.parametrize("lang", sorted(IDIOMAS))
def test_layout_cabe_em_1280x720_em_cada_idioma(lang):
    rel = "aulas/onboarding.html?lang=" + lang
    r = subprocess.run(
        [sys.executable, os.path.join(RAIZ, "tools", "check_slides.py"), rel],
        cwd=RAIZ, capture_output=True, text=True, timeout=180,
    )
    assert r.returncode == 0, r.stdout[-2000:]


# ---------------------------------------------------------------- conteudo
import datetime  # noqa: E402
import re  # noqa: E402

DIAS_EN = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4}


@pytest.mark.parametrize("deck", DECKS, ids=os.path.basename)
def test_rodape_numerado_pela_posicao_do_slide(deck):
    texto = open(deck, encoding="utf-8").read()
    secoes = re.findall(r"<section.*?</section>", texto, flags=re.S)
    for i, sec in enumerate(secoes, start=1):
        m = re.search(r'<p class="footer-page">(\d+)</p>', sec)
        if m:
            assert int(m.group(1)) == i, "slide %d com rodape %s" % (i, m.group(1))


@pytest.mark.parametrize("deck", DECKS, ids=os.path.basename)
def test_dia_da_semana_bate_com_a_data(deck):
    """Todo "Wed 21/10" em ingles precisa cair mesmo naquele dia em 2026.
    PT e FR sao traducao do mesmo par, entao conferir o EN cobre os tres."""
    texto = open(deck, encoding="utf-8").read()
    pares = re.findall(r'data-l="en">(Mon|Tue|Wed|Thu|Fri) (\d{2})/(\d{2})', texto)
    assert pares, "nenhuma data com dia da semana encontrada"
    for dia, d, m in pares:
        data = datetime.date(2026, int(m), int(d))
        assert data.weekday() == DIAS_EN[dia], "%s %s/%s cai em outro dia" % (dia, d, m)


# ---------------------------------------------------------------- LBL e grupos
import csv  # noqa: E402

import extrair_lbl  # noqa: E402

DECK_ONB = os.path.join(RAIZ, "aulas", "onboarding.html")


def _linha(semana, nome, peso, tipo="Autoestudo", aluno="A", grupo="G01", ativo="Sim", data=""):
    return {"Atividade_Semana": semana, "Atividade_Nome": nome, "Atividade_Peso": peso,
            "Atividade_Tipo": tipo, "Atividade_Professor_Nome": "", "Atividade_Data_Inicio": data,
            "Aluno_Nome": aluno, "Grupo_Nome": grupo, "Aluno_Ativo_Na_Turma": ativo}


def test_sexta_e_sprint_da_semana():
    assert extrair_lbl.sexta_da_semana("Semana 01") == datetime.date(2026, 10, 16)
    assert extrair_lbl.sexta_da_semana("Semana 06") == datetime.date(2026, 11, 20)
    assert [extrair_lbl.sprint_da_semana("Semana %02d" % n) for n in range(1, 11)] == \
        [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]


def test_ponderadas_ignora_peso_zero_e_deduplica_por_aluno():
    linhas = [_linha("Semana 02", "X", "4", aluno="A"), _linha("Semana 02", "X", "4", aluno="B"),
              _linha("Semana 02", "Leitura", "0"), _linha("Semana 02", "Vazia", "")]
    out = extrair_lbl.ponderadas(linhas)
    assert [a["nome"] for a in out] == ["X"]
    assert out[0]["data"] == "23/10/2026" and out[0]["sprint"] == 1


def test_grupos_so_alunos_ativos_em_ordem():
    linhas = [_linha("Semana 01", "a", "0", aluno="Zoe", grupo="G02"),
              _linha("Semana 01", "a", "0", aluno="Ana", grupo="G02"),
              _linha("Semana 01", "b", "0", aluno="Ana", grupo="G02"),
              _linha("Semana 01", "a", "0", aluno="Saiu", grupo="G01", ativo="Não")]
    assert extrair_lbl.grupos(linhas) == {"G02": ["Ana", "Zoe"]}


def test_slide_de_entregas_bate_com_o_csv():
    ativ = list(csv.DictReader(open(os.path.join(RAIZ, "dados", "atividades_ponderadas.csv"),
                                    encoding="utf-8")))
    assert sum(float(a["peso"]) for a in ativ) == 100
    html_deck = open(DECK_ONB, encoding="utf-8").read()
    for a in ativ:
        trecho = '<span class="item-nome">%s</span> <span class="item-meta">%.0f%% &middot; %s</span>' % (
            a["nome"], float(a["peso"]), a["data"][:5])
        assert trecho in html_deck, a["nome"]


def test_parceiro_se_chama_brazilian_army():
    html_deck = open(DECK_ONB, encoding="utf-8").read()
    assert "<h3>Brazilian Army</h3>" in html_deck
    assert not re.search(r"Arm[ée]e|Exército Brasileiro", html_deck)


def test_slide_de_grupos_lista_todos_os_alunos(servidor, pagina):
    pagina.goto(servidor + "/aulas/onboarding.html?lang=en", wait_until="networkidle")
    nomes = pagina.evaluate(
        "[...document.querySelectorAll('section[data-local=grupos] .grupo-col li')].map(e => e.textContent)")
    esperado = pagina.evaluate("Object.values(window.SI08_GRUPOS).flat()")
    assert nomes and sorted(nomes) == sorted(esperado)
    assert pagina.evaluate("Reveal.getTotalSlides()") == 14


def test_sem_dados_de_grupo_o_slide_some_sem_mexer_na_numeracao(servidor, pagina):
    pagina.route("**/dados/grupos.js", lambda rota: rota.abort())
    try:
        pagina.goto(servidor + "/aulas/onboarding.html?lang=en", wait_until="networkidle")
        assert pagina.evaluate("document.querySelectorAll('[data-local=grupos]').length") == 0
        assert pagina.evaluate("Reveal.getTotalSlides()") == 13
        rodapes = pagina.evaluate(
            "[...document.querySelectorAll('.footer-page')].map(e => +e.textContent)")
        assert rodapes == list(range(2, 2 + len(rodapes)))
    finally:
        pagina.unroute("**/dados/grupos.js")
