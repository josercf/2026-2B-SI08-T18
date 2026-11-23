#!/usr/bin/env python3
"""Agrega as notas das ponderadas por grupo, sem nomes, e grava dados/notas_sprints.json.

Entradas:
    export da turma na Adalove ("Turma (N).xlsx", fora do git)   notas individuais
    dados/notas_grupo_adalove.json                               nota de grupo dos artefatos (API)
    dados/atividades_ponderadas.csv                              pesos e sprints

Uso:
    python3 tools/extrair_notas.py "~/Downloads/Turma.xlsx" [--coletado-em 2026-11-17]

Saida (ADR-007): nenhum nome, e-mail ou nota identificada por aluno. Por artefato de projeto,
a nota do grupo e a lista ordenada da razao nota individual / nota do grupo. Por autoestudo,
a media da turma, a media de cada grupo e a contagem de notas zero da turma.
"""
import argparse
import csv
import json
import os
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
GRUPOS = ["G01", "G02", "G03", "G04", "G05"]


def _nota(valor):
    if valor in (None, ""):
        return None
    return float(str(valor).replace(",", "."))


def ler_export(caminho):
    import openpyxl
    wb = openpyxl.load_workbook(os.path.expanduser(caminho), read_only=True)
    linhas = list(wb.active.iter_rows(values_only=True))
    cab = linhas[0]
    return [dict(zip(cab, r)) for r in linhas[1:]]


def notas_individuais(linhas):
    """{atividade: {grupo: [notas]}} so de alunos ativos, atividades com peso e nota lancada."""
    out = {}
    vistos = set()
    for r in linhas:
        if r.get("Aluno_Ativo_Na_Turma") != "Sim" or not float(r.get("Atividade_Peso") or 0):
            continue
        nota = _nota(r.get("Atividade_Nota"))
        if nota is None:
            continue
        chave = (r["Aluno_Nome"], r["Atividade_Nome"])
        if chave in vistos:
            continue
        vistos.add(chave)
        out.setdefault(r["Atividade_Nome"], {}).setdefault(r["Grupo_Nome"], []).append(nota)
    return out


def media(valores):
    return round(statistics.mean(valores), 2) if valores else None


def agregar(individuais, grupo_api, ativ):
    projeto, autoestudo, pendentes = [], [], []
    for a in ativ:
        nome, sprint, peso, tipo = a["nome"], int(a["sprint"]), float(a["peso"]), a["tipo"]
        if sprint > 3:
            continue
        por_grupo = individuais.get(nome, {})
        if nome in grupo_api:
            notas_g = grupo_api[nome]
            if all(v is None for v in notas_g.values()):
                pendentes.append({"nome": nome, "sprint": sprint, "peso": peso, "tipo": tipo})
                continue
            grupos = {}
            for g in GRUPOS:
                ng = notas_g[g]
                ind = por_grupo.get(g, [])
                fatores = sorted((round(n / ng, 2) for n in ind), reverse=True) if ng else []
                grupos[g] = {"nota_grupo": ng, "media_individual": media(ind), "fatores": fatores}
            projeto.append({"nome": nome, "sprint": sprint, "peso": peso, "grupos": grupos})
        elif tipo == "Autoestudo":
            todas = [n for g in GRUPOS for n in por_grupo.get(g, [])]
            if not todas:
                pendentes.append({"nome": nome, "sprint": sprint, "peso": peso, "tipo": tipo})
                continue
            autoestudo.append({
                "nome": nome, "sprint": sprint, "peso": peso,
                "media_turma": media(todas), "notas": len(todas),
                "zeros": sum(1 for n in todas if n == 0),
                "abaixo_de_6": sum(1 for n in todas if n < 6),
                "grupos": {g: media(por_grupo.get(g, [])) for g in GRUPOS},
            })
    return projeto, autoestudo, pendentes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export")
    ap.add_argument("--coletado-em", default=None, help="data do export, AAAA-MM-DD")
    a = ap.parse_args()
    api = json.loads((RAIZ / "dados" / "notas_grupo_adalove.json").read_text(encoding="utf-8"))
    with open(RAIZ / "dados" / "atividades_ponderadas.csv", encoding="utf-8") as fh:
        ativ = list(csv.DictReader(fh))
    projeto, autoestudo, pendentes = agregar(notas_individuais(ler_export(a.export)),
                                             api["artefatos"], ativ)
    saida = {
        "export_individual_em": a.coletado_em,
        "api_grupo_em": api["coletado_em"],
        "projeto": projeto,
        "autoestudo": autoestudo,
        "pendentes": pendentes,
    }
    destino = RAIZ / "dados" / "notas_sprints.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"gravado {destino}: {len(projeto)} artefatos, {len(autoestudo)} autoestudos, "
          f"{len(pendentes)} pendentes", file=sys.stderr)


if __name__ == "__main__":
    main()
