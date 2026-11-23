#!/usr/bin/env python3
"""Gera aulas/sprint-planning-4.html (Sprint Planning 4, 23/11/2026).

Deck curto: numeros da Sprint 3 e das ponderadas publicadas, calendario e entregas da
Sprint 4. O planejamento nao acontece em sala; cada grupo apresenta a planning ao final do dia.

Entradas:
    dados/notas_sprints.json           (tools/extrair_notas.py, ADR-007)
    dados/metricas_sprint3.json        (tools/coletar_gitlab.py, opcional: sem ele a Parte A some)
    dados/metricas_sprint2.json        (opcional: comparacao com a Sprint 2)
    dados/atividades_ponderadas.csv, dados/traducoes_atividades.csv

Uso:
    python3 tools/gerar_sprint_planning_4.py
"""
import json
import math
import statistics
from pathlib import Path

import gerar_sprint_planning as base
from gerar_sprint_planning import (L, LEGENDA, barras, cab, dia, evento, evento_nome, indicador,
                                   nota, num, pct, secao, slide_conteudo)

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "aulas" / "sprint-planning-4.html"
RODAPE = "SI08 &middot; T18 &middot; Sprint Planning 4"
GRUPOS = ["G01", "G02", "G03", "G04", "G05"]
# Horario em que cada grupo apresenta a planning. None: o deck diz "ao final do dia".
HORARIO_APRESENTACAO = None

CURTO = {
    "Data Discovery with Data Model Canvas": ("Data Model Canvas", "Data Model Canvas", "Data Model Canvas"),
    "Market and Risk Analysis Workbook": ("Market and Risk", "Mercado e riscos", "Marché et risques"),
    "Data Ingestion Structure": ("Data Ingestion", "Ingestão de dados", "Ingestion des données"),
    "Information Architecture Specification and Decision Matrix (MAI-MD)": ("MAI-MD", "MAI-MD", "MAI-MD"),
    "Architecture Activity": ("Architecture Activity", "Atividade de arquitetura", "Activité d'architecture"),
    "Graded Assignment: Hierarchical Classification and Outcomes Matrix":
        ("Hierarchical Classification", "Classificação hierárquica", "Classification hiérarchique"),
    "Business Question 1": ("Business Question 1", "Questão de negócio 1", "Question métier 1"),
    "Math Challenge 1": ("Math Challenge 1", "Desafio de matemática 1", "Défi de mathématiques 1"),
    "Graded Activity: Who Decides What? Group Power and Decision Mapping":
        ("Who Decides What?", "Quem decide o quê?", "Qui décide quoi ?"),
    "Automated Data Cube": ("Automated Data Cube", "Cubo de dados automatizado", "Cube de données automatisé"),
}


# ------------------------------------------------------------------ dados
def _json(nome):
    p = RAIZ / "dados" / nome
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def carregar():
    _, ativ, trad, _ = base.carregar()
    return _json("notas_sprints.json"), _json("metricas_sprint3.json"), _json("metricas_sprint2.json"), ativ, trad


def N(valor, casas=1):
    en, pt, fr = num(valor, casas)
    return f'<span data-l="en">{en}</span><span data-l="pt">{pt}</span><span data-l="fr">{fr}</span>'


def C(nome):
    return L(*CURTO[nome])


def fatores_por_sprint(notas):
    """{sprint: {grupo: [fator medio de cada integrante]}} a partir dos artefatos de projeto.

    O fator individual e o mesmo nos artefatos da mesma sprint; a media protege contra
    arredondamento diferente entre eles.
    """
    out = {}
    for sprint in sorted({p["sprint"] for p in notas["projeto"]}):
        arts = [p for p in notas["projeto"] if p["sprint"] == sprint]
        out[sprint] = {}
        for g in GRUPOS:
            listas = [p["grupos"][g]["fatores"] for p in arts]
            out[sprint][g] = [round(statistics.mean(v), 2) for v in zip(*listas)]
    return out


def media_fator(valores):
    return round(statistics.mean(valores), 2)


