#!/usr/bin/env python3
"""
Extrai do export da turma no Adalove ("Turma (N).xlsx") as duas coisas que o
deck de orientacao usa:

1. dados/atividades_ponderadas.csv: toda atividade com peso > 0 (sem nenhum
   dado de aluno). Versionado: e a fonte do slide de entregas por sprint.
2. dados/grupos.js: nomes dos alunos por grupo, versionado e publicado no
   Pages (publicacao autorizada pelo orientador em 14/10/2026). Sem esse
   arquivo, o deck remove o slide de grupos.

Uso:
    python3 tools/extrair_lbl.py "~/Downloads/Turma (6).xlsx"
"""
import csv
import datetime
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INICIO_SEMANA_01 = datetime.date(2026, 10, 12)  # segunda-feira da Semana 01


def sexta_da_semana(rotulo):
    """'Semana 04' -> 06/11/2026, a sexta-feira daquela semana do modulo."""
    n = int(rotulo.split()[-1])
    return INICIO_SEMANA_01 + datetime.timedelta(weeks=n - 1, days=4)


def sprint_da_semana(rotulo):
    """Sprints de duas semanas: semanas 1-2 -> 1, 3-4 -> 2 ... 9-10 -> 5."""
    return (int(rotulo.split()[-1]) + 1) // 2


def ponderadas(linhas):
    """Atividades unicas com peso > 0, ordenadas por semana e nome."""
    vistas = {}
    for r in linhas:
        peso = float(r["Atividade_Peso"] or 0)
        if peso <= 0:
            continue
        chave = (r["Atividade_Semana"], r["Atividade_Nome"])
        vistas.setdefault(chave, {
            "semana": r["Atividade_Semana"],
            "sprint": sprint_da_semana(r["Atividade_Semana"]),
            "tipo": r["Atividade_Tipo"],
            "nome": r["Atividade_Nome"].strip(),
            "peso": peso,
            "professor": r["Atividade_Professor_Nome"] or "",
            "data": r["Atividade_Data_Inicio"] or sexta_da_semana(r["Atividade_Semana"]).strftime("%d/%m/%Y"),
        })
    return sorted(vistas.values(), key=lambda a: (a["semana"], a["nome"]))


def grupos(linhas):
    """{'G01': [nomes em ordem alfabetica], ...}, so alunos ativos."""
    out = {}
    for r in linhas:
        if r["Aluno_Ativo_Na_Turma"] != "Sim":
            continue
        out.setdefault(r["Grupo_Nome"], set()).add(r["Aluno_Nome"].strip())
    return {g: sorted(n) for g, n in sorted(out.items())}


def ler_xlsx(caminho):
    import openpyxl
    wb = openpyxl.load_workbook(caminho, read_only=True, data_only=True)
    ws = wb.active
    it = ws.iter_rows(values_only=True)
    cab = next(it)
    return [dict(zip(cab, r)) for r in it]


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    linhas = ler_xlsx(os.path.expanduser(sys.argv[1]))
    os.makedirs(os.path.join(RAIZ, "dados"), exist_ok=True)

    ativ = ponderadas(linhas)
    with open(os.path.join(RAIZ, "dados", "atividades_ponderadas.csv"), "w",
              newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ativ[0]))
        w.writeheader()
        w.writerows(ativ)

    g = grupos(linhas)
    with open(os.path.join(RAIZ, "dados", "grupos.js"), "w", encoding="utf-8") as fh:
        fh.write("// Gerado por tools/extrair_lbl.py a partir do export da turma no Adalove.\n")
        fh.write("window.SI08_GRUPOS = %s;\n" % json.dumps(g, ensure_ascii=False, indent=2))

    print("%d atividades ponderadas, soma dos pesos = %.0f" % (len(ativ), sum(a["peso"] for a in ativ)))
    print("%d grupos, %d alunos" % (len(g), sum(len(v) for v in g.values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
