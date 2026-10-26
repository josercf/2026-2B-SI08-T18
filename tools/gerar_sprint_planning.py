#!/usr/bin/env python3
"""Gera aulas/sprint-planning-2.html a partir dos dados versionados.

Entradas:
    dados/metricas_sprint1.json        (tools/coletar_gitlab.py)
    dados/atividades_ponderadas.csv    (tools/extrair_lbl.py)
    dados/traducoes_atividades.csv
    dados/grupos.js                    (so para contar integrantes)

Uso:
    python3 tools/gerar_sprint_planning.py

O deck e trilingue (ADR-001). Todo numero dos slides de retrospectiva vem do JSON de
metricas; nenhum e escrito a mao. Rodar de novo depois de recoletar as metricas.
"""
import csv
import json
import math
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "aulas" / "sprint-planning-2.html"
RODAPE = "SI08 &middot; T18 &middot; Sprint Planning 2"
DIAS_DE_EXECUCAO = 7  # 9 dias uteis de 26/10 a 06/11 (feriado em 02/11), menos planning e review


# ------------------------------------------------------------------ dados
def carregar():
    metricas = json.loads((RAIZ / "dados" / "metricas_sprint1.json").read_text(encoding="utf-8"))
    with open(RAIZ / "dados" / "atividades_ponderadas.csv", encoding="utf-8") as fh:
        ativ = list(csv.DictReader(fh))
    with open(RAIZ / "dados" / "traducoes_atividades.csv", encoding="utf-8") as fh:
        trad = {r["nome"]: r for r in csv.DictReader(fh)}
    bruto = (RAIZ / "dados" / "grupos.js").read_text(encoding="utf-8")
    grupos = json.loads(bruto[bruto.index("{"):bruto.rindex("}") + 1])
    return metricas, ativ, trad, grupos


# ------------------------------------------------------------------ texto
def L(en, pt, fr):
    return (f'<span data-l="en">{en}</span>\n'
            f'            <span data-l="pt">{pt}</span>\n'
            f'            <span data-l="fr">{fr}</span>')


def num(valor, casas=0):
    """(en, pt, fr) de um numero; ponto decimal em ingles, virgula em pt e fr."""
    base = f"{valor:.{casas}f}"
    return base, base.replace(".", ","), base.replace(".", ",")


def pct(valor):
    return f"{valor}%", f"{valor}%", f"{valor}&nbsp;%"


def n3(valor, casas=0):
    return num(valor, casas)


def slide_conteudo(n, titulo, corpo, logo="positiva", id_=None, extra_class=""):
    ident = f' id="{id_}"' if id_ else ""
    return f"""      <section class="content-slide{extra_class}"{ident}>
        <div class="top-bar"></div>
        <img class="inteli-logo-header" src="../assets/img/inteli-logo-{logo}.svg" alt="Inteli">
        <div class="slide-title-area">
          <div class="accent-bar"></div>
          <h2>
            {titulo}
          </h2>
        </div>
{corpo}
        <div class="slide-footer">
          <p class="footer-bar">{RODAPE}</p>
          <p class="footer-page">{n}</p>
        </div>
      </section>
"""


def nota(en, pt, fr, atalhos=""):
    return f"""        <p class="nota-fonte">
          {L(en, pt, fr)}
          {atalhos}
        </p>"""


def barras(valores, maximo):
    cols = []
    for v in valores:
        altura = 0 if v == 0 else max(2, round(v / maximo * 82))
        cols.append(
            f'<div class="barra{" zero" if v == 0 else ""}"><p class="num">{v}</p>'
            f'<div class="col" style="height:{altura}%"></div></div>')
    return '<div class="barras">' + "".join(cols) + "</div>"


def indicador(valor, rot, destaque=False):
    cls = " destaque" if destaque else ""
    return (f'<div class="indicador{cls}"><p class="valor">{valor}</p>'
            f'<p class="rotulo">{L(*rot)}</p></div>')


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
              <span data-l="en">Sprint Planning 2</span>
              <span data-l="pt">Sprint Planning 2</span>
              <span data-l="fr">Sprint Planning 2</span>
            </h1>
            <h3>
              <span data-l="en">Sprint 1 retrospective and Sprint 2 plan</span>
              <span data-l="pt">Retrospectiva da Sprint 1 e plano da Sprint 2</span>
              <span data-l="fr">Rétrospective du sprint 1 et plan du sprint 2</span>
            </h3>
          </div>
        </div>
      </section>