# ------------------------------------------------------------------ slides
def capa():
    return f"""      <!-- 1 - Capa -->
      <section class="cover-slide">
        <div class="cover-panel">
          <div class="cover-content">
            <div class="cover-brand-mark">
              <img src="../assets/img/inteli-logo-negativa.svg" alt="Inteli">
            </div>
            <p class="cover-eyebrow">
              <span data-l="en">Information Systems &middot; Module 08 &middot; Class T18 &middot; 2026-2B</span>
              <span data-l="pt">Sistemas de Informação &middot; Módulo 08 &middot; Turma T18 &middot; 2026-2B</span>
              <span data-l="fr">Systèmes d'information &middot; Module 08 &middot; Classe T18 &middot; 2026-2B</span>
            </p>
            <div class="cover-accent"></div>
            <h1>
              {L("Sprint Planning 4", "Sprint Planning 4", "Sprint Planning 4")}
            </h1>
            <h3>
              {L("Sprint 3 in numbers and Sprint 4 deliveries", "Sprint 3 em números e entregas da Sprint 4",
                 "Le sprint 3 en chiffres et les livrables du sprint 4")}
            </h3>
          </div>
        </div>
      </section>
"""


def agenda(n, com_gitlab):
    itens = []
    if com_gitlab:
        itens.append(("Sprint 3 in GitLab, by group", "Sprint 3 no GitLab, por grupo", "Le sprint 3 dans GitLab, par groupe"))
    itens += [
        ("Published grades of the graded deliveries", "Notas publicadas das ponderadas", "Notes publiées des livrables notés"),
        ("Sprint 4 calendar and deliveries", "Calendário e entregas da Sprint 4", "Calendrier et livrables du sprint 4"),
        ("Planning presented by each group at the end of the day", "Planning apresentada por cada grupo ao final do dia",
         "Planning présenté par chaque groupe en fin de journée"),
    ]
    lis = "\n".join(f"          <li>\n            {L(*i)}\n          </li>" for i in itens)
    return f"""      <!-- {n} - Agenda -->
      <section class="content-slide agenda-slide">
        <div class="top-bar"></div>
        <img class="inteli-logo-header" src="../assets/img/inteli-logo-negativa.svg" alt="Inteli">
        <div class="slide-title-area">
          <div class="accent-bar"></div>
          <h2>
            {L("Agenda", "Agenda", "Ordre du jour")}
          </h2>
        </div>
        <ol class="agenda-list">
{lis}
        </ol>
        <div class="slide-footer">
          <p class="footer-bar">{RODAPE}</p>
          <p class="footer-page">{n}</p>
        </div>
      </section>
"""


# ---------- Parte A: GitLab
def _periodo(m):
    i = m["inicio"][8:10] + "/" + m["inicio"][5:7]
    f = m["fim"][8:10] + "/" + m["fim"][5:7]
    return i, f


def numeros_gitlab(n, m3, m2):
    t = base.totais(m3["grupos"])
    i, f = _periodo(m3)
    titulo = L(
        f"Sprint 3: {t['commits']} commits and {t['mrs_merged']} merge requests merged across the five groups",
        f"Sprint 3: {t['commits']} commits e {t['mrs_merged']} merge requests integrados nos cinco grupos",
        f"Sprint 3 : {t['commits']} commits et {t['mrs_merged']} merge requests intégrés dans les cinq groupes")

    def bloco(valor, rot, antes=None, cls=""):
        comp = ""
        if antes is not None:
            comp = (f'<p class="rotulo">{L(f"Sprint 2: {antes}", f"Sprint 2: {antes}", f"Sprint 2 : {antes}")}</p>')
        return (f'<div class="numero {cls}"><p class="valor">{valor}</p>'
                f'<p class="rotulo">{L(*rot)}</p>{comp}</div>')

    t2 = base.totais(m2["grupos"]) if m2 else {}
    corpo = f"""        <div class="numeros-grandes">
          {bloco(t['commits'], ("commits", "commits", "commits"), t2.get('commits'))}
          {bloco(t['issues_abertas_na_sprint'], ("issues opened", "issues abertas", "issues ouvertes"), t2.get('issues_abertas_na_sprint'), "verde")}
          {bloco(t['issues_fechadas_na_sprint'], ("issues closed", "issues fechadas", "issues fermées"), t2.get('issues_fechadas_na_sprint'), "verde")}
          {bloco(t['mrs_criados'], ("merge requests created", "merge requests criados", "merge requests créés"), t2.get('mrs_criados'))}
          {bloco(t['mrs_merged'], ("merge requests merged", "merge requests integrados", "merge requests intégrés"), t2.get('mrs_merged'), "destaque")}
          {bloco(t['mrs_com_revisao'], ("MRs with a comment from another member", "MRs com comentário de outro integrante", "MR avec un commentaire d'un autre membre"), t2.get('mrs_com_revisao'), "destaque")}
        </div>
{nota(f"Source: GitLab (git.inteli.edu.br), {i} to {f}. Commits exclude merge commits.",
      f"Fonte: GitLab (git.inteli.edu.br), de {i} a {f}. Commits sem commits de merge.",
      f"Source : GitLab (git.inteli.edu.br), du {i} au {f}. Commits hors commits de merge.")}"""
    return slide_conteudo(n, titulo, corpo)


