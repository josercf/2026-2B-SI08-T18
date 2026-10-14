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
