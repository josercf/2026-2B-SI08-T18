"""Testes do deck de Sprint Planning 2 e da coleta de metricas do GitLab (ADR-005).

Os testes genericos de deck (tres idiomas, travessao, referencias locais, rodape numerado,
dia da semana, layout em 1280x720) ja cobrem este deck via test_decks.py e test_index.py.
Aqui ficam a coerencia com os dados, a ausencia de nomes e de token e a resolucao de identidades.

Rodar a partir da raiz deste projeto:
    python3 -m pytest tools/tests/test_sprint_planning.py -v
"""
import csv
import json
import os
import re
import sys
import unicodedata

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "tools"))

import coletar_gitlab  # noqa: E402
import gerar_sprint_planning as gen  # noqa: E402

DECK = os.path.join(RAIZ, "aulas", "sprint-planning-2.html")
METRICAS = os.path.join(RAIZ, "dados", "metricas_sprint1.json")


def _html():
    with open(DECK, encoding="utf-8") as fh:
        return fh.read()


def _metricas():
    with open(METRICAS, encoding="utf-8") as fh:
        return json.load(fh)


def _norma(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", t)


# ------------------------------------------------------------------ coerencia dos dados
def test_deck_esta_atualizado_com_os_dados():
    """O HTML versionado e exatamente o que o gerador produz hoje: nada editado a mao."""
    assert _html() == gen.gerar()


def test_tabela_bate_com_o_json():
    html = _html()
    for g in _metricas()["grupos"]:
        linha = re.search(
            r'<th scope="row"><a href="#/%s">%s</a></th>\s*<td>(\d+)</td>\s*<td>(\d+)</td>\s*'
            r'<td>(\d+)</td>\s*<td>(\d+)</td>\s*<td>(\d+)/(\d+)</td>' % (g["grupo"].lower(), g["grupo"]),
            html)
        assert linha, g["grupo"]
        integrantes, commits, abertas, fechadas, revisados, criados = map(int, linha.groups())
        assert integrantes == g["integrantes"]
        assert commits == g["commits"] == sum(g["commits_por_integrante"]) + g["commits_de_nao_integrantes"]
        assert (abertas, fechadas) == (g["issues_abertas_na_sprint"], g["issues_fechadas_na_sprint"])
        assert (revisados, criados) == (g["mrs_com_revisao"], g["mrs_criados"])


def test_total_da_turma_e_a_soma_dos_grupos():
    gs = _metricas()["grupos"]
    total = re.search(r'<tr class="total">.*?</tr>', _html(), flags=re.S).group(0)
    assert ">%d<" % sum(g["commits"] for g in gs) in total
    assert ">%d<" % sum(g["issues_fechadas_na_sprint"] for g in gs) in total


def test_um_vetor_por_integrante_com_o_tamanho_do_grupo():
    for g in _metricas()["grupos"]:
        assert len(g["commits_por_integrante"]) == g["integrantes"]
        assert len(g["revisoes_por_integrante"]) == g["integrantes"]
        assert g["commits_por_integrante"] == sorted(g["commits_por_integrante"], reverse=True)
        assert g["integrantes_sem_commit"] == g["commits_por_integrante"].count(0)


def test_cada_grupo_tem_dois_slides_ancorados():
    html = _html()
    for g in _metricas()["grupos"]:
        nome = g["grupo"].lower()
        assert '<section class="content-slide" id="%s">' % nome in html
        assert '<section class="content-slide" id="%s-fluxo">' % nome in html


def test_todo_atalho_interno_aponta_para_um_slide():
    html = _html()
    ids = set(re.findall(r'<section[^>]* id="([^"]+)"', html))
    atalhos = set(re.findall(r'href="#/([^"]+)"', html))
    assert atalhos, "nenhum atalho interno"
    assert atalhos <= ids, atalhos - ids


# ------------------------------------------------------------------ privacidade e segredos
def _alunos():
    bruto = open(os.path.join(RAIZ, "dados", "grupos.js"), encoding="utf-8").read()
    grupos = json.loads(bruto[bruto.index("{"):bruto.rindex("}") + 1])
    return [a for lista in grupos.values() for a in lista]


def test_deck_e_metricas_nao_trazem_nome_de_aluno():
    for caminho in (DECK, METRICAS):
        texto = _norma(open(caminho, encoding="utf-8").read())
        for aluno in _alunos():
            assert _norma(aluno) not in texto, (os.path.basename(caminho), aluno)


def test_metricas_nao_trazem_email():
    assert "@" not in open(METRICAS, encoding="utf-8").read()


# Token de verdade tem 20+ caracteres depois do prefixo; o prefixo sozinho (em docs e testes) nao casa.
TOKEN = re.compile(r"glpat-[A-Za-z0-9_.-]{20,}")


def test_nenhum_token_gitlab_versionado():
    for base, pastas, arquivos in os.walk(RAIZ):
        pastas[:] = [p for p in pastas if p not in (".git", ".pytest_cache", "__pycache__")]
        for nome in arquivos:
            if nome.endswith((".png", ".svg", ".pyc")):
                continue
            with open(os.path.join(base, nome), encoding="utf-8", errors="ignore") as fh:
                assert not TOKEN.search(fh.read()), os.path.join(base, nome)


# ------------------------------------------------------------------ plano da sprint
def test_pesos_da_sprint_2_somam_20_e_cada_entrega_aparece_no_deck():
    with open(os.path.join(RAIZ, "dados", "atividades_ponderadas.csv"), encoding="utf-8") as fh:
        s2 = [a for a in csv.DictReader(fh) if a["sprint"] == "2"]
    assert sum(float(a["peso"]) for a in s2) == 20.0
    html = _html()
    for a in s2:
        assert a["nome"] in html, a["nome"]


def test_dias_de_execucao_descontam_feriado_planning_e_review():
    """26/10 a 06/11 tem 10 dias uteis; 02/11 e feriado; planning e review nao executam."""
    assert gen.DIAS_DE_EXECUCAO == 10 - 1 - 2


def test_arguicoes_terminam_na_quinta_29_10():
    import datetime
    assert datetime.date(2026, 10, 29).weekday() == 3
    assert "29/10" in _html()


# ------------------------------------------------------------------ coletor
ALUNOS = ["Guilherme Hassenpflug", "Henri Charles Hans Alain Hager", "Paulo Vitor Barros de Almeida",
          "Giovanna Neves Rodrigues", "Lívia de Souza Negrini"]


@pytest.mark.parametrize("pistas,esperado", [
    (("Henri", "henri.hager@sou.inteli.edu.br"), 1),
    (("pvitoralmeida", "paulo.almeida@sou.inteli.edu.br"), 2),
    (("Livia Negrini", "livia.negrini@sou.inteli.edu.br"), 4),
    (("guihassen", "gui_steam@yahoo.com"), 0),      # alias de conta pessoal
    (("Jose Romualdo da Costa Filho", "jose.romualdo@prof.inteli.edu.br"), None),  # docente
    (("project_1_bot_abc", "project_1_bot_abc"), None),
])
def test_resolver_casa_autor_com_aluno(pistas, esperado):
    assert coletar_gitlab.resolver(ALUNOS, *pistas) == esperado


def test_resolver_devolve_none_em_empate():
    assert coletar_gitlab.resolver(["Maria Lima", "Maria Souza"], "Maria") is None


def test_mediana_em_dias():
    assert coletar_gitlab.mediana_dias([]) is None
    assert coletar_gitlab.mediana_dias([86400, 3 * 86400, 10 * 86400]) == 3.0


def test_coletor_exige_token_no_ambiente(monkeypatch, capsys):
    monkeypatch.delenv("GITLAB_TOKEN", raising=False)
    monkeypatch.setattr(sys, "argv", ["x", "--sprint", "1", "--inicio", "2026-10-14", "--fim", "2026-10-23"])
    with pytest.raises(SystemExit) as e:
        coletar_gitlab.main()
    assert "GITLAB_TOKEN" in str(e.value)


def test_top_metade_arredonda_para_cima():
    g = {"commits": 100, "commits_por_integrante": [50, 30, 20]}
    assert gen.top_metade(g) == (2, 80)