def tabela_gitlab(n, m3):
    gs = m3["grupos"]
    rev = {g["grupo"]: round(100 * g["mrs_com_revisao"] / g["mrs_criados"]) if g["mrs_criados"] else 0 for g in gs}
    lo, hi = min(rev.values()), max(rev.values())
    titulo = L(f"The share of reviewed merge requests ranges from {lo}% to {hi}% across groups",
               f"A parcela de merge requests revisados varia de {lo}% a {hi}% entre os grupos",
               f"La part de merge requests relus varie de {lo} % à {hi} % selon les groupes")
    linhas = []
    for g in gs:
        lt = g["lead_time_issue_dias_mediana"]
        linhas.append(f"""            <tr>
              <th scope="row"><a href="#/{g['grupo'].lower()}">{g['grupo']}</a></th>
              <td>{g['integrantes']}</td>
              <td>{g['commits']}</td>
              <td>{g['issues_fechadas_na_sprint']}/{g['issues_abertas_na_sprint']}</td>
              <td>{g['mrs_com_revisao']}/{g['mrs_criados']}</td>
              <td>{rev[g['grupo']]}%</td>
              <td>{N(lt) if lt is not None else '&ndash;'}</td>
            </tr>""")
    corpo = f"""        <table class="grupos-tabela">
          <thead>
            <tr>
              <th>{L("Group", "Grupo", "Groupe")}</th>
              <th>{L("Members", "Integrantes", "Membres")}</th>
              <th>Commits</th>
              <th>{L("Issues closed / opened", "Issues fechadas / abertas", "Issues fermées / ouvertes")}</th>
              <th>{L("MRs reviewed / created", "MRs revisados / criados", "MR relus / créés")}</th>
              <th>{L("Reviewed", "Revisados", "Relus")}</th>
              <th>{L("Issue lead time (days)", "Lead time de issue (dias)", "Lead time issue (jours)")}</th>
            </tr>
          </thead>
          <tbody>
{chr(10).join(linhas)}
          </tbody>
        </table>
{nota("MR reviewed: has a comment from a member other than the author. Median lead time. Click a group to open its slide.",
      "MR revisado: tem comentário de integrante diferente do autor. Lead time mediano. Clicar no grupo abre o slide dele.",
      "MR relu : comporte un commentaire d'un membre autre que l'auteur. Lead time médian. Cliquer sur un groupe ouvre sa slide.")}"""
    return slide_conteudo(n, titulo, corpo, id_="tabela")


