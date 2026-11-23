"""Testes do deck de Sprint Planning 4 e da agregacao de notas (ADR-007).

Os testes genericos (tres idiomas, referencias locais, rodape, layout) ficam em test_decks.py.

Rodar a partir da raiz deste projeto:
    python3 -m pytest tools/tests/test_sprint_planning_4.py -v
"""
import csv
import json
import os
import re
import statistics
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "tools"))

import extrair_notas as ext  # noqa: E402
import gerar_sprint_planning_4 as gen  # noqa: E402

DECK = os.path.join(RAIZ, "aulas", "sprint-planning-4.html")
NOTAS = os.path.join(RAIZ, "dados", "notas_sprints.json")
API = os.path.join(RAIZ, "dados", "notas_grupo_adalove.json")


def _ler(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def _notas():
    return json.loads(_ler(NOTAS))


def _alunos():
    bruto = _ler(os.path.join(RAIZ, "dados", "grupos.js"))
    return json.loads(bruto[bruto.index("{"):bruto.rindex("}") + 1])


# ------------------------------------------------------------------ deck
def test_deck_esta_atualizado_com_o_gerador():
    assert _ler(DECK) == gen.gerar()


def test_nota_de_grupo_do_deck_bate_com_a_api():
    api = json.loads(_ler(API))["artefatos"]
    for p in _notas()["projeto"]:
        assert {g: v["nota_grupo"] for g, v in p["grupos"].items()} == api[p["nome"]]


def test_artefato_sem_nota_publicada_fica_pendente_e_fora_da_tabela():
    n = _notas()
    pendentes = {p["nome"] for p in n["pendentes"]}
    assert "Automated Data Cube" in pendentes
    assert "Automated Data Cube" not in {p["nome"] for p in n["projeto"]}


def test_media_da_turma_no_slide_de_artefatos():
    html = gen.artefatos(1, _notas())
    for p in _notas()["projeto"]:
        m = statistics.mean(p["grupos"][g]["nota_grupo"] for g in gen.GRUPOS)
        assert f"{m:.2f}".replace(".", ",") in html


def test_fator_tem_um_valor_por_integrante_do_grupo():
    alunos = _alunos()
    for sprint, grupos in gen.fatores_por_sprint(_notas()).items():
        for g, fatores in grupos.items():
            assert len(fatores) == len(alunos[g]), (sprint, g)
            assert fatores == sorted(fatores, reverse=True)
            assert all(0 <= f <= 1 for f in fatores)


def test_entregas_da_sprint_4_somam_31_e_aparecem_no_deck():
    with open(os.path.join(RAIZ, "dados", "atividades_ponderadas.csv"), encoding="utf-8") as fh:
        s4 = [a for a in csv.DictReader(fh) if a["sprint"] == "4"]
    assert sum(float(a["peso"]) for a in s4) == 31.0
    deck = _ler(DECK)
    for a in s4:
        assert a["nome"] in deck


def test_sem_metricas_do_gitlab_a_parte_a_some(monkeypatch):
    notas, _, _, ativ, trad = gen.carregar()
    monkeypatch.setattr(gen, "carregar", lambda: (notas, None, None, ativ, trad))
    html = gen.gerar()
    assert "Sprint 3 no GitLab" not in html
    assert 'id="tabela"' not in html


def test_com_metricas_do_gitlab_a_parte_a_tem_um_slide_por_grupo(monkeypatch):
    m1 = json.loads(_ler(os.path.join(RAIZ, "dados", "metricas_sprint1.json")))
    m3 = {**m1, "sprint": 3, "inicio": "2026-11-09", "fim": "2026-11-19"}
    notas, _, _, ativ, trad = gen.carregar()
    monkeypatch.setattr(gen, "carregar", lambda: (notas, m3, m1, ativ, trad))
    html = gen.gerar()
    for g in gen.GRUPOS:
        assert f'id="{g.lower()}"' in html
        assert f'href="#/{g.lower()}"' in html
    assert "de 09/11 a 19/11" in html


def test_horario_da_apresentacao_entra_no_titulo(monkeypatch):
    monkeypatch.setattr(gen, "HORARIO_APRESENTACAO", "17h")
    assert "hoje às 17h" in gen.apresentacao_planning(1)


# ------------------------------------------------------------------ privacidade
def test_deck_e_dados_nao_trazem_nome_de_aluno():
    nomes = [n for g in _alunos().values() for n in g]
    textos = [_ler(DECK), _ler(NOTAS), _ler(API)]
    for nome in nomes:
        for t in textos:
            assert nome not in t


def test_dados_versionados_nao_trazem_feedback():
    assert "activityFeedback" not in _ler(API)
    assert "feedback" not in _ler(NOTAS).lower()


# ------------------------------------------------------------------ extracao
def _linha(aluno, grupo, atividade, nota, peso="4", ativo="Sim"):
    return {"Aluno_Nome": aluno, "Aluno_Ativo_Na_Turma": ativo, "Grupo_Nome": grupo,
            "Atividade_Nome": atividade, "Atividade_Peso": peso, "Atividade_Nota": nota}


def test_notas_individuais_ignora_inativo_peso_zero_sem_nota_e_duplicata():
    linhas = [
        _linha("A", "G01", "X", "8"),
        _linha("A", "G01", "X", "8"),          # duplicata
        _linha("B", "G01", "X", "7,5"),        # virgula decimal
        _linha("C", "G01", "X", "9", ativo="Não"),
        _linha("D", "G01", "X", "", ),         # sem nota
        _linha("E", "G01", "Y", "9", peso="0"),
    ]
    assert ext.notas_individuais(linhas) == {"X": {"G01": [8.0, 7.5]}}


def test_agregar_calcula_fator_e_separa_pendentes():
    ativ = [
        {"nome": "Art", "sprint": "2", "peso": "6", "tipo": "Desenvolvimento de Projeto"},
        {"nome": "Auto", "sprint": "2", "peso": "3", "tipo": "Autoestudo"},
        {"nome": "Cubo", "sprint": "3", "peso": "7", "tipo": "Desenvolvimento de Projeto"},
        {"nome": "Futuro", "sprint": "4", "peso": "4", "tipo": "Autoestudo"},
    ]
    api = {"Art": {g: 8.0 for g in ext.GRUPOS}, "Cubo": {g: None for g in ext.GRUPOS}}
    ind = {"Art": {"G01": [8.0, 4.0, 0.0]}, "Auto": {"G01": [10.0, 0.0], "G02": [5.0]}}
    projeto, auto, pend = ext.agregar(ind, api, ativ)
    assert projeto[0]["grupos"]["G01"]["fatores"] == [1.0, 0.5, 0.0]
    assert auto[0]["media_turma"] == 5.0 and auto[0]["zeros"] == 1 and auto[0]["abaixo_de_6"] == 2
    assert [p["nome"] for p in pend] == ["Cubo"]


@pytest.mark.parametrize("arquivo", ["tools/gerar_sprint_planning_4.py", "tools/extrair_notas.py"])
def test_sem_travessao_nos_scripts(arquivo):
    assert "—" not in _ler(os.path.join(RAIZ, arquivo))


def test_titulos_sem_formato_de_listicle():
    titulos = re.findall(r'<span data-l="pt">([^<]+)</span>', gen.gerar())
    for t in titulos:
        assert not re.match(r"^(As|Os) (duas|dois|três|quatro|cinco|seis|sete) ", t), t
