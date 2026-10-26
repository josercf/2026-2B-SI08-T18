#!/usr/bin/env python3
"""Coleta as métricas de GitLab de uma sprint por grupo e grava dados/metricas_sprintN.json.

Uso:
    GITLAB_TOKEN=... python3 tools/coletar_gitlab.py --sprint 1 --inicio 2026-10-14 --fim 2026-10-23

O token (escopo read_api) vem só do ambiente e nunca é gravado. A saída agrega por grupo e
não contém nome nem e-mail de aluno: a distribuição de commits e de revisões por integrante
sai como lista numérica ordenada, sem identificação (ver ADR-005).
"""
import argparse
import json
import os
import re
import statistics
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = "https://git.inteli.edu.br/api/v4"
GRUPOS = {"G01": 50209, "G02": 50214, "G03": 50216, "G04": 50218, "G05": 50220}
FUSO = timezone(timedelta(hours=-3))
RAIZ = Path(__file__).resolve().parent.parent
# Contas pessoais que não casam com o nome no GitLab: e-mail ou usuário -> nome completo do aluno.
ALIASES = {"gui_steam@yahoo.com": "Guilherme Hassenpflug"}


def get(caminho, token, **params):
    """GET paginado: devolve a lista completa de uma coleção."""
    itens, pagina = [], 1
    while True:
        qs = urllib.parse.urlencode({**params, "per_page": 100, "page": pagina})
        req = urllib.request.Request(f"{BASE}{caminho}?{qs}", headers={"PRIVATE-TOKEN": token})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                corpo = json.load(r)
                proxima = r.headers.get("X-Next-Page")
        except urllib.error.HTTPError as e:
            sys.exit(f"HTTP {e.code} em {caminho}: {e.read()[:200]!r}")
        if not isinstance(corpo, list):
            return corpo
        itens += corpo
        if not proxima:
            return itens
        pagina = int(proxima)


def _norma(texto):
    t = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", t)


def carregar_alunos():
    """Alunos por grupo, a partir de dados/grupos.js (gerado do export da Adalove)."""
    bruto = (RAIZ / "dados" / "grupos.js").read_text(encoding="utf-8")
    return json.loads(bruto[bruto.index("{"):bruto.rindex("}") + 1])


def resolver(alunos, *pistas):
    """Índice do aluno cujo nome melhor casa com as pistas (nome, usuário, e-mail), ou None.

    Casa por tokens do nome completo (4+ letras) contidos nas pistas. Empate ou nenhum
    casamento devolve None, e quem chama conta a identidade como não mapeada.
    """
    pistas = pistas + tuple(ALIASES[p.lower()] for p in pistas if p and p.lower() in ALIASES)
    alvo = "".join(_norma(p.split("@")[0] if "@" in (p or "") else p) for p in pistas)
    melhores, nota = [], 0
    for i, nome in enumerate(alunos):
        tokens = [_norma(t) for t in re.split(r"[\s\-–]+", nome)]
        pontos = sum(1 for t in tokens if len(t) >= 4 and t in alvo)
        if pontos > nota:
            melhores, nota = [i], pontos
        elif pontos == nota and pontos:
            melhores.append(i)
    return melhores[0] if len(melhores) == 1 else None


def dt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def mediana_dias(deltas):
    return round(statistics.median(deltas) / 86400, 1) if deltas else None