def slide_grupo(n, g, m3):
    k, p = base.top_metade(g)
    nome, total = g["grupo"], g["integrantes"]
    p_en, p_pt, p_fr = pct(p)
    titulo = L(f"{nome}: {k} of {total} members made {p_en} of the Sprint 3 commits",
               f"{nome}: {k} de {total} integrantes fizeram {p_pt} dos commits da Sprint 3",
               f"{nome} : {k} membres sur {total} ont fait {p_fr} des commits du sprint 3")
    vals = g["commits_por_integrante"]
    i, f = _periodo(m3)
    corpo = f"""        <div class="grupo-corpo">
          <div>
            <p class="grafico-titulo">{L("Commits per member", "Commits por integrante", "Commits par membre")}</p>
            {barras(vals, max(max(vals), 1))}
            <p class="grafico-legenda">{L("Members ordered from most to fewest commits, without names.", "Integrantes ordenados do maior para o menor número de commits, sem nomes.", "Membres classés du plus au moins de commits, sans noms.")}</p>
          </div>
          <div class="indicadores">
            {indicador(g['commits'], ("commits in the sprint", "commits na sprint", "commits dans le sprint"))}
            {indicador(g['issues_fechadas_na_sprint'], ("issues closed", "issues fechadas", "issues fermées"))}
            {indicador(f"{g['mrs_com_revisao']}/{g['mrs_criados']}", ("MRs reviewed / created", "MRs revisados / criados", "MR relus / créés"))}
            {indicador(g['integrantes_sem_commit'], ("members without a commit", "integrantes sem commit", "membres sans commit"), destaque=g['integrantes_sem_commit'] > 0)}
          </div>
        </div>
{nota(f"Sprint 3, {i} to {f}. Commits exclude merge commits.",
      f"Sprint 3, de {i} a {f}. Commits sem commits de merge.",
      f"Sprint 3, du {i} au {f}. Commits hors commits de merge.",
      atalhos='<a href="#/tabela">' + L("Back to the table", "Voltar à tabela", "Retour au tableau") + "</a>")}"""
    return slide_conteudo(n, titulo, corpo, id_=nome.lower())


# ---------- Parte B: notas
def artefatos(n, notas):
    proj = notas["projeto"]
    todas = [p["grupos"][g]["nota_grupo"] for p in proj for g in GRUPOS]
    lo, hi = num(min(todas), 1), num(max(todas), 1)
    titulo = L(f"Group grades on the {len(proj)} graded project artifacts range from {lo[0]} to {hi[0]}",
               f"As notas de grupo nos {len(proj)} artefatos de projeto avaliados vão de {lo[1]} a {hi[1]}",
               f"Les notes de groupe sur les {len(proj)} livrables de projet notés vont de {lo[2]} à {hi[2]}")
    cabs = "\n".join(f'              <th>{C(p["nome"])}<span class="apoio">Sprint {p["sprint"]} &middot; {int(p["peso"])}%</span></th>'
                     for p in proj)
    linhas = []
    for g in GRUPOS:
        tds = "".join(f'<td>{N(p["grupos"][g]["nota_grupo"])}</td>' for p in proj)
        linhas.append(f'            <tr>\n              <th scope="row">{g}</th>{tds}\n            </tr>')
    medias = "".join(f'<td>{N(statistics.mean(p["grupos"][g]["nota_grupo"] for g in GRUPOS), 2)}</td>' for p in proj)
    linhas.append(f'            <tr class="total">\n              <th scope="row">{L("Class mean", "Média da turma", "Moyenne de la classe")}</th>{medias}\n            </tr>')
    pend = ", ".join(CURTO[p["nome"]][0] for p in notas["pendentes"])
    pend_pt = ", ".join(CURTO[p["nome"]][1] for p in notas["pendentes"])
    pend_fr = ", ".join(CURTO[p["nome"]][2] for p in notas["pendentes"])
    corpo = f"""        <table class="grupos-tabela">
          <thead>
            <tr>
              <th>{L("Group", "Grupo", "Groupe")}</th>
{cabs}
            </tr>
          </thead>
          <tbody>
{chr(10).join(linhas)}
          </tbody>
        </table>
{nota(f"Source: Adalove API, group grade, collected on 23/11. Sprint 3 grades not yet published: {pend}.",
      f"Fonte: API da Adalove, nota do grupo, coletada em 23/11. Notas da Sprint 3 ainda não publicadas: {pend_pt}.",
      f"Source : API Adalove, note du groupe, collectée le 23/11. Notes du sprint 3 pas encore publiées : {pend_fr}.")}"""
    return slide_conteudo(n, titulo, corpo, id_="artefatos")