"""


def agenda(n):
    itens = [
        ("Sprint 1 retrospective in numbers", "Retrospectiva da Sprint 1 em números",
         "Rétrospective du sprint 1 en chiffres"),
        ("Each group in detail", "Cada grupo em detalhe", "Chaque groupe en détail"),
        ("Work process document", "Documento do processo de trabalho",
         "Document du processus de travail"),
        ("Sprint 2 artifacts and calendar", "Artefatos e calendário da Sprint 2",
         "Livrables et calendrier du sprint 2"),
        ("Suggested topics for the planning", "Tópicos sugeridos para o planejamento",
         "Sujets suggérés pour la planification"),
        ("Planning closed today", "Planejamento fechado hoje",
         "Planification clôturée aujourd'hui"),
        ("Individual oral defenses", "Arguições individuais", "Soutenances individuelles"),
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


def secao(n, eyebrow, titulo, sub):
    return f"""      <!-- {n} - Separador -->
      <section class="section-slide">
        <img class="inteli-logo-header" src="../assets/img/inteli-logo-positiva.svg" alt="Inteli">
        <p class="section-eyebrow">
          {L(*eyebrow)}
        </p>
        <div class="accent-bar"></div>
        <h2>
          {L(*titulo)}
        </h2>
        <h3>
          {L(*sub)}
        </h3>
      </section>
