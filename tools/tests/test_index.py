"""Testes do portal do modulo (index.html).

Rodar a partir da raiz deste projeto:
    python3 -m pytest tools/tests/test_index.py -v
"""
import glob
import html.parser
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INDEX = os.path.join(RAIZ, "index.html")
ONBOARDING = os.path.join(RAIZ, "aulas", "onboarding.html")


class _Coletor(html.parser.HTMLParser):
    VAZIOS = ("img", "meta", "link", "br", "hr", "input")

    def __init__(self):
        super().__init__()
        self.pilha, self.grupos, self.refs, self.n = [], {}, [], 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.pilha and "data-l" in a:
            self.grupos.setdefault(self.pilha[-1], []).append(a["data-l"])
        for chave in ("src", "href"):
            v = a.get(chave)
            if v and not v.startswith(("http://", "https://", "#", "mailto:")):
                self.refs.append(v)
        if tag in self.VAZIOS:
            return
        self.n += 1
        self.pilha.append(self.n)

    def handle_endtag(self, tag):
        if tag not in self.VAZIOS and self.pilha:
            self.pilha.pop()


def _texto(caminho):
    with open(caminho, encoding="utf-8") as fh:
        return fh.read()


def _coletar():
    c = _Coletor()
    c.feed(_texto(INDEX))
    return c


def test_todo_texto_existe_nos_tres_idiomas():
    grupos = _coletar().grupos
    assert grupos
    for langs in grupos.values():
        assert sorted(langs) == ["en", "fr", "pt"], langs


def test_referencias_locais_existem():
    for ref in _coletar().refs:
        assert os.path.exists(os.path.join(RAIZ, ref.split("?")[0])), ref


def test_todo_deck_publicado_aparece_nos_tres_idiomas():
    """Deck novo em aulas/ sem entrada no portal fica invisivel para a turma."""
    html = _texto(INDEX)
    decks = [os.path.relpath(p, RAIZ) for p in glob.glob(os.path.join(RAIZ, "aulas", "*.html"))
             if not os.path.basename(p).startswith("_")]
    assert decks
    for deck in decks:
        for lang in ("en", "pt", "fr"):
            assert 'href="%s?lang=%s"' % (deck, lang) in html, (deck, lang)


def test_calendario_bate_com_o_onboarding():
    html = _texto(INDEX)
    onb = _texto(ONBOARDING)
    reviews = re.findall(r'<td class="review">(\d{2}/\d{2})</td>', html)
    envios = re.findall(r'<td class="envio">(\d{2}/\d{2})</td>', html)
    assert len(reviews) == len(envios) == 5
    for data in reviews:
        assert '<span class="data-pill">%s/2026</span>' % data in onb, data
    for data in envios:
        assert 'data-l="en">Wed %s' % data in onb, data


def test_sem_travessao():
    assert "—" not in _texto(INDEX) and "&mdash;" not in _texto(INDEX)