def fator_individual(n, notas):
    fat = fatores_por_sprint(notas)
    s1, s2 = sorted(fat)[:2]
    todos1 = [v for g in GRUPOS for v in fat[s1][g]]
    todos2 = [v for g in GRUPOS for v in fat[s2][g]]
    m1, m2 = round(100 * statistics.mean(todos1)), round(100 * statistics.mean(todos2))
    titulo = L(f"The individual grade averaged {m2}% of the group grade in Sprint 2, down from {m1}% in Sprint 1",
               f"A nota individual ficou, em média, em {m2}% da nota do grupo na Sprint 2, contra {m1}% na Sprint 1",
               f"La note individuelle a représenté en moyenne {m2} % de la note du groupe au sprint 2, contre {m1} % au sprint 1")
    linhas = []
    for g in GRUPOS:
        a, b = fat[s1][g], fat[s2][g]
        baixos = sum(1 for v in b if v <= 0.7)
        linhas.append(f"""            <tr>
              <th scope="row">{g}</th>
              <td>{round(100 * media_fator(a))}%</td>
              <td>{round(100 * media_fator(b))}%</td>
              <td>{round(100 * min(b))}%&ndash;{round(100 * max(b))}%</td>
              <td>{baixos}/{len(b)}</td>
            </tr>""")
    baixos_t = sum(1 for v in todos2 if v <= 0.7)
    linhas.append(f"""            <tr class="total">
              <th scope="row">{L("Class", "Turma", "Classe")}</th>
              <td>{m1}%</td>
              <td>{m2}%</td>
              <td>{round(100 * min(todos2))}%&ndash;{round(100 * max(todos2))}%</td>
              <td>{baixos_t}/{len(todos2)}</td>
            </tr>""")
    corpo = f"""        <table class="grupos-tabela">
          <thead>
            <tr>
              <th>{L("Group", "Grupo", "Groupe")}</th>
              <th>{L("Mean, Sprint 1", "Média, Sprint 1", "Moyenne, sprint 1")}</th>
              <th>{L("Mean, Sprint 2", "Média, Sprint 2", "Moyenne, sprint 2")}</th>
              <th>{L("Range, Sprint 2", "Faixa, Sprint 2", "Écart, sprint 2")}</th>
              <th>{L("Members at 70% or less, Sprint 2", "Integrantes com 70% ou menos, Sprint 2", "Membres à 70 % ou moins, sprint 2")}</th>
            </tr>
          </thead>
          <tbody>
{chr(10).join(linhas)}
          </tbody>
        </table>
{nota("Individual grade divided by the group grade on the project artifacts of each sprint, without names. 0% is a member without a grade.",
      "Nota individual dividida pela nota do grupo nos artefatos de projeto de cada sprint, sem nomes. 0% é integrante sem nota.",
      "Note individuelle divisée par la note du groupe sur les livrables de projet de chaque sprint, sans noms. 0 % est un membre sans note.")}"""
    return slide_conteudo(n, titulo, corpo, id_="fator")


def autoestudos(n, notas):
    aut = notas["autoestudo"]
    pior = min(aut, key=lambda a: a["media_turma"])
    en, pt, fr = CURTO[pior["nome"]]
    m = num(pior["media_turma"], 2)
    titulo = L(f"{en} has the lowest class mean, {m[0]}, with {pior['abaixo_de_6']} of {pior['notas']} grades below 6",
               f"{pt} tem a menor média da turma, {m[1]}, com {pior['abaixo_de_6']} de {pior['notas']} notas abaixo de 6",
               f"{fr} a la moyenne de classe la plus basse, {m[2]}, avec {pior['abaixo_de_6']} notes sur {pior['notas']} sous 6")
    cabs = "".join(f"<th>{g}</th>" for g in GRUPOS)
    linhas = []
    for a in aut:
        tds = "".join(f'<td>{N(a["grupos"][g], 1)}</td>' for g in GRUPOS)
        linhas.append(f"""            <tr>
              <th scope="row">{C(a['nome'])}<span class="apoio">Sprint {a['sprint']} &middot; {int(a['peso'])}%</span></th>
              <td>{N(a['media_turma'], 2)}</td>{tds}
              <td>{a['abaixo_de_6']}</td>
              <td>{a['zeros']}</td>
            </tr>""")
    corpo = f"""        <table class="grupos-tabela">
          <thead>
            <tr>
              <th>{L("Self-study", "Autoestudo", "Auto-étude")}</th>
              <th>{L("Class", "Turma", "Classe")}</th>{cabs}
              <th>{L("Below 6", "Abaixo de 6", "Sous 6")}</th>
              <th>{L("Zero", "Zero", "Zéro")}</th>
            </tr>
          </thead>
          <tbody>
{chr(10).join(linhas)}
          </tbody>
        </table>
{nota(f"Individual grades from the Adalove export of {notas['export_individual_em'][8:10]}/{notas['export_individual_em'][5:7]}; group columns are means, without names.",
      f"Notas individuais do export da Adalove de {notas['export_individual_em'][8:10]}/{notas['export_individual_em'][5:7]}; colunas de grupo são médias, sem nomes.",
      f"Notes individuelles de l'export Adalove du {notas['export_individual_em'][8:10]}/{notas['export_individual_em'][5:7]} ; colonnes de groupe en moyennes, sans noms.")}"""
    return slide_conteudo(n, titulo, corpo, id_="autoestudos")