"""


def totais(gs):
    chaves = ["commits", "issues_abertas_na_sprint", "issues_fechadas_na_sprint",
              "mrs_criados", "mrs_merged", "mrs_com_revisao"]
    return {k: sum(g[k] for g in gs) for k in chaves}


def numeros_grandes(n, m):
    gs = m["grupos"]
    t = totais(gs)
    lt = [g["lead_time_issue_dias_mediana"] for g in gs]
    lo, hi = min(lt), max(lt)
    titulo = L(
        f"Sprint 1: {t['commits']} commits, {t['issues_abertas_na_sprint']} issues opened and "
        f"{t['issues_fechadas_na_sprint']} closed",
        f"Sprint 1: {t['commits']} commits, {t['issues_abertas_na_sprint']} issues abertas e "
        f"{t['issues_fechadas_na_sprint']} fechadas",
        f"Sprint 1 : {t['commits']} commits, {t['issues_abertas_na_sprint']} issues ouvertes et "
        f"{t['issues_fechadas_na_sprint']} fermées")

    def bloco(valor, rot, cls=""):
        return (f'<div class="numero {cls}"><p class="valor">{valor}</p>'
                f'<p class="rotulo">{L(*rot)}</p></div>')

    en_lo, pt_lo, _ = n3(lo, 1)
    en_hi, pt_hi, _ = n3(hi, 1)
    faixa = f'<span data-l="en">{en_lo} to {en_hi}</span><span data-l="pt">{pt_lo} a {pt_hi}</span>' \
            f'<span data-l="fr">{pt_lo} à {pt_hi}</span>'
    corpo = f"""        <div class="numeros-grandes">
          {bloco(t['commits'], ("commits across the five groups", "commits nos cinco grupos", "commits dans les cinq groupes"))}
          {bloco(t['issues_abertas_na_sprint'], ("issues opened during the sprint", "issues abertas durante a sprint", "issues ouvertes pendant le sprint"), "verde")}
          {bloco(t['issues_fechadas_na_sprint'], ("issues closed during the sprint", "issues fechadas durante a sprint", "issues fermées pendant le sprint"), "verde")}
          {bloco(t['mrs_merged'], (f"merge requests merged, out of {t['mrs_criados']} created", f"merge requests integrados, de {t['mrs_criados']} criados", f"merge requests intégrés, sur {t['mrs_criados']} créés"), "destaque")}
          {bloco(t['mrs_com_revisao'], ("merge requests with a comment from another member", "merge requests com comentário de outro integrante", "merge requests avec un commentaire d'un autre membre"), "destaque")}
          {bloco(faixa, ("days of median issue lead time, by group", "dias de lead time mediano de issue, por grupo", "jours de lead time médian des issues, par groupe"))}
        </div>
{nota("Source: GitLab (git.inteli.edu.br), 14/10 to 23/10, collected on 26/10. Commits exclude merge commits. Lead time runs from creation to closing.",
      "Fonte: GitLab (git.inteli.edu.br), de 14/10 a 23/10, coletado em 26/10. Commits sem commits de merge. Lead time vai da criação ao fechamento.",
      "Source : GitLab (git.inteli.edu.br), du 14/10 au 23/10, collecté le 26/10. Commits hors commits de merge. Le lead time va de la création à la fermeture.")}"""
    return slide_conteudo(n, titulo, corpo)


def tabela_grupos(n, m, grupos_slide):
    gs = m["grupos"]
    t = totais(gs)
    lt = [g["lead_time_issue_dias_mediana"] for g in gs]
    en_lo, pt_lo, fr_lo = n3(min(lt), 1)
    en_hi, pt_hi, fr_hi = n3(max(lt), 1)
    titulo = L(f"Issue lead time ranges from {en_lo} to {en_hi} days across groups",
               f"O lead time de issue varia de {pt_lo} a {pt_hi} dias entre os grupos",
               f"Le lead time des issues varie de {fr_lo} à {fr_hi} jours selon les groupes")
    linhas = []
    for g in gs:
        ident = grupos_slide[g["grupo"]]
        _, lt_i, _ = n3(g["lead_time_issue_dias_mediana"], 1)
        _, lt_m, _ = n3(g["lead_time_mr_dias_mediana"], 1)
        en_i, pt_i, fr_i = n3(g["lead_time_issue_dias_mediana"], 1)
        en_m, pt_m, fr_m = n3(g["lead_time_mr_dias_mediana"], 1)
        linhas.append(f"""            <tr>
              <th scope="row"><a href="#/{ident}">{g['grupo']}</a></th>
              <td>{g['integrantes']}</td>
              <td>{g['commits']}</td>
              <td>{g['issues_abertas_na_sprint']}</td>
              <td>{g['issues_fechadas_na_sprint']}</td>
              <td>{g['mrs_com_revisao']}/{g['mrs_criados']}</td>
              <td><span data-l="en">{en_i}</span><span data-l="pt">{pt_i}</span><span data-l="fr">{fr_i}</span></td>
              <td><span data-l="en">{en_m}</span><span data-l="pt">{pt_m}</span><span data-l="fr">{fr_m}</span></td>
            </tr>""")
    integrantes = sum(g["integrantes"] for g in gs)
    linhas.append(f"""            <tr class="total">
              <th scope="row">{L("Class", "Turma", "Classe")}</th>
              <td>{integrantes}</td>
              <td>{t['commits']}</td>
              <td>{t['issues_abertas_na_sprint']}</td>
              <td>{t['issues_fechadas_na_sprint']}</td>
              <td>{t['mrs_com_revisao']}/{t['mrs_criados']}</td>
              <td>&ndash;</td>
              <td>&ndash;</td>
            </tr>""")
    corpo = f"""        <table class="grupos-tabela">
          <thead>
            <tr>
              <th>{L("Group", "Grupo", "Groupe")}</th>
              <th>{L("Members", "Integrantes", "Membres")}</th>
              <th>Commits</th>
              <th>{L("Issues opened", "Issues abertas", "Issues ouvertes")}</th>
              <th>{L("Issues closed", "Issues fechadas", "Issues fermées")}</th>
              <th>{L("MRs reviewed / created", "MRs revisados / criados", "MR relus / créés")}</th>
              <th>{L("Issue lead time (days)", "Lead time de issue (dias)", "Lead time issue (jours)")}</th>
              <th>{L("MR lead time (days)", "Lead time de MR (dias)", "Lead time MR (jours)")}</th>
            </tr>
          </thead>
          <tbody>
{chr(10).join(linhas)}
          </tbody>
        </table>
{nota("Median lead time. MR reviewed: has a comment from a member other than the author. Click a group to open its slides.",
      "Lead time mediano. MR revisado: tem comentário de integrante diferente do autor. Clicar no grupo abre os slides dele.",
      "Lead time médian. MR relu : comporte un commentaire d'un membre autre que l'auteur. Cliquer sur un groupe ouvre ses slides.")}"""
    return slide_conteudo(n, titulo, corpo, id_="tabela")


def top_metade(g):
    valores = g["commits_por_integrante"]
    k = math.ceil(len(valores) / 2)
    return k, round(100 * sum(valores[:k]) / g["commits"])


def slide_grupo_commits(n, g, ident):
    k, p = top_metade(g)
    nome, total = g["grupo"], g["integrantes"]
    p_en, p_pt, p_fr = pct(p)
    titulo = L(f"{nome}: {k} of {total} members make {p_en} of the commits",
               f"{nome}: {k} de {total} integrantes fazem {p_pt} dos commits",
               f"{nome} : {k} membres sur {total} font {p_fr} des commits")
    vals = g["commits_por_integrante"]
    corpo = f"""        <div class="grupo-corpo">
          <div>
            <p class="grafico-titulo">{L("Commits per member", "Commits por integrante", "Commits par membre")}</p>
            {barras(vals, max(vals))}
            <p class="grafico-legenda">{L("Members ordered from most to fewest commits, without names.", "Integrantes ordenados do maior para o menor número de commits, sem nomes.", "Membres classés du plus au moins de commits, sans noms.")}</p>
          </div>
          <div class="indicadores">
            {indicador(g['commits'], ("commits in the sprint", "commits na sprint", "commits dans le sprint"))}
            {indicador(g['issues_abertas_na_sprint'], ("issues opened", "issues abertas na sprint", "issues ouvertes"))}
            {indicador(g['issues_fechadas_na_sprint'], ("issues closed", "issues fechadas na sprint", "issues fermées"))}
            {indicador(g['issues_abertas_agora'], ("issues still open on 26/10", "issues ainda abertas em 26/10", "issues encore ouvertes le 26/10"), destaque=g['issues_abertas_agora'] > 0)}
          </div>
        </div>
{nota("Sprint 1, 14/10 to 23/10. Commits exclude merge commits.",
      "Sprint 1, de 14/10 a 23/10. Commits sem commits de merge.",
      "Sprint 1, du 14/10 au 23/10. Commits hors commits de merge.",
      atalhos='<a href="#/tabela">' + L("Back to the table", "Voltar à tabela", "Retour au tableau") + "</a>")}"""
    return slide_conteudo(n, titulo, corpo, id_=ident)


def slide_grupo_fluxo(n, g, ident):
    nome = g["grupo"]
    criados, revisados = g["mrs_criados"], g["mrs_com_revisao"]
    titulo = L(f"{nome}: {revisados} of {criados} MRs were reviewed by teammates",
               f"{nome}: {revisados} de {criados} MRs foram revisados por colegas",
               f"{nome} : {revisados} MR sur {criados} relus par des collègues")
    vals = g["revisoes_por_integrante"]
    en_i, pt_i, fr_i = n3(g["lead_time_issue_dias_mediana"], 1)
    en_m, pt_m, fr_m = n3(g["lead_time_mr_dias_mediana"], 1)
    li = f'<span data-l="en">{en_i}</span><span data-l="pt">{pt_i}</span><span data-l="fr">{fr_i}</span>'
    lm = f'<span data-l="en">{en_m}</span><span data-l="pt">{pt_m}</span><span data-l="fr">{fr_m}</span>'
    corpo = f"""        <div class="grupo-corpo">
          <div>
            <p class="grafico-titulo">{L("Review comments per member", "Comentários de revisão por integrante", "Commentaires de revue par membre")}</p>
            {barras(vals, max(max(vals), 1))}
            <p class="grafico-legenda">{L("Comments on other members' MRs, without names. A red bar is a member with none.", "Comentários em MRs de outros integrantes, sem nomes. Barra vermelha é integrante sem nenhum.", "Commentaires sur les MR des autres membres, sans noms. Une barre rouge est un membre sans aucun.")}</p>
          </div>
          <div class="indicadores">
            {indicador(criados, ("merge requests created", "merge requests criados", "merge requests créés"))}
            {indicador(g['mrs_merged'], ("merge requests merged", "merge requests integrados", "merge requests intégrés"))}
            {indicador(li, ("days of median issue lead time", "dias de lead time mediano de issue", "jours de lead time médian des issues"), destaque=True)}
            {indicador(lm, ("days of median MR lead time", "dias de lead time mediano de MR", "jours de lead time médian des MR"))}
          </div>
        </div>
{nota("Sprint 1, 14/10 to 23/10. Lead time: issue from creation to closing, MR from creation to merge.",
      "Sprint 1, de 14/10 a 23/10. Lead time: da criação ao fechamento na issue, da criação ao merge no MR.",
      "Sprint 1, du 14/10 au 23/10. Lead time : de la création à la fermeture pour l'issue, de la création au merge pour le MR.",
      atalhos='<a href="#/tabela">' + L("Back to the table", "Voltar à tabela", "Retour au tableau") + "</a>")}"""
    return slide_conteudo(n, titulo, corpo, id_=ident)


def processo_atividade(n):
    titulo = L("Activity: the group's work process document",
               "Atividade: documento do processo de trabalho do grupo",
               "Activité : document du processus de travail du groupe")
    passos = [
        ("Describe how Sprint 1 worked in practice: board, daily, MR reviews, and commits.",
         "Descrever como a Sprint 1 funcionou na prática: quadro, daily, revisão de MRs e commits.",
         "Décrire le fonctionnement réel du sprint 1 : tableau, daily, revue des MR et commits."),
        ("Compare the description with the planning rules: checklist, DoR, DoD, and WIP.",
         "Comparar a descrição com as regras da planning: checklist, DoR, DoD e WIP.",
         "Comparer la description avec les règles du planning : checklist, DoR, DoD et WIP."),
        ("Write the Sprint 2 process in <code>docs/processo.md</code> in the group repository.",
         "Escrever o processo da Sprint 2 em <code>docs/processo.md</code> no repositório do grupo.",
         "Rédiger le processus du sprint 2 dans <code>docs/processo.md</code> du dépôt du groupe."),
        ("Open a merge request with the document and have another member review it.",
         "Abrir um merge request com o documento e pedir a revisão de outro integrante.",
         "Ouvrir une merge request avec le document et demander la relecture d'un autre membre."),
    ]
    lis = "\n".join(f"          <li><span>{L(*p)}</span></li>" for p in passos)
    corpo = f"""        <ol class="passos">
{lis}
        </ol>
{nota("The document is done today, together with the planning, and versioned on the group's main branch.",
      "O documento é feito hoje, junto com a planning, e versionado na main do grupo.",
      "Le document est rédigé aujourd'hui, avec le planning, et versionné sur la main du groupe.")}"""
    return slide_conteudo(n, titulo, corpo)


def processo_conteudo(n):
    titulo = L("Minimum content of the process document",
               "Conteúdo mínimo do documento de processo",
               "Contenu minimal du document de processus")
    linhas = [
        (("Board and columns", "Quadro e colunas", "Tableau et colonnes"),
         ("Board columns, DoR to enter Doing, DoD to enter Done, WIP of 1 card per student.",
          "Colunas do quadro, DoR para entrar em Doing, DoD para entrar em Done, WIP de 1 card por aluno.",
          "Colonnes du tableau, DoR pour entrer en Doing, DoD pour entrer en Done, WIP de 1 carte par étudiant.")),
        (("Estimation and breakdown", "Estimativa e corte", "Estimation et découpage"),
         ("Sizes S, M, L, and XL (15, 30, 60, and 120 min), breakdown by value, and review time.",
          "Tamanhos P, M, G e GG (15, 30, 60 e 120 min), corte por valor e tempo de revisão.",
          "Tailles S, M, L et XL (15, 30, 60 et 120 min), découpage par valeur et temps de revue.")),
        (("Daily", "Daily", "Daily"),
         ("Time, Scrum Master, and reading the board from right to left.",
          "Horário, scrum master e leitura do quadro da direita para a esquerda.",
          "Horaire, Scrum Master et lecture du tableau de droite à gauche.")),
        (("Code review", "Revisão de código", "Revue de code"),
         ("Who reviews, review pyramid, merge request template, and review deadline.",
          "Quem revisa, pirâmide de revisão, template de merge request e prazo para revisar.",
          "Qui relit, pyramide de revue, modèle de merge request et délai de relecture.")),
        (("Commits and branches", "Commits e branches", "Commits et branches"),
         ("Semantic messages linked to the issue (#number) and the branch naming convention.",
          "Mensagens semânticas ligadas à issue (#número) e convenção de nome de branch.",
          "Messages sémantiques liés à l'issue (#numéro) et convention de nommage des branches.")),
    ]
    trs = "\n".join(
        f'            <tr>\n              <th scope="row">{L(*a)}</th>\n              <td>{L(*b)}</td>\n            </tr>'
        for a, b in linhas)
    corpo = f"""        <table class="ref-tabela grande">
          <thead>
            <tr>
              <th>{L("Section", "Seção", "Section")}</th>
              <th>{L("What the group describes", "O que o grupo descreve", "Ce que le groupe décrit")}</th>
            </tr>
          </thead>
          <tbody>
{trs}
          </tbody>
        </table>"""
    return slide_conteudo(n, titulo, corpo)


def evento(tipo, en, pt, fr):
    return f'<p class="ev {tipo}">{L(en, pt, fr)}</p>'


def evento_nome(tipo, nome, peso=None):
    extra = f" &middot; {peso}%" if peso else ""
    return f'<p class="ev {tipo}">{nome}{extra}</p>'


def dia(cab, eventos, cls=""):
    c = f" {cls}" if cls else ""
    corpo = "\n              ".join(eventos)
    return f"""          <div class="dia{c}">
            <p class="dia-cab">{cab}</p>
            <div class="dia-corpo">
              {corpo}
            </div>
          </div>"""


def cab(en, pt, fr, data):
    return f'<span data-l="en">{en} {data}</span><span data-l="pt">{pt} {data}</span><span data-l="fr">{fr} {data}</span>'


LEGENDA = f"""        <div class="legenda">
          <span class="l-aula">{L("Instruction", "Instrução", "Cours")}</span>
          <span class="l-entrega">{L("Weighted delivery", "Entrega ponderada", "Livrable noté")}</span>
          <span class="l-marco">{L("Milestone", "Marco", "Jalon")}</span>
        </div>"""


def semana3(n):
    titulo = L("Calendar of week 3, 26/10 to 30/10", "Calendário da semana 3, 26/10 a 30/10",
               "Calendrier de la semaine 3, du 26/10 au 30/10")
    dias = [
        dia(cab("Mon", "Seg", "Lun.", "26/10"), [
            evento("marco", "Sprint 2 planning, today", "Planning da Sprint 2, hoje", "Planning du sprint 2, aujourd'hui"),
            evento("marco", "Scheduling of the oral defenses", "Agendamento das arguições", "Planification des soutenances")], "hoje"),
        dia(cab("Tue", "Ter", "Mar.", "27/10"), [
            evento_nome("aula", "PCA"),
            evento("marco", "Scheduling of the oral defenses", "Agendamento das arguições", "Planification des soutenances")]),
        dia(cab("Wed", "Qua", "Mer.", "28/10"), [evento_nome("aula", "Relationships")]),
        dia(cab("Thu", "Qui", "Jeu.", "29/10"), [
            evento_nome("aula", "ETL"),
            evento("marco", "Last day of the oral defenses", "Último dia das arguições", "Dernier jour des soutenances")]),
        dia(cab("Fri", "Sex", "Ven.", "30/10"), [
            evento_nome("aula", "Market intelligence"),
            evento_nome("entrega", "Graded Assignment: Hierarchical Classification", 3)]),
    ]
    corpo = f"""        <div class="semana">
{chr(10).join(dias)}
        </div>
{LEGENDA}"""
    return slide_conteudo(n, titulo, corpo, id_="semana3")


def semana4(n):
    titulo = L("Calendar of week 4, 02/11 to 06/11", "Calendário da semana 4, 02/11 a 06/11",
               "Calendrier de la semaine 4, du 02/11 au 06/11")
    dias = [
        dia(cab("Mon", "Seg", "Lun.", "02/11"), [
            evento("marco", "Holiday: All Souls' Day", "Feriado: Finados", "Jour férié : Jour des défunts")], "feriado"),
        dia(cab("Tue", "Ter", "Mar.", "03/11"), [evento_nome("aula", "Centroids")]),
        dia(cab("Wed", "Qua", "Mer.", "04/11"), [
            evento_nome("aula", "Competitive Analysis"),
            evento("marco", "Presentation due, 6 pm", "Envio da apresentação, 18h", "Envoi de la présentation, 18 h")]),
        dia(cab("Thu", "Qui", "Jeu.", "05/11"), [evento_nome("aula", "Data Warehouses")]),
        dia(cab("Fri", "Sex", "Ven.", "06/11"), [
            evento("marco", "Sprint Review", "Sprint Review", "Sprint Review"),
            evento_nome("entrega", "Data Ingestion Structure", 6),
            evento_nome("entrega", "MAI-MD", 4),
            evento_nome("entrega", "Math Challenge 1", 4),
            evento_nome("entrega", "Business Question 1", 3),
            evento("marco", "Artifact on main, 11:59 pm", "Artefato na main, 23h59", "Livrable sur main, 23 h 59")]),
    ]
    corpo = f"""        <div class="semana">
{chr(10).join(dias)}
        </div>
{LEGENDA}"""
    return slide_conteudo(n, titulo, corpo, id_="semana4")


def entregas(n, ativ, trad):
    s2 = [a for a in ativ if a["sprint"] == "2"]
    soma = sum(float(a["peso"]) for a in s2)
    assert soma == 20.0, soma
    titulo = L(f"Sprint 2 holds {int(soma)}% of the module weight in {len(s2)} deliveries",
               f"A Sprint 2 reúne {int(soma)}% do peso do módulo em {len(s2)} entregas",
               f"Le sprint 2 réunit {int(soma)} % du poids du module en {len(s2)} livrables")
    linhas = ['            <tr class="marco">\n              <td class="data">06/11</td>\n'
              f'              <td>{L("Sprint artifact: Data ingestion system, on main by 11:59 pm", "Artefato da sprint: Data ingestion system, na main até 23h59", "Livrable du sprint : Data ingestion system, sur main avant 23 h 59")}</td>\n'
              '              <td class="peso">&ndash;</td>\n            </tr>']
    for a in sorted(s2, key=lambda x: (x["data"][3:5], x["data"][:2])):
        t = trad[a["nome"]]
        peso = int(float(a["peso"]))
        linhas.append(
            f'            <tr>\n              <td class="data">{a["data"][:5]}</td>\n'
            f'              <td><span data-l="en">{a["nome"]}</span><span data-l="pt">{t["pt"]}</span><span data-l="fr">{t["fr"]}</span></td>\n'
            f'              <td class="peso">{peso}%</td>\n            </tr>')
    corpo = f"""        <table class="ref-tabela grande">
          <thead>
            <tr>
              <th>{L("Date", "Data", "Date")}</th>
              <th>{L("Delivery", "Entrega", "Livrable")}</th>
              <th>{L("Weight", "Peso", "Poids")}</th>
            </tr>
          </thead>
          <tbody>
{chr(10).join(linhas).replace(chr(10) + '              <th', chr(10) + '              <th')}
          </tbody>
        </table>
{nota("Weights from the module plan (Adalove export of 14/10). The sprint artifact has no separate weight.",
      "Pesos do plano do módulo (export da Adalove de 14/10). O artefato da sprint não tem peso separado.",
      "Poids du plan du module (export Adalove du 14/10). Le livrable du sprint n'a pas de poids distinct.")}"""
    return slide_conteudo(n, titulo, corpo)


def topicos(n):
    titulo = L("Suggested topics for planning Sprint 2",
               "Tópicos sugeridos para planejar a Sprint 2",
               "Sujets suggérés pour planifier le sprint 2")
    linhas = [
        (("Data ingestion: sources, structure, and pipeline", "Ingestão de dados: fontes, estrutura e pipeline", "Ingestion des données : sources, structure et pipeline"),
         "Data Ingestion Structure &middot; 6%", "06/11",
         ("Support: ETL (29/10), Data Warehouses (05/11)", "Apoio: ETL (29/10), Data Warehouses (05/11)", "Appui : ETL (29/10), Data Warehouses (05/11)")),
        (("Information architecture and decision matrix", "Arquitetura da informação e matriz de decisão", "Architecture de l'information et matrice de décision"),
         "MAI-MD &middot; 4%", "06/11", None),
        (("Business and market questions", "Perguntas de negócio e de mercado", "Questions métier et marché"),
         "Business Question 1 &middot; 3%", "06/11",
         ("Support: Market intelligence (30/10), Competitive Analysis (04/11)", "Apoio: Market intelligence (30/10), Competitive Analysis (04/11)", "Appui : Market intelligence (30/10), Competitive Analysis (04/11)")),
        (("Mathematics: PCA, centroids, and relationships", "Matemática: PCA, centroides e relações", "Mathématiques : ACP, centroïdes et relations"),
         "Math Challenge 1 &middot; 4%", "06/11",
         ("Support: PCA (27/10), Relationships (28/10), Centroids (03/11)", "Apoio: PCA (27/10), Relationships (28/10), Centroids (03/11)", "Appui : PCA (27/10), Relationships (28/10), Centroids (03/11)")),
        (("Hierarchical classification and outcomes matrix", "Classificação hierárquica e matriz de resultados", "Classification hiérarchique et matrice des résultats"),
         "Graded Assignment &middot; 3%", "30/10", None),
        (("Work process and quality of delivery", "Processo de trabalho e qualidade da entrega", "Processus de travail et qualité de la livraison"),
         "Kanban + GitLab", L("Every day", "Todo dia", "Chaque jour"), None),
    ]
    trs = []
    for t, entrega, prazo, apoio in linhas:
        ap = f'<span class="apoio">{L(*apoio)}</span>' if apoio else ""
        trs.append(
            f'            <tr>\n              <th scope="row">{L(*t)}{ap}</th>\n'
            f'              <td>{entrega}</td>\n              <td class="data">{prazo}</td>\n            </tr>')
    return slide_conteudo(n, titulo, f"""        <table class="ref-tabela densa">
          <thead>
            <tr>
              <th>{L("Topic", "Tópico", "Sujet")}</th>
              <th>{L("Delivery it supports", "Entrega que sustenta", "Livrable qu'il soutient")}</th>
              <th>{L("Date", "Data", "Date")}</th>
            </tr>
          </thead>
          <tbody>
{chr(10).join(trs)}
          </tbody>
        </table>
{nota("Suggestion. Each group adjusts the topics, breaks them into tasks of 15 to 120 min, and records them in GitLab.",
      "Sugestão. Cada grupo ajusta os tópicos, divide em tarefas de 15 a 120 min e registra no GitLab.",
      "Suggestion. Chaque groupe ajuste les sujets, les découpe en tâches de 15 à 120 min et les enregistre dans GitLab.")}""")


def planning_hoje(n, grupos):
    tam = sorted({len(v) for v in grupos.values()})
    menor, maior = tam[0], tam[-1]
    titulo = L(f"Sprint 2 has {DIAS_DE_EXECUCAO} working days, and the planning closes today",
               f"A Sprint 2 tem {DIAS_DE_EXECUCAO} dias úteis, e o planejamento fecha hoje",
               f"Le sprint 2 compte {DIAS_DE_EXECUCAO} jours ouvrés, la planification se clôt aujourd'hui")
    passos = [
        ("Every sprint task is a card in GitLab, estimated as S, M, L, or XL (15 to 120 min).",
         "Toda tarefa da sprint é um card no GitLab, estimada em P, M, G ou GG (15 a 120 min).",
         "Chaque tâche du sprint est une carte dans GitLab, estimée en S, M, L ou XL (15 à 120 min)."),
        (f"At least {DIAS_DE_EXECUCAO} tasks per student, one per working day ({DIAS_DE_EXECUCAO * menor} to {DIAS_DE_EXECUCAO * maior} per group).",
         f"No mínimo {DIAS_DE_EXECUCAO} tarefas por aluno, uma por dia útil ({DIAS_DE_EXECUCAO * menor} a {DIAS_DE_EXECUCAO * maior} por grupo).",
         f"Au moins {DIAS_DE_EXECUCAO} tâches par étudiant, une par jour ouvré ({DIAS_DE_EXECUCAO * menor} à {DIAS_DE_EXECUCAO * maior} par groupe)."),
        ("Review time planned in each task, with a reviewer other than the author.",
         "Tempo de revisão planejado em cada tarefa, com revisor diferente do autor.",
         "Temps de revue planifié dans chaque tâche, avec un relecteur autre que l'auteur."),
        ("Scrum Master elected and WIP of 1 card in Doing per student.",
         "Scrum master eleito e WIP de 1 card em Doing por aluno.",
         "Scrum Master élu et WIP de 1 carte en Doing par étudiant."),
        ("Process document open as a merge request in the group repository.",
         "Documento de processo aberto como merge request no repositório do grupo.",
         "Document de processus ouvert en merge request dans le dépôt du groupe."),
    ]
    lis = "\n".join(f"          <li><span>{L(*p)}</span></li>" for p in passos)
    corpo = f"""        <ol class="passos compacta">
{lis}
        </ol>
{nota(f"{DIAS_DE_EXECUCAO} working days: 9 from 26/10 to 06/11 (02/11 is a holiday), minus the planning day and the review day.",
      f"{DIAS_DE_EXECUCAO} dias úteis: 9 de 26/10 a 06/11 (02/11 é feriado), menos o dia da planning e o da review.",
      f"{DIAS_DE_EXECUCAO} jours ouvrés : 9 du 26/10 au 06/11 (le 02/11 est férié), moins le jour du planning et celui de la review.")}
        <div class="aviso dica">
          <span class="material-symbols-outlined aviso-icone" aria-hidden="true">cake</span>
          <p>
            <strong>{L("Tip:", "Dica:", "Astuce :")}</strong>
            {L("Wednesday, 04/11, is the advisor's birthday. The presentation is due at 6 pm, and sending it early makes the celebration lighter.",
               "quarta-feira, 04/11, é aniversário do orientador. O envio da apresentação vence às 18h, e entregar cedo deixa a comemoração mais leve.",
               "le mercredi 04/11, c'est l'anniversaire de l'encadrant. La présentation est à rendre à 18 h, et l'envoyer tôt allège la fête.")}
          </p>
        </div>"""
    return slide_conteudo(n, titulo, corpo)


def arguicoes(n):
    titulo = L("Individual oral defenses of Sprint 1", "Arguições individuais da Sprint 1",
               "Soutenances individuelles du sprint 1")
    linhas = [
        (("Scheduling", "Agendamento", "Planification"),
         ("By the advisor, between today (26/10) and tomorrow (27/10)", "Pelo orientador, entre hoje (26/10) e amanhã (27/10)",
          "Par l'encadrant, entre aujourd'hui (26/10) et demain (27/10)")),
        (("Deadline", "Prazo final", "Date limite"),
         ("All defenses finished by Thursday, 29/10", "Todas as arguições concluídas até quinta-feira, 29/10",
          "Toutes les soutenances terminées d'ici jeudi 29/10")),
        (("Weight", "Peso", "Poids"),
         ("60% of the individual assessment; the other 40% is the use of Kanban and GitLab",
          "60% da avaliação individual; os outros 40% são o uso do Kanban e do GitLab",
          "60 % de l'évaluation individuelle ; les 40 % restants portent sur l'usage de Kanban et GitLab")),
    ]
    trs = "\n".join(
        f'            <tr>\n              <th scope="row">{L(*a)}</th>\n              <td>{L(*b)}</td>\n            </tr>'
        for a, b in linhas)
    corpo = f"""        <table class="ref-tabela grande enorme">
          <tbody>
{trs}
          </tbody>
        </table>"""
    return slide_conteudo(n, titulo, corpo)


def encerramento():
    return f"""      <!-- Encerramento -->
      <section class="end-slide">
        <img class="inteli-logo-header" src="../assets/img/inteli-logo-negativa.svg" alt="Inteli">
        <div class="end-accent"></div>
        <h1>
          {L("Questions", "Dúvidas", "Questions")}
        </h1>
        <h3>
          {L("Sprint Planning 2", "Sprint Planning 2", "Sprint Planning 2")}
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
    m, ativ, trad, grupos = carregar()
    slides = []
    ids = {g["grupo"]: g["grupo"].lower() for g in m["grupos"]}

    def pos():
        return len(slides) + 1

    slides.append(capa())
    slides.append(agenda(pos()))
    slides.append(secao(pos(), ("Part A", "Parte A", "Partie A"),
                        ("Sprint 1 in numbers", "Sprint 1 em números", "Le sprint 1 en chiffres"),
                        ("GitLab data from 14/10 to 23/10", "Dados do GitLab de 14/10 a 23/10",
                         "Données GitLab du 14/10 au 23/10")))
    slides.append(numeros_grandes(pos(), m))
    slides.append(tabela_grupos(pos(), m, ids))
    for g in m["grupos"]:
        slides.append(slide_grupo_commits(pos(), g, ids[g["grupo"]]))
        slides.append(slide_grupo_fluxo(pos(), g, ids[g["grupo"]] + "-fluxo"))
    slides.append(processo_atividade(pos()))
    slides.append(processo_conteudo(pos()))
    slides.append(secao(pos(), ("Part B", "Parte B", "Partie B"),
                        ("Sprint 2", "Sprint 2", "Sprint 2"),
                        ("Artifacts, calendar, and planning", "Artefatos, calendário e planejamento",
                         "Livrables, calendrier et planification")))
    slides.append(semana3(pos()))
    slides.append(semana4(pos()))
    slides.append(entregas(pos(), ativ, trad))
    slides.append(topicos(pos()))
    slides.append(planning_hoje(pos(), grupos))
    slides.append(arguicoes(pos()))
    slides.append(encerramento())

    html = f"""<!doctype html>
<html lang="en" data-lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sprint Planning 2 &middot; SI08 T18</title>

  <!-- Gerado por tools/gerar_sprint_planning.py (nao editar a mao). Retrospectiva
       da Sprint 1 a partir de dados/metricas_sprint1.json (tools/coletar_gitlab.py)
       e plano da Sprint 2. Deck trilingue (ADR-001); metricas por grupo, sem
       nomes de alunos (ADR-005). -->

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
    return html


if __name__ == "__main__":
    saida = gerar()
    SAIDA.write_text(saida, encoding="utf-8")
    print(f"gravado {SAIDA} ({saida.count('<section')} slides)")