def coletar_projeto(pid, ini, fim, token):
    janela = {"created_after": ini.isoformat(), "created_before": fim.isoformat()}
    commits = get(f"/projects/{pid}/repository/commits", token, all="true",
                  since=ini.isoformat(), until=fim.isoformat())
    # Commits de merge não medem contribuição individual.
    commits = [c for c in commits if len(c.get("parent_ids", [])) < 2]
    autores = [(c.get("author_name") or "", c.get("author_email") or "") for c in commits]

    issues = get(f"/projects/{pid}/issues", token, scope="all", **janela)
    todas = get(f"/projects/{pid}/issues", token, scope="all", state="opened")
    fechadas_na_janela = [
        i for i in get(f"/projects/{pid}/issues", token, scope="all", state="closed")
        if i.get("closed_at") and ini <= dt(i["closed_at"]) <= fim
    ]
    lead_issue = [(dt(i["closed_at"]) - dt(i["created_at"])).total_seconds() for i in fechadas_na_janela]

    mrs = get(f"/projects/{pid}/merge_requests", token, scope="all", **janela)
    mrs_merged = [m for m in mrs if m.get("merged_at")]
    lead_mr = [(dt(m["merged_at"]) - dt(m["created_at"])).total_seconds() for m in mrs_merged]
    revisores = []
    mrs_revisados = 0
    for m in mrs:
        notas = get(f"/projects/{pid}/merge_requests/{m['iid']}/notes", token)
        de_outros = [n for n in notas if not n.get("system")
                     and n["author"]["id"] != m["author"]["id"]
                     and ini <= dt(n["created_at"]) <= fim]
        if de_outros:
            mrs_revisados += 1
        revisores += [(n["author"]["name"], n["author"]["username"]) for n in de_outros]
    return {
        "autores": autores,
        "commits": len(commits),
        "issues_abertas_na_sprint": len(issues),
        "issues_fechadas_na_sprint": len(fechadas_na_janela),
        "issues_abertas_agora": len(todas),
        "lead_time_issue": lead_issue,
        "mrs_criados": len(mrs),
        "mrs_merged": len(mrs_merged),
        "lead_time_mr": lead_mr,
        "mrs_com_revisao": mrs_revisados,
        "revisores": revisores,
    }


def agregar_grupo(nome, gid, alunos, ini, fim, token):
    projetos = get(f"/groups/{gid}/projects", token, include_subgroups="true")
    agg = {"autores": [], "revisores": [], "lead_time_issue": [], "lead_time_mr": []}
    soma = dict.fromkeys(["commits", "issues_abertas_na_sprint", "issues_fechadas_na_sprint",
                          "issues_abertas_agora", "mrs_criados", "mrs_merged", "mrs_com_revisao"], 0)
    for p in projetos:
        r = coletar_projeto(p["id"], ini, fim, token)
        for k in soma:
            soma[k] += r[k]
        agg["autores"] += r["autores"]
        agg["revisores"] += r["revisores"]
        agg["lead_time_issue"] += r["lead_time_issue"]
        agg["lead_time_mr"] += r["lead_time_mr"]
    commits = [0] * len(alunos)
    revisoes = [0] * len(alunos)
    sem_mapa = {"commits": 0, "revisoes": 0}
    for pistas in agg["autores"]:
        i = resolver(alunos, *pistas)
        if i is None:
            sem_mapa["commits"] += 1
            print(f"  [{nome}] commit sem aluno: {pistas}", file=sys.stderr)
        else:
            commits[i] += 1
    for pistas in agg["revisores"]:
        i = resolver(alunos, *pistas)
        if i is None:
            sem_mapa["revisoes"] += 1
        else:
            revisoes[i] += 1
    commits_ord = sorted(commits, reverse=True)
    revisoes_ord = sorted(revisoes, reverse=True)
    return {
        "grupo": nome,
        "projetos": len(projetos),
        **soma,
        "integrantes": len(alunos),
        "integrantes_sem_commit": commits.count(0),
        "commits_de_nao_integrantes": sem_mapa["commits"],
        "revisoes_de_nao_integrantes": sem_mapa["revisoes"],
        "commits_por_integrante": commits_ord,
        "revisoes_por_integrante": revisoes_ord,
        "lead_time_issue_dias_mediana": mediana_dias(agg["lead_time_issue"]),
        "lead_time_mr_dias_mediana": mediana_dias(agg["lead_time_mr"]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sprint", type=int, required=True)
    ap.add_argument("--inicio", required=True, help="AAAA-MM-DD")
    ap.add_argument("--fim", required=True, help="AAAA-MM-DD, inclusive")
    a = ap.parse_args()
    token = os.environ.get("GITLAB_TOKEN")
    if not token:
        sys.exit("Defina GITLAB_TOKEN no ambiente.")
    ini = datetime.fromisoformat(a.inicio).replace(tzinfo=FUSO)
    fim = datetime.fromisoformat(a.fim).replace(tzinfo=FUSO) + timedelta(days=1) - timedelta(seconds=1)
    alunos = carregar_alunos()
    saida = {"sprint": a.sprint, "inicio": a.inicio, "fim": a.fim,
             "grupos": [agregar_grupo(n, g, alunos[n], ini, fim, token) for n, g in GRUPOS.items()]}
    destino = RAIZ / "dados" / f"metricas_sprint{a.sprint}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"gravado {destino}")


if __name__ == "__main__":
    main()