# ---------- Parte C: Sprint 4
def semana7(n):
    titulo = L("Calendar of week 7, 23/11 to 27/11", "Calendário da semana 7, 23/11 a 27/11",
               "Calendrier de la semaine 7, du 23/11 au 27/11")
    dias = [
        dia(cab("Mon", "Seg", "Lun.", "23/11"), [
            evento("marco", "Sprint 4 planning, today", "Planning da Sprint 4, hoje", "Planning du sprint 4, aujourd'hui"),
            evento("marco", "Each group presents its planning at the end of the day",
                   "Cada grupo apresenta a planning ao final do dia",
                   "Chaque groupe présente son planning en fin de journée")], "hoje"),
        dia(cab("Tue", "Ter", "Mar.", "24/11"), [evento_nome("aula", "Economics of Innovation")]),
        dia(cab("Wed", "Qua", "Mer.", "25/11"), [evento_nome("aula", "Statistical Inference: Hypothesis Testing")]),
        dia(cab("Thu", "Qui", "Jeu.", "26/11"), [evento_nome("aula", "Team Building: designing collaborative routines")]),
        dia(cab("Fri", "Sex", "Ven.", "27/11"), [
            evento_nome("aula", "DataApp Package with Layered Architecture"),
            evento_nome("entrega", "Business Question 2", 3),
            evento_nome("entrega", "DataApp Packaging", 4),
            evento_nome("entrega", "Math Challenge 2", 4)]),
    ]
    corpo = f"""        <div class="semana">
{chr(10).join(dias)}
        </div>
{LEGENDA}"""
    return slide_conteudo(n, titulo, corpo, id_="semana7")


def semana8(n):
    titulo = L("Calendar of week 8, 30/11 to 04/12", "Calendário da semana 8, 30/11 a 04/12",
               "Calendrier de la semaine 8, du 30/11 au 04/12")
    dias = [
        dia(cab("Mon", "Seg", "Lun.", "30/11"), [
            evento("marco", "Project follow-up", "Acompanhamento do projeto", "Suivi du projet")]),
        dia(cab("Tue", "Ter", "Mar.", "01/12"), [evento_nome("aula", "Data Storytelling and Action-Oriented Prototyping")]),
        dia(cab("Wed", "Qua", "Mer.", "02/12"), [evento_nome("aula", "DAG Automation")]),
        dia(cab("Thu", "Qui", "Jeu.", "03/12"), [evento_nome("aula", "Automated Testing")]),
        dia(cab("Fri", "Sex", "Ven.", "04/12"), [
            evento("marco", "Sprint Review 4", "Sprint Review 4", "Sprint Review 4"),
            evento_nome("entrega", "DataAPP: First Version", 4),
            evento_nome("entrega", "Prototyping Dossier and 5C Matrix", 6),
            evento_nome("entrega", "Business Deliverables", 3),
            evento_nome("entrega", "DAG and Testing Activity", 4),
            evento_nome("entrega", "Curation and DataViz Audit", 3)]),
    ]
    corpo = f"""        <div class="semana">
{chr(10).join(dias)}
        </div>
{LEGENDA}"""
    return slide_conteudo(n, titulo, corpo, id_="semana8")


def entregas(n, ativ, trad):
    s4 = [a for a in ativ if a["sprint"] == "4"]
    soma = sum(float(a["peso"]) for a in s4)
    proj = sum(float(a["peso"]) for a in s4 if a["tipo"] == "Desenvolvimento de Projeto")
    titulo = L(f"Sprint 4 holds {int(soma)}% of the module weight in {len(s4)} deliveries, {int(proj)}% of it in group artifacts",
               f"A Sprint 4 reúne {int(soma)}% do peso do módulo em {len(s4)} entregas, {int(proj)}% delas em artefatos do grupo",
               f"Le sprint 4 réunit {int(soma)} % du poids du module en {len(s4)} livrables, dont {int(proj)} % en livrables de groupe")
    tipo = {"Desenvolvimento de Projeto": ("Group artifact", "Artefato do grupo", "Livrable du groupe"),
            "Autoestudo": ("Individual self-study", "Autoestudo individual", "Auto-étude individuelle")}
    linhas = []
    for a in sorted(s4, key=lambda x: (x["data"][3:5] + x["data"][:2], x["tipo"] != "Desenvolvimento de Projeto", x["nome"])):
        t = trad[a["nome"]]
        linhas.append(
            f'            <tr>\n              <td class="data">{a["data"][:5]}</td>\n'
            f'              <td><span data-l="en">{a["nome"]}</span><span data-l="pt">{t["pt"]}</span><span data-l="fr">{t["fr"]}</span></td>\n'
            f'              <td>{L(*tipo[a["tipo"]])}</td>\n'
            f'              <td class="peso">{int(float(a["peso"]))}%</td>\n            </tr>')
    corpo = f"""        <table class="ref-tabela densa">
          <thead>
            <tr>
              <th>{L("Date", "Data", "Date")}</th>
              <th>{L("Delivery", "Entrega", "Livrable")}</th>
              <th>{L("Type", "Tipo", "Type")}</th>
              <th>{L("Weight", "Peso", "Poids")}</th>
            </tr>
          </thead>
          <tbody>
{chr(10).join(linhas)}
          </tbody>
        </table>"""
    return slide_conteudo(n, titulo, corpo, id_="entregas")


def apresentacao_planning(n):
    if HORARIO_APRESENTACAO:
        h = HORARIO_APRESENTACAO
        titulo = L(f"Planning presentation per group, today at {h}", f"Apresentação da planning por grupo, hoje às {h}",
                   f"Présentation du planning par groupe, aujourd'hui à {h}")
    else:
        titulo = L("Planning presentation per group, at the end of the day",
                   "Apresentação da planning por grupo, ao final do dia",
                   "Présentation du planning par groupe, en fin de journée")
    passos = [
        ("Sprint 4 goal in one sentence, tied to the 04/12 deliveries.",
         "Objetivo da Sprint 4 em uma frase, ligado às entregas de 04/12.",
         "Objectif du sprint 4 en une phrase, lié aux livrables du 04/12."),
        ("Backlog in the GitLab board: every card with an ID, a size, and exactly one owner.",
         "Backlog no board do GitLab: todo card com ID, tamanho e exatamente um dono.",
         "Backlog dans le tableau GitLab : chaque carte avec un identifiant, une taille et un seul responsable."),
        ("Distribution per member and who reviews whose merge requests.",
         "Distribuição por integrante e quem revisa os merge requests de quem.",
         "Répartition par membre et qui relit les merge requests de qui."),
        ("Path to the Sprint Review 4 demonstration: what will run, on which data.",
         "Caminho até a demonstração da Sprint Review 4: o que vai rodar e sobre quais dados.",
         "Chemin jusqu'à la démonstration de la Sprint Review 4 : ce qui tournera et sur quelles données."),
        ("What changes from Sprint 3, given the numbers shown today.",
         "O que muda em relação à Sprint 3, a partir dos números de hoje.",
         "Ce qui change par rapport au sprint 3, à partir des chiffres d'aujourd'hui."),
    ]
    lis = "\n".join(f"          <li><span>{L(*p)}</span></li>" for p in passos)
    corpo = f"""        <ol class="passos compacta">
{lis}
        </ol>
{nota("The board is the source of truth: a task outside the board does not count as delivered.",
      "O board é a fonte da verdade: tarefa fora do board não conta como entregue.",
      "Le tableau fait foi : une tâche hors du tableau ne compte pas comme livrée.")}"""
    return slide_conteudo(n, titulo, corpo, id_="planning")


def encerramento():
    return f"""      <!-- Encerramento -->
      <section class="end-slide">
        <img class="inteli-logo-header" src="../assets/img/inteli-logo-negativa.svg" alt="Inteli">
        <div class="end-accent"></div>
        <h1>
          {L("Questions", "Dúvidas", "Questions")}
        </h1>
        <h3>
          {L("Sprint Planning 4", "Sprint Planning 4", "Sprint Planning 4")}
        </h3>
        <p class="end-assinatura">
          <span data-l="en">Prof. José Romualdo &middot; Project advisor &middot; SI08 T18 &middot; 2026-2B</span>
          <span data-l="pt">Prof. José Romualdo &middot; Orientação &middot; SI08 T18 &middot; 2026-2B</span>
          <span data-l="fr">Prof. José Romualdo &middot; Orientation du projet &middot; SI08 T18 &middot; 2026-2B</span>
        </p>
      </section>
"""


# ------------------------------------------------------------------ montagem
def gerar():
    """HTML completo do deck, sem gravar."""
    base.RODAPE = RODAPE  # slide_conteudo le o rodape do modulo base
    notas, m3, m2, ativ, trad = carregar()
    slides = []

    def pos():
        return len(slides) + 1

    slides.append(capa())
    slides.append(agenda(pos(), m3 is not None))
    parte = iter("ABC")
    if m3:
        p = next(parte)
        i, f = _periodo(m3)
        slides.append(secao(pos(), (f"Part {p}", f"Parte {p}", f"Partie {p}"),
                            ("Sprint 3 in GitLab", "Sprint 3 no GitLab", "Le sprint 3 dans GitLab"),
                            (f"Data from {i} to {f}, by group and without names", f"Dados de {i} a {f}, por grupo e sem nomes",
                             f"Données du {i} au {f}, par groupe et sans noms")))
        slides.append(numeros_gitlab(pos(), m3, m2))
        slides.append(tabela_gitlab(pos(), m3))
        for g in m3["grupos"]:
            slides.append(slide_grupo(pos(), g, m3))
    p = next(parte)
    slides.append(secao(pos(), (f"Part {p}", f"Parte {p}", f"Partie {p}"),
                        ("Graded deliveries", "Ponderadas", "Livrables notés"),
                        ("Grades published in Adalove, by group and without names", "Notas publicadas na Adalove, por grupo e sem nomes",
                         "Notes publiées dans Adalove, par groupe et sans noms")))
    slides.append(artefatos(pos(), notas))
    slides.append(fator_individual(pos(), notas))
    slides.append(autoestudos(pos(), notas))
    p = next(parte)
    slides.append(secao(pos(), (f"Part {p}", f"Parte {p}", f"Partie {p}"),
                        ("Sprint 4", "Sprint 4", "Sprint 4"),
                        ("Calendar, deliveries, and the planning presentation", "Calendário, entregas e apresentação da planning",
                         "Calendrier, livrables et présentation du planning")))
    slides.append(semana7(pos()))
    slides.append(semana8(pos()))
    slides.append(entregas(pos(), ativ, trad))
    slides.append(apresentacao_planning(pos()))
    slides.append(encerramento())

    return f"""<!doctype html>
<html lang="en" data-lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sprint Planning 4 &middot; SI08 T18</title>

  <!-- Gerado por tools/gerar_sprint_planning_4.py (nao editar a mao). Deck trilingue
       (ADR-001); metricas do GitLab por grupo sem nomes (ADR-005); notas agregadas por
       grupo sem nomes (ADR-007). -->

  <script src="../assets/js/idioma.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css">
  <link rel="stylesheet" href="../assets/css/inteli-brand.css">
  <link rel="stylesheet" href="../assets/css/inteli-theme.css">
  <link rel="stylesheet" href="../assets/css/orientacao.css">
  <link rel="stylesheet" href="../assets/css/retrospectiva.css">
  <link rel="stylesheet" href="../assets/css/inteli-print.css" media="print">
</head>
<body>
  <div class="reveal">
    <div class="slides">

{chr(10).join(slides)}
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
  <script>
    Reveal.initialize({{
      width: 1280, height: 720, center: false, margin: 0,
      hash: true, slideNumber: false, transition: 'fade'
    }});
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    saida = gerar()
    SAIDA.write_text(saida, encoding="utf-8")
    print(f"gravado {SAIDA} ({saida.count('<section')} slides)")
