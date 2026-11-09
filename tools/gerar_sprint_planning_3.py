#!/usr/bin/env python3
"""Gera aulas/sprint-planning-3.html (Sprint Planning 3, 09/11/2026, 14h, 2h).

Entradas:
    dados/atividades_ponderadas.csv    (tools/extrair_lbl.py)
    dados/traducoes_atividades.csv
    dados/grupos.js

Uso:
    python3 tools/gerar_sprint_planning_3.py

Deck trilingue (ADR-001), com os helpers de tools/gerar_sprint_planning.py. O quadro de
post-its da Parte A e a pagina quadro/reflexao-sprint2.html (ADR-006). Datas e pesos da
Sprint 3 vem da Adalove (export e consulta pelo MCP em 09/11/2026); os avisos e os
horarios da validacao previa vem do orientador.
"""
from pathlib import Path

import gerar_sprint_planning as base
from gerar_sprint_planning import (L, LEGENDA, cab, dia, evento, evento_nome, nota, secao,
                                   slide_conteudo)

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "aulas" / "sprint-planning-3.html"
RODAPE = "SI08 &middot; T18 &middot; Sprint Planning 3"
QUADRO = "../quadro/reflexao-sprint2.html"

# Perguntas do quadro: as mesmas de assets/js/reflexao.js (o teste confere).
PERGUNTAS = [
    ("What was the goal of Sprint 2, in one sentence? Write it without asking your teammates.",
     "Qual era o objetivo da Sprint 2, em uma frase? Escreva sem consultar os colegas.",
     "Quel était l’objectif du sprint 2, en une phrase ? Écrivez-le sans consulter vos collègues."),
    ("What did you personally deliver in Sprint 2? Cite the issue or merge request in GitLab.",
     "O que você entregou na Sprint 2? Cite a issue ou o merge request no GitLab.",
     "Qu’avez-vous livré personnellement au sprint 2 ? Citez l’issue ou la merge request dans GitLab."),
    ("Who decided to make a single presentation for Sprint Review 2, when, and were you consulted?",
     "Quem decidiu fazer uma apresentação única na Sprint Review 2, quando, e você foi consultado?",
     "Qui a décidé de faire une présentation unique à la Sprint Review 2, quand, et avez-vous été consulté ?"),
    ("Were the risks of that decision (delay, long presentation, failed demo) in the risk matrix? What was the mitigation?",
     "Os riscos dessa decisão (atraso, apresentação longa, falha na demonstração) estavam na matriz de risco? Qual era a mitigação?",
     "Les risques de cette décision (retard, présentation longue, démo ratée) figuraient-ils dans la matrice des risques ? Quelle était la mitigation ?"),
    ("What will you do differently in Sprint 3, starting tomorrow? Write one commitment someone can check.",
     "O que você vai fazer diferente na Sprint 3, a partir de amanhã? Escreva um compromisso que alguém possa verificar.",
     "Que ferez-vous différemment au sprint 3, dès demain ? Écrivez un engagement vérifiable."),
]

# Roteiro do encontro: (inicio, fim, bloco, o que o aluno faz). Soma 120 min.
ROTEIRO = [
    ("14:00", "14:05", ("Opening and agenda", "Abertura e agenda", "Ouverture et ordre du jour"),
     ("Listens", "Escuta", "Écoute")),
    ("14:05", "14:25", ("A. Sprint 2 reflection board", "A. Quadro de reflexão da Sprint 2", "A. Tableau de réflexion du sprint 2"),
     ("Answers 5 questions in post-its, alone", "Responde 5 perguntas em post-its, sozinho", "Répond à 5 questions en post-it, seul")),
    ("14:25", "14:35", ("Reading the board and the risk matrix", "Leitura do quadro e matriz de risco", "Lecture du tableau et matrice des risques"),
     ("Discusses with the class", "Discute com a turma", "Discute avec la classe")),
    ("14:35", "14:45", ("B. Academic and executive presentations", "B. Apresentação acadêmica e executiva", "B. Présentation académique et exécutive"),
     ("Listens and asks", "Escuta e pergunta", "Écoute et pose des questions")),
    ("14:45", "15:00", ("Rebuilding the Sprint 2 presentation", "Reconstrução da apresentação da Sprint 2", "Reconstruction de la présentation du sprint 2"),
     ("Builds slides with the whole group", "Monta os slides com o grupo inteiro", "Construit les slides avec tout le groupe")),
    ("15:00", "15:25", ("Presentations, 5 min per group", "Apresentações, 5 min por grupo", "Présentations, 5 min par groupe"),
     ("2 drawn members present and demo", "2 sorteados apresentam e demonstram", "2 tirés au sort présentent et font la démo")),
    ("15:25", "15:35", ("C. Situational leadership", "C. Liderança situacional", "C. Leadership situationnel"),
     ("Listens and asks", "Escuta e pergunta", "Écoute et pose des questions")),
    ("15:35", "15:45", ("D. Sprint 3: planning, daily, and notices", "D. Sprint 3: planning, daily e avisos", "D. Sprint 3 : planning, daily et avis"),
     ("Reads the group's planning", "Lê a planning do grupo", "Lit le planning du groupe")),
    ("15:45", "16:00", ("Backlog onto the board", "Backlog no board", "Backlog dans le tableau"),
     ("Reviews tasks and creates the cards", "Revisa as tarefas e cria os cards", "Revoit les tâches et crée les cartes")),
]


def _min(h):
    hh, mm = h.split(":")
    return int(hh) * 60 + int(mm)


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
              {L("Sprint Planning 3", "Sprint Planning 3", "Sprint Planning 3")}
            </h1>
            <h3>
              {L("Sprint 2 review and Sprint 3 plan", "Revisão da Sprint 2 e plano da Sprint 3", "Revue du sprint 2 et plan du sprint 3")}
            </h3>
          </div>
        </div>
      </section>
"""


def agenda(n):
    total = sum(_min(f) - _min(i) for i, f, _, _ in ROTEIRO)
    assert total == 120, total
    trs = "\n".join(
        f'            <tr>\n              <td class="data">{i}&ndash;{f}</td>\n'
        f'              <th scope="row">{L(*b)}</th>\n              <td>{L(*a)}</td>\n            </tr>'
        for i, f, b, a in ROTEIRO)
    corpo = f"""        <table class="ref-tabela densa">
          <thead>
            <tr>
              <th>{L("Time", "Horário", "Horaire")}</th>
              <th>{L("Block", "Bloco", "Bloc")}</th>
              <th>{L("What the student does", "O que o aluno faz", "Ce que fait l'étudiant")}</th>
            </tr>
          </thead>
          <tbody>
{trs}
          </tbody>
        </table>"""
    return slide_conteudo(n, L("Agenda for today, 14:00 to 16:00", "Agenda de hoje, 14h às 16h",
                               "Ordre du jour, 14 h à 16 h"), corpo, id_="agenda")


def review2(n):
    titulo = L("Sprint Review 2 took 1h30 in a single presentation of more than 50 slides",
               "A Sprint Review 2 durou 1h30 em uma apresentação única de mais de 50 slides",
               "La Sprint Review 2 a duré 1 h 30 en une présentation unique de plus de 50 slides")
    linhas = [
        (("Delivery of the slides", "Entrega dos slides", "Envoi des slides"),
         ("Wednesday 04/11, 6 pm", "Quarta-feira 04/11, 18h", "Mercredi 04/11, 18 h"),
         ("Not delivered in advance", "Não entregues antes", "Pas envoyés à l'avance")),
        (("Format", "Formato", "Format"),
         ("One presentation per group", "Uma apresentação por grupo", "Une présentation par groupe"),
         ("One presentation for the whole class, decided by the students", "Uma apresentação da turma inteira, decidida pelos alunos",
          "Une présentation pour toute la classe, décidée par les étudiants")),
        (("Size and duration", "Tamanho e duração", "Taille et durée"),
         ("Short, with a demonstration", "Curta, com demonstração", "Courte, avec démonstration"),
         ("More than 50 slides and 1h30", "Mais de 50 slides e 1h30", "Plus de 50 slides et 1 h 30")),
    ]
    trs = "\n".join(
        f'            <tr>\n              <th scope="row">{L(*a)}</th>\n              <td>{L(*b)}</td>\n'
        f'              <td class="destaque">{L(*c)}</td>\n            </tr>' for a, b, c in linhas)
    corpo = f"""        <table class="ref-tabela grande">
          <thead>
            <tr>
              <th>{L("Item", "Item", "Élément")}</th>
              <th>{L("Agreed in Sprint Planning 2", "Combinado na Sprint Planning 2", "Convenu au Sprint Planning 2")}</th>
              <th>{L("What happened", "O que aconteceu", "Ce qui s'est passé")}</th>
            </tr>
          </thead>
          <tbody>
{trs}
          </tbody>
        </table>
{nota("Source: Sprint Planning 2 calendar and the advisor's record of Sprint Review 2 (06/11).",
      "Fonte: calendário da Sprint Planning 2 e registro do orientador da Sprint Review 2 (06/11).",
      "Source : calendrier du Sprint Planning 2 et notes de l'encadrant sur la Sprint Review 2 (06/11).")}"""
    return slide_conteudo(n, titulo, corpo)


def atividade_quadro(n):
    titulo = L("Activity: each member answers the Sprint 2 board alone, in 20 minutes",
               "Atividade: cada integrante responde sozinho o quadro da Sprint 2, em 20 minutos",
               "Activité : chaque membre répond seul au tableau du sprint 2, en 20 minutes")
    passos = [
        ("Open the link of your group's board, posted in the group's Slack channel.",
         "Abrir o link do quadro do grupo, enviado no canal do grupo no Slack.",
         "Ouvrir le lien du tableau du groupe, envoyé sur le canal Slack du groupe."),
        ("Choose your name. Your post-its are signed and the advisor sees who wrote each one.",
         "Escolher o próprio nome. Os post-its saem assinados e o orientador vê quem escreveu cada um.",
         "Choisir son nom. Les post-it sont signés et l'encadrant voit qui a écrit chacun."),
        ("Write at least one post-it for each of the 5 questions, without talking to the group.",
         "Escrever pelo menos um post-it em cada uma das 5 perguntas, sem conversar com o grupo.",
         "Écrire au moins un post-it pour chacune des 5 questions, sans parler au groupe."),
        ("Read your teammates' post-its when the time is up, not before.",
         "Ler os post-its dos colegas quando o tempo acabar, e não antes.",
         "Lire les post-it des collègues quand le temps est écoulé, pas avant."),
    ]
    lis = "\n".join(f"          <li><span>{L(*p)}</span></li>" for p in passos)
    corpo = f"""        <ol class="passos">
{lis}
        </ol>
{nota("Delivery: at least 5 signed post-its per student on the group's board, by 14:25.",
      "Entrega: no mínimo 5 post-its assinados por aluno no quadro do grupo, até 14h25.",
      "Livrable : au moins 5 post-it signés par étudiant sur le tableau du groupe, avant 14 h 25.",
      atalhos=f'<a href="{QUADRO}?painel=1" target="_blank" rel="noopener">' + L("Advisor's panel", "Painel do orientador", "Panneau de l'encadrant") + "</a>")}"""
    return slide_conteudo(n, titulo, corpo, id_="quadro")


def perguntas(n):
    trs = "\n".join(
        f'            <tr>\n              <td class="data">{i}</td>\n              <td>{L(*q)}</td>\n            </tr>'
        for i, q in enumerate(PERGUNTAS, 1))
    corpo = f"""        <table class="ref-tabela grande">
          <tbody>
{trs}
          </tbody>
        </table>"""
    return slide_conteudo(n, L("Questions on the reflection board", "Perguntas do quadro de reflexão",
                               "Questions du tableau de réflexion"), corpo)


def matriz_risco(n):
    titulo = L("Risk matrix applied to the single-presentation decision",
               "Matriz de risco aplicada à decisão da apresentação única",
               "Matrice des risques appliquée à la décision de présentation unique")
    linhas = [
        (("Consolidating 5 groups' slides runs late", "Consolidar os slides de 5 grupos atrasa", "La consolidation des slides des 5 groupes prend du retard"),
         ("Internal deadline 24 h before the review, with one owner of the file", "Prazo interno 24h antes da review, com um dono do arquivo", "Délai interne 24 h avant la review, avec un responsable du fichier")),
        (("The presentation exceeds the time box", "A apresentação passa do tempo", "La présentation dépasse le temps prévu"),
         ("Fixed time per group and a member keeping time", "Tempo fixo por grupo e um integrante cronometrando", "Temps fixe par groupe et un membre chronométreur")),
        (("The live demonstration fails", "A demonstração ao vivo falha", "La démonstration en direct échoue"),
         ("Recorded video of the demo as plan B", "Vídeo gravado da demonstração como plano B", "Vidéo enregistrée de la démo comme plan B")),
        (("A group's content depends on another group", "O conteúdo de um grupo depende de outro grupo", "Le contenu d'un groupe dépend d'un autre groupe"),
         ("Each group presents its own increment", "Cada grupo apresenta o próprio incremento", "Chaque groupe présente son propre incrément")),
    ]
    trs = "\n".join(
        f'            <tr>\n              <th scope="row">{L(*r)}</th>\n              <td>{L(*m)}</td>\n'
        f'              <td class="data">?</td>\n              <td class="data">?</td>\n            </tr>'
        for r, m in linhas)
    corpo = f"""        <table class="ref-tabela densa">
          <thead>
            <tr>
              <th>{L("Risk", "Risco", "Risque")}</th>
              <th>{L("Mitigation that was available", "Mitigação que estava disponível", "Mitigation qui était disponible")}</th>
              <th>{L("Mapped?", "Mapeado?", "Identifié ?")}</th>
              <th>{L("Owner?", "Dono?", "Responsable ?")}</th>
            </tr>
          </thead>
          <tbody>
{trs}
          </tbody>
        </table>
        <div class="aviso">
          <span class="material-symbols-outlined aviso-icone" aria-hidden="true">forum</span>
          <p>
            <strong>{L("For discussion:", "Para discussão:", "Pour discussion :")}</strong>
            {L("which of these risks was in your group's matrix from Sprint 1, and who would have triggered the mitigation?",
               "qual destes riscos estava na matriz do grupo desde a Sprint 1, e quem acionaria a mitigação?",
               "lequel de ces risques figurait dans la matrice du groupe depuis le sprint 1, et qui aurait déclenché la mitigation ?")}
          </p>
        </div>"""
    return slide_conteudo(n, titulo, corpo, id_="risco")


def academica_executiva(n):
    titulo = L("Academic and executive presentations differ in order, time, and purpose",
               "Apresentação acadêmica e executiva diferem em ordem, tempo e propósito",
               "Présentations académique et exécutive diffèrent par l'ordre, le temps et le but")
    linhas = [
        (("Purpose", "Propósito", "But"),
         ("Show method and rigor", "Mostrar método e rigor", "Montrer la méthode et la rigueur"),
         ("Support a decision", "Apoiar uma decisão", "Appuyer une décision")),
        (("Order", "Ordem", "Ordre"),
         ("Context, method, results, conclusion", "Contexto, método, resultados, conclusão", "Contexte, méthode, résultats, conclusion"),
         ("Conclusion first, then evidence", "Conclusão primeiro, depois a evidência", "Conclusion d'abord, puis les preuves")),
        (("Audience", "Público", "Public"),
         ("Examining board", "Banca avaliadora", "Jury"),
         ("Partner, manager, product owner", "Parceiro, gestor, product owner", "Partenaire, manager, product owner")),
        (("Time", "Tempo", "Temps"),
         ("Long, follows the content", "Longo, acompanha o conteúdo", "Long, suit le contenu"),
         ("Fixed and short; content fits the time", "Fixo e curto; o conteúdo cabe no tempo", "Fixe et court ; le contenu tient dans le temps")),
        (("Slide title", "Título do slide", "Titre du slide"),
         ("Topic name", "Nome do tema", "Nom du thème"),
         ("Sentence with the finding and the number", "Frase com o achado e o número", "Phrase avec le constat et le chiffre")),
        (("Success measure", "Medida de sucesso", "Mesure de succès"),
         ("Reproducibility", "Reprodutibilidade", "Reproductibilité"),
         ("A decision taken at the end", "Uma decisão tomada no fim", "Une décision prise à la fin")),
    ]
    trs = "\n".join(
        f'            <tr>\n              <th scope="row">{L(*a)}</th>\n              <td>{L(*b)}</td>\n              <td>{L(*c)}</td>\n            </tr>'
        for a, b, c in linhas)
    corpo = f"""        <table class="ref-tabela">
          <thead>
            <tr>
              <th>{L("Criterion", "Critério", "Critère")}</th>
              <th>{L("Academic", "Acadêmica", "Académique")}</th>
              <th>{L("Executive", "Executiva", "Exécutive")}</th>
            </tr>
          </thead>
          <tbody>
{trs}
          </tbody>
        </table>
{nota("The Sprint Review is an executive presentation: the partner decides what to accept.",
      "A Sprint Review é uma apresentação executiva: o parceiro decide o que aceita.",
      "La Sprint Review est une présentation exécutive : le partenaire décide ce qu'il accepte.")}"""
    return slide_conteudo(n, titulo, corpo)


ESTRUTURA = [
    ("Agenda", "Agenda", "Ordre du jour", 15,
     ("Sections and time of each", "Seções e tempo de cada uma", "Sections et temps de chacune")),
    ("Sprint goal", "Objetivo da sprint", "Objectif du sprint", 30,
     ("Goal of the sprint that ended and of the sprint that starts, one sentence each",
      "Objetivo da sprint que terminou e da que começa, uma frase cada",
      "Objectif du sprint terminé et de celui qui commence, une phrase chacun")),
    ("Status report", "Status report", "Status report", 45,
     ("Planned versus delivered, per board item, with the percentage done",
      "Planejado versus entregue, por item do board, com o percentual concluído",
      "Prévu par rapport au livré, par élément du tableau, avec le pourcentage réalisé")),
    ("Sprint increment", "Incremento da sprint", "Incrément du sprint", 60,
     ("What was built to reach each feature, described in slides",
      "O que foi feito para chegar a cada feature, descrito em slides",
      "Ce qui a été fait pour atteindre chaque fonctionnalité, décrit en slides")),
    ("Demonstration", "Demonstração", "Démonstration", 90,
     ("The increment running, live; recorded video as plan B",
      "O incremento rodando, ao vivo; vídeo gravado como plano B",
      "L'incrément qui tourne, en direct ; vidéo enregistrée comme plan B")),
    ("Problems and risks", "Problemas e riscos", "Problèmes et risques", 45,
     ("What blocked the sprint and the risks for the next one, each with a mitigation and an owner",
      "O que travou a sprint e os riscos da próxima, cada um com mitigação e dono",
      "Ce qui a bloqué le sprint et les risques du suivant, chacun avec une mitigation et un responsable")),
    ("Questions", "Perguntas", "Questions", 15,
     ("Decisions the group needs from the partner", "Decisões que o grupo precisa do parceiro",
      "Décisions dont le groupe a besoin du partenaire")),
]


def estrutura(n):
    total = sum(e[3] for e in ESTRUTURA)
    assert total == 300, total
    titulo = L(f"The executive Sprint Review fits {len(ESTRUTURA)} sections in 5 minutes",
               f"A Sprint Review executiva cabe em {len(ESTRUTURA)} seções e 5 minutos",
               f"La Sprint Review exécutive tient en {len(ESTRUTURA)} sections et 5 minutes")
    trs = "\n".join(
        f'            <tr>\n              <td class="data">{i}</td>\n              <th scope="row">{L(en, pt, fr)}</th>\n'
        f'              <td>{L(*o)}</td>\n              <td class="peso">{s} s</td>\n            </tr>'
        for i, (en, pt, fr, s, o) in enumerate(ESTRUTURA, 1))
    corpo = f"""        <table class="ref-tabela densa">
          <thead>
            <tr>
              <th>#</th>
              <th>{L("Section", "Seção", "Section")}</th>
              <th>{L("Content", "Conteúdo", "Contenu")}</th>
              <th>{L("Time", "Tempo", "Temps")}</th>
            </tr>
          </thead>
          <tbody>
{trs}
          </tbody>
        </table>
{nota("One section per slide, except the increment, which may take one slide per feature. Maximum of 10 slides.",
      "Uma seção por slide, exceto o incremento, que pode ter um slide por feature. Máximo de 10 slides.",
      "Une section par slide, sauf l'incrément, qui peut avoir un slide par fonctionnalité. Maximum 10 slides.")}"""
    return slide_conteudo(n, titulo, corpo, id_="estrutura")


def atividade_reconstrucao(n):
    titulo = L("Activity: each group rebuilds its Sprint 2 presentation in 15 minutes",
               "Atividade: cada grupo reconstrói a apresentação da Sprint 2 em 15 minutos",
               "Activité : chaque groupe reconstruit sa présentation du sprint 2 en 15 minutes")
    passos = [
        ("Create one slide file per group and post the link in the group's Slack channel.",
         "Criar um arquivo de slides por grupo e enviar o link no canal do grupo no Slack.",
         "Créer un fichier de slides par groupe et envoyer le lien sur le canal Slack du groupe."),
        ("Follow the 7 executive sections, using only what the group delivered in Sprint 2.",
         "Seguir as 7 seções executivas, só com o que o grupo entregou na Sprint 2.",
         "Suivre les 7 sections exécutives, uniquement avec ce que le groupe a livré au sprint 2."),
        ("Every member edits at least one slide; the file history shows who did it.",
         "Todo integrante edita pelo menos um slide; o histórico do arquivo mostra quem fez.",
         "Chaque membre modifie au moins un slide ; l'historique du fichier montre qui l'a fait."),
        ("At 15:00 the advisor draws 2 members per group, who present for 5 minutes with a live demo.",
         "Às 15h o orientador sorteia 2 integrantes por grupo, que apresentam em 5 minutos com demonstração ao vivo.",
         "À 15 h l'encadrant tire au sort 2 membres par groupe, qui présentent en 5 minutes avec une démo en direct."),
    ]
    lis = "\n".join(f"          <li><span>{L(*p)}</span></li>" for p in passos)
    corpo = f"""        <ol class="passos">
{lis}
        </ol>
{nota("Delivery: link to the rebuilt presentation (maximum 10 slides) in the group's Slack channel, by 15:00.",
      "Entrega: link da apresentação reconstruída (máximo de 10 slides) no canal do grupo no Slack, até 15h.",
      "Livrable : lien de la présentation reconstruite (10 slides maximum) sur le canal Slack du groupe, avant 15 h.",
      atalhos='<a href="#/estrutura">' + L("See the 7 sections", "Ver as 7 seções", "Voir les 7 sections") + "</a>")}"""
    return slide_conteudo(n, titulo, corpo)


def _t(x, y, en, pt, fr, cls="", extra=""):
    """Texto do SVG nas tres linguas, agrupado para o seletor de idioma (ADR-001)."""
    c = f' class="{cls}"' if cls else ""
    return (f'<g{c}><text x="{x}" y="{y}"{extra} data-l="en">{en}</text>'
            f'<text x="{x}" y="{y}"{extra} data-l="pt">{pt}</text>'
            f'<text x="{x}" y="{y}"{extra} data-l="fr">{fr}</text></g>')


def figura_hersey_blanchard():
    """Modelo de Hersey e Blanchard redesenhado a partir da figura do artigo de Bassani (2021)."""
    # Area do grafico: x de 70 a 530, y de 20 a 330; meio em (300, 175).
    quad = [
        (185, 70, "E3", ("Participating", "Compartilhar", "Participer"),
         ("High relationship,", "Relacionamento alto,", "Relation forte,"), ("low task", "tarefa baixa", "tâche faible")),
        (415, 70, "E2", ("Selling", "Persuadir", "Persuader"),
         ("High task,", "Tarefa alta,", "Tâche forte,"), ("high relationship", "relacionamento alto", "relation forte")),
        (185, 225, "E4", ("Delegating", "Delegar", "Déléguer"),
         ("Low relationship,", "Relacionamento baixo,", "Relation faible,"), ("low task", "tarefa baixa", "tâche faible")),
        (415, 225, "E1", ("Telling", "Determinar", "Diriger"),
         ("High task,", "Tarefa alta,", "Tâche forte,"), ("low relationship", "relacionamento baixo", "relation faible")),
    ]
    partes = []
    for cx, y, cod, nome, d1, d2 in quad:
        partes.append(f'<text x="{cx}" y="{y + 34}" class="lid-cod">{cod}</text>')
        partes.append(_t(cx, y + 62, *nome, cls="lid-nome"))
        partes.append(_t(cx, y + 86, *d1, cls="lid-desc"))
        partes.append(_t(cx, y + 104, *d2, cls="lid-desc"))
    regua = [(127, "M4"), (242, "M3"), (357, "M2"), (472, "M1")]
    for x, m in regua:
        partes.append(f'<rect x="{x - 57}" y="380" width="115" height="34" class="lid-celula"/>')
        partes.append(f'<text x="{x}" y="403" class="lid-m">{m}</text>')
    return f"""<svg class="lid-figura" viewBox="0 0 560 470" role="img" aria-label="Hersey and Blanchard situational leadership model">
            <rect x="70" y="20" width="230" height="155" class="lid-q"/>
            <rect x="300" y="20" width="230" height="155" class="lid-q"/>
            <rect x="70" y="175" width="230" height="155" class="lid-q"/>
            <rect x="300" y="175" width="230" height="155" class="lid-q"/>
            <path d="M78,322 C150,318 190,60 300,40 C410,60 450,318 522,322" class="lid-curva"/>
            <line x1="70" y1="330" x2="70" y2="14" class="lid-eixo"/>
            <line x1="70" y1="330" x2="538" y2="330" class="lid-eixo"/>
            {"".join(partes)}
            {_t(28, 175, "Relationship behavior", "Comportamento de relacionamento", "Comportement relationnel", cls="lid-eixo-rot", extra=' transform="rotate(-90 28 175)"')}
            {_t(56, 30, "high", "alto", "fort", cls="lid-ext", extra=' transform="rotate(-90 56 30)"')}
            {_t(56, 318, "low", "baixo", "faible", cls="lid-ext", extra=' transform="rotate(-90 56 318)"')}
            {_t(300, 354, "Task behavior", "Comportamento de tarefa", "Comportement de tâche", cls="lid-eixo-rot")}
            {_t(86, 354, "low", "baixo", "faible", cls="lid-ext")}
            {_t(516, 354, "high", "alto", "fort", cls="lid-ext")}
            {_t(127, 374, "High", "Alta", "Élevée", cls="lid-faixa")}
            {_t(300, 374, "Moderate", "Moderada", "Modérée", cls="lid-faixa")}
            {_t(472, 374, "Low", "Baixa", "Faible", cls="lid-faixa")}
            {_t(300, 440, "Team maturity", "Maturidade da equipe", "Maturité de l'équipe", cls="lid-eixo-rot")}
            {_t(70, 440, "mature", "madura", "mature", cls="lid-ext")}
            {_t(530, 440, "immature", "imatura", "immature", cls="lid-ext")}
          </svg>"""


def lideranca(n):
    titulo = L("In situational leadership, the leader's style follows the team's maturity for the task",
               "Na liderança situacional, o estilo do líder acompanha a maturidade da equipe para a tarefa",
               "En leadership situationnel, le style du leader suit la maturité de l'équipe pour la tâche")
    linhas = [
        ("M1", ("Unable and unwilling or insecure", "Sem capacidade nem disposição, ou insegura", "Incapable et peu disposée ou hésitante"),
         "E1", ("Telling", "Determinar", "Diriger")),
        ("M2", ("Unable, but willing or confident", "Sem capacidade, mas com disposição ou confiança", "Incapable, mais volontaire ou confiante"),
         "E2", ("Selling", "Persuadir", "Persuader")),
        ("M3", ("Able, but unwilling or insecure", "Com capacidade, mas sem disposição ou insegura", "Capable, mais peu disposée ou hésitante"),
         "E3", ("Participating", "Compartilhar", "Participer")),
        ("M4", ("Able and willing (competent, secure)", "Capaz e disposta (competente e segura)", "Capable et volontaire (compétente, sûre)"),
         "E4", ("Delegating", "Delegar", "Déléguer")),
    ]
    trs = "\n".join(
        f'              <tr>\n                <td class="data">{m}</td>\n                <td>{L(*c)}</td>\n'
        f'                <th scope="row">{e} {L(*est)}</th>\n              </tr>'
        for m, c, e, est in linhas)
    corpo = f"""        <div class="lid-grade">
          {figura_hersey_blanchard()}
          <table class="ref-tabela densa">
            <thead>
              <tr>
                <th>{L("Maturity", "Maturidade", "Maturité")}</th>
                <th>{L("Team", "Equipe", "Équipe")}</th>
                <th>{L("Style", "Estilo", "Style")}</th>
              </tr>
            </thead>
            <tbody>
{trs}
            </tbody>
          </table>
        </div>
{nota("Redrawn from Hersey and Blanchard (1986), in Bassani (2021), figures 2 and 3. Maturity is the capacity to accept one's own duties and responsibilities, set goals, and carry out the tasks requested.",
      "Redesenhado de Hersey e Blanchard (1986), em Bassani (2021), figuras 2 e 3. Maturidade é a capacidade de aceitar as próprias incumbências e responsabilidades, estabelecer metas e exercer as tarefas solicitadas.",
      "Redessiné d'après Hersey et Blanchard (1986), dans Bassani (2021), figures 2 et 3. La maturité est la capacité d'accepter ses propres missions et responsabilités, de fixer des objectifs et d'exécuter les tâches demandées.")}"""
    return slide_conteudo(n, titulo, corpo, id_="lideranca")


def mudanca_estilo(n):
    titulo = L("From Sprint 3 on, the advisor moves from delegating to selling",
               "A partir da Sprint 3, a orientação passa do estilo delegar para o persuadir",
               "À partir du sprint 3, l'encadrement passe du style déléguer au style persuader")
    linhas = [
        (("Planning", "Planning", "Planning"),
         ("Built by each group", "Feita por cada grupo", "Fait par chaque groupe"),
         ("Delivered by the advisor, with tasks per group", "Entregue pelo orientador, com tarefas por grupo", "Remis par l'encadrant, avec des tâches par groupe")),
        (("Daily", "Daily", "Daily"),
         ("Free format", "Formato livre", "Format libre"),
         ("Recorded on Slack by the Scrum Master", "Registrada no Slack pelo scrum master", "Enregistrée sur Slack par le Scrum Master")),
        (("Presentation", "Apresentação", "Présentation"),
         ("Sent on Wednesday", "Enviada na quarta-feira", "Envoyée le mercredi"),
         ("Sent on Wednesday and validated in 30 min with the whole group", "Enviada na quarta e validada em 30 min com o grupo inteiro", "Envoyée le mercredi et validée en 30 min avec tout le groupe")),
        (("Presenters", "Apresentadores", "Présentateurs"),
         ("Chosen by the group", "Escolhidos pelo grupo", "Choisis par le groupe"),
         ("Chosen by the advisor on the morning of the review", "Escolhidos pelo orientador na manhã da review", "Choisis par l'encadrant le matin de la review")),
    ]
    trs = "\n".join(
        f'            <tr>\n              <th scope="row">{L(*a)}</th>\n              <td>{L(*b)}</td>\n              <td class="destaque">{L(*c)}</td>\n            </tr>'
        for a, b, c in linhas)
    corpo = f"""        <table class="ref-tabela grande">
          <thead>
            <tr>
              <th>{L("Practice", "Prática", "Pratique")}</th>
              <th>{L("Sprints 1 and 2", "Sprints 1 e 2", "Sprints 1 et 2")}</th>
              <th>{L("Sprint 3", "Sprint 3", "Sprint 3")}</th>
            </tr>
          </thead>
          <tbody>
{trs}
          </tbody>
        </table>
{nota("The autonomy given in Sprints 1 and 2 was not matched by the same level of commitment and responsibility. The return to delegating depends on Sprint 3 deliveries on time.",
      "A autonomia dada nas Sprints 1 e 2 não teve contrapartida no mesmo nível de empenho e responsabilidade. A volta ao estilo delegar depende das entregas da Sprint 3 no prazo.",
      "L'autonomie donnée aux sprints 1 et 2 n'a pas eu de contrepartie au même niveau d'engagement et de responsabilité. Le retour au style déléguer dépend des livraisons du sprint 3 dans les délais.")}"""
    return slide_conteudo(n, titulo, corpo)


def leitura(n):
    titulo = L("Reading for the week: situational leadership", "Leitura da semana: liderança situacional",
               "Lecture de la semaine : leadership situationnel")
    corpo = f"""        <table class="ref-tabela grande enorme">
          <tbody>
            <tr>
              <th scope="row">{L("Article", "Artigo", "Article")}</th>
              <td>{L("Bassani, E. V. T. Situational leadership and its impacts on organizations. REFAQI, special issue, 2021.", "Bassani, E. V. T. Liderança situacional e seus impactos para as organizações. REFAQI, edição especial, 2021.", "Bassani, E. V. T. Le leadership situationnel et ses impacts sur les organisations. REFAQI, numéro spécial, 2021.")}</td>
            </tr>
            <tr>
              <th scope="row">{L("Where", "Onde", "Où")}</th>
              <td>{L("PDF in the class Slack channel, #2026-2b-t18", "PDF no canal da turma no Slack, #2026-2b-t18", "PDF sur le canal Slack de la classe, #2026-2b-t18")}</td>
            </tr>
            <tr>
              <th scope="row">{L("Focus", "Foco", "À lire")}</th>
              <td>{L("Sections 3 and 4: the four styles and maturity", "Seções 3 e 4: os quatro estilos e a maturidade", "Sections 3 et 4 : les quatre styles et la maturité")}</td>
            </tr>
          </tbody>
        </table>"""
    return slide_conteudo(n, titulo, corpo)


def semana5(n):
    titulo = L("Calendar of week 5, 09/11 to 13/11", "Calendário da semana 5, 09/11 a 13/11",
               "Calendrier de la semaine 5, du 09/11 au 13/11")
    dias = [
        dia(cab("Mon", "Seg", "Lun.", "09/11"), [
            evento("marco", "Sprint 3 planning, today", "Planning da Sprint 3, hoje", "Planning du sprint 3, aujourd'hui"),
            evento("marco", "Artificial assessment opens, 4 pm", "Avaliação artificial abre, 16h", "Évaluation artificielle ouverte, 16 h")], "hoje"),
        dia(cab("Tue", "Ter", "Mar.", "10/11"), [evento_nome("aula", "Data Cubes and Data Marts")]),
        dia(cab("Wed", "Qua", "Mer.", "11/11"), [evento_nome("aula", "Relationships and hierarchies")]),
        dia(cab("Thu", "Qui", "Jeu.", "12/11"), [
            evento_nome("aula", "Data Visualization"),
            evento("marco", "Artificial assessment closes, 11:59 pm", "Avaliação artificial fecha, 23h59", "Évaluation artificielle fermée, 23 h 59")]),
        dia(cab("Fri", "Sex", "Ven.", "13/11"), [
            evento("marco", "Project follow-up", "Acompanhamento do projeto", "Suivi du projet"),
            evento_nome("entrega", "Who Decides What?", 3)]),
    ]
    corpo = f"""        <div class="semana">
{chr(10).join(dias)}
        </div>
{LEGENDA}"""
    return slide_conteudo(n, titulo, corpo, id_="semana5")


def semana6(n):
    titulo = L("Calendar of week 6, 16/11 to 20/11", "Calendário da semana 6, 16/11 a 20/11",
               "Calendrier de la semaine 6, du 16/11 au 20/11")
    dias = [
        dia(cab("Mon", "Seg", "Lun.", "16/11"), [evento_nome("aula", "Digital Transformation")]),
        dia(cab("Tue", "Ter", "Mar.", "17/11"), [evento_nome("aula", "Predictive Models")]),
        dia(cab("Wed", "Qua", "Mer.", "18/11"), [
            evento_nome("aula", "Phygital and Omnichannel"),
            evento("marco", "Presentation delivered", "Apresentação entregue", "Présentation remise"),
            evento("marco", "Pre-validation, 30 min per group", "Validação prévia, 30 min por grupo", "Prévalidation, 30 min par groupe")]),
        dia(cab("Thu", "Qui", "Jeu.", "19/11"), [
            evento("marco", "Sprint Review 3, morning", "Sprint Review 3, manhã", "Sprint Review 3, matin")]),
        dia(cab("Fri", "Sex", "Ven.", "20/11"), [
            evento("marco", "Holiday: Black Consciousness Day", "Feriado: Consciência Negra", "Jour férié : Conscience noire"),
            evento_nome("entrega", "Automated Data Cube", 7)], "feriado"),
    ]
    corpo = f"""        <div class="semana">
{chr(10).join(dias)}
        </div>
{LEGENDA}"""
    return slide_conteudo(n, titulo, corpo, id_="semana6")


def entregas(n, ativ, trad):
    s3 = [a for a in ativ if a["sprint"] == "3"]
    soma = sum(float(a["peso"]) for a in s3)
    assert soma == 10.0, soma
    titulo = L(f"Sprint 3 holds {int(soma)}% of the module weight in {len(s3)} deliveries",
               f"A Sprint 3 reúne {int(soma)}% do peso do módulo em {len(s3)} entregas",
               f"Le sprint 3 réunit {int(soma)} % du poids du module en {len(s3)} livrables")
    quando = {
        "Graded Activity: Who Decides What? Group Power and Decision Mapping":
            ("13/11", ("Graded activity done in class, individual and handwritten",
                       "Atividade ponderada feita em aula, individual e manuscrita",
                       "Activité notée réalisée en cours, individuelle et manuscrite")),
        "Automated Data Cube":
            ("20/11", ("Group artifact on main; demonstrated at Sprint Review 3 on 19/11",
                       "Artefato do grupo na main; demonstrado na Sprint Review 3 em 19/11",
                       "Livrable du groupe sur main ; démontré à la Sprint Review 3 le 19/11")),
    }
    linhas = []
    for a in sorted(s3, key=lambda x: quando[x["nome"]][0][::-1]):
        t = trad[a["nome"]]
        data, obs = quando[a["nome"]]
        linhas.append(
            f'            <tr>\n              <td class="data">{data}</td>\n'
            f'              <td><span data-l="en">{a["nome"]}</span><span data-l="pt">{t["pt"]}</span><span data-l="fr">{t["fr"]}</span>\n'
            f'              <span class="apoio">{L(*obs)}</span></td>\n'
            f'              <td class="peso">{int(float(a["peso"]))}%</td>\n            </tr>')
    corpo = f"""        <table class="ref-tabela grande">
          <thead>
            <tr>
              <th>{L("Date", "Data", "Date")}</th>
              <th>{L("Delivery", "Entrega", "Livrable")}</th>
              <th>{L("Weight", "Peso", "Poids")}</th>
            </tr>
          </thead>
          <tbody>
{chr(10).join(linhas)}
          </tbody>
        </table>
{nota("Weights from the module plan in Adalove, checked on 09/11.",
      "Pesos do plano do módulo na Adalove, conferidos em 09/11.",
      "Poids du plan du module dans Adalove, vérifiés le 09/11.")}"""
    return slide_conteudo(n, titulo, corpo)


def cubo(n):
    titulo = L("Checklist of the Automated Data Cube artifact", "Checklist do artefato Automated Data Cube",
               "Checklist du livrable Automated Data Cube")
    linhas = [
        (("Dimensional model", "Modelagem dimensional", "Modélisation dimensionnelle"),
         ("Fact table (grain, metrics, keys), dimensions, star or snowflake with justification, diagram",
          "Tabela fato (granularidade, métricas, chaves), dimensões, estrela ou floco de neve com justificativa, diagrama",
          "Table de faits (granularité, mesures, clés), dimensions, étoile ou flocon justifié, diagramme")),
        (("ClickHouse views", "Views no ClickHouse", "Vues ClickHouse"),
         ("Fact and dimension views built only from the raw JSON ingestion table, with JSON extraction and CAST; SQL in the repository",
          "Views de fato e dimensão criadas só a partir da tabela bruta de ingestão em JSON, com extração JSON e CAST; SQL no repositório",
          "Vues de faits et de dimensions construites uniquement à partir de la table brute JSON, avec extraction JSON et CAST ; SQL dans le dépôt")),
        (("Documentation", "Documentação", "Documentation"),
         ("Model rationale, parsing and CAST strategy, how views are derived, how to run and validate, limitations",
          "Racional do modelo, estratégia de parsing e CAST, derivação das views, como executar e validar, limitações",
          "Justification du modèle, stratégie de parsing et CAST, dérivation des vues, exécution et validation, limites")),
        (("Assessment", "Avaliação", "Évaluation"),
         ("Dimensions relevant to the dataApp, correct views, coherent model, clear documentation",
          "Dimensões relevantes para o dataApp, views corretas, modelo coerente, documentação clara",
          "Dimensions pertinentes pour la dataApp, vues correctes, modèle cohérent, documentation claire")),
    ]
    trs = "\n".join(
        f'            <tr>\n              <th scope="row">{L(*a)}</th>\n              <td>{L(*b)}</td>\n            </tr>'
        for a, b in linhas)
    corpo = f"""        <table class="ref-tabela densa">
          <tbody>
{trs}
          </tbody>
        </table>
{nota("Source: Automated Data Cube activity in Adalove (week 6, weight 7%).",
      "Fonte: atividade Automated Data Cube na Adalove (semana 6, peso 7%).",
      "Source : activité Automated Data Cube dans Adalove (semaine 6, poids 7 %).")}"""
    return slide_conteudo(n, titulo, corpo, id_="cubo")


def planning_entregue(n):
    titulo = L("Each group receives its Sprint 3 planning ready, as a file published in the module portal",
               "Cada grupo recebe a planning da Sprint 3 pronta, em arquivo publicado no portal do módulo",
               "Chaque groupe reçoit son planning du sprint 3 prêt, en fichier publié sur le portail du module")
    passos = [
        ("The file <code>planning-sprint3-GXX.md</code>, in English, starts from the group's board and repository and lists the tasks, sizes, dependencies, and Definition of Done.",
         "O arquivo <code>planning-sprint3-GXX.md</code>, em inglês, parte do board e do repositório do grupo e lista as tarefas, tamanhos, dependências e Definition of Done.",
         "Le fichier <code>planning-sprint3-GXX.md</code>, en anglais, part du tableau et du dépôt du groupe et liste les tâches, tailles, dépendances et la Definition of Done."),
        ("Every task gets exactly one owner today; nobody keeps more than 1 card in Doing.",
         "Toda tarefa recebe exatamente um dono hoje; ninguém fica com mais de 1 card em Doing.",
         "Chaque tâche reçoit exactement un responsable aujourd'hui ; personne n'a plus d'une carte en Doing."),
        ("Changing, splitting, or dropping a task requires the advisor's approval on Slack.",
         "Trocar, dividir ou retirar uma tarefa exige aprovação do orientador no Slack.",
         "Changer, découper ou retirer une tâche exige l'accord de l'encadrant sur Slack."),
        ("The board is the source of truth: a task outside the board does not count as delivered.",
         "O board é a fonte da verdade: tarefa fora do board não conta como entregue.",
         "Le tableau fait foi : une tâche hors du tableau ne compte pas comme livrée."),
    ]
    lis = "\n".join(f"          <li><span>{L(*p)}</span></li>" for p in passos)
    base_url = "https://github.com/josercf/2026-2B-SI08-T18/blob/main/planning/sprint3/planning-sprint3-"
    links = " &middot; ".join(f'<a href="{base_url}{g}.md" target="_blank" rel="noopener">{g}</a>'
                              for g in ("G01", "G02", "G03", "G04", "G05"))
    corpo = f"""        <ol class="passos compacta">
{lis}
        </ol>
{nota("Planning per group:", "Planning por grupo:", "Planning par groupe :", atalhos=links)}"""
    return slide_conteudo(n, titulo, corpo, id_="planning")


def daily(n):
    titulo = L("The daily is recorded on Slack every working day, under the Scrum Master",
               "A daily é registrada no Slack todo dia útil, sob responsabilidade do scrum master",
               "Le daily est enregistré sur Slack chaque jour ouvré, sous la responsabilité du Scrum Master")
    linhas = [
        (("Where", "Onde", "Où"),
         ("Thread opened by the Scrum Master in the group's channel, #2026-2b-t18-grupoXX",
          "Thread aberta pelo scrum master no canal do grupo, #2026-2b-t18-grupoXX",
          "Fil ouvert par le Scrum Master sur le canal du groupe, #2026-2b-t18-grupoXX")),
        (("Each member", "Cada integrante", "Chaque membre"),
         ("Replies with: done yesterday, doing today, blocker, and the link to the card",
          "Responde com: o que fez ontem, o que faz hoje, impedimento e o link do card",
          "Répond avec : fait hier, fait aujourd'hui, blocage et le lien de la carte")),
        (("Scrum Master", "Scrum master", "Scrum Master"),
         ("Records absences, blockers, and decisions in the group's Scrum Master canvas",
          "Registra ausências, impedimentos e decisões no canvas do scrum master do grupo",
          "Note absences, blocages et décisions dans le canvas du Scrum Master du groupe")),
        (("Advisor", "Orientador", "Encadrant"),
         ("Reads the threads and the canvas; a missing reply counts as absence from the daily",
          "Lê as threads e o canvas; resposta ausente conta como falta na daily",
          "Lit les fils et le canvas ; une réponse manquante compte comme absence au daily")),
    ]
    trs = "\n".join(
        f'            <tr>\n              <th scope="row">{L(*a)}</th>\n              <td>{L(*b)}</td>\n            </tr>'
        for a, b in linhas)
    corpo = f"""        <table class="ref-tabela grande">
          <tbody>
{trs}
          </tbody>
        </table>"""
    return slide_conteudo(n, titulo, corpo, id_="daily")


def avisos(n):
    titulo = L("Notices for Sprint 3", "Avisos da Sprint 3", "Avis du sprint 3")
    linhas = [
        (("Presentation", "Apresentação", "Présentation"),
         ("Delivered on Wednesday, 18/11", "Entregue na quarta-feira, 18/11", "Remise le mercredi 18/11")),
        (("Sprint Review 3", "Sprint Review 3", "Sprint Review 3"),
         ("Thursday, 19/11, because of the Black Consciousness holiday on 20/11", "Quinta-feira, 19/11, por causa do feriado da Consciência Negra em 20/11",
          "Jeudi 19/11, en raison du jour férié de la Conscience noire le 20/11")),
        (("Pre-validation", "Validação prévia", "Prévalidation"),
         ("30 min per group on 18/11, all members present: G01 10:00, G02 10:30, G03 11:00, G04 11:30, G05 16:20. Invitations sent by e-mail",
          "30 min por grupo em 18/11, com todos presentes: G01 10h, G02 10h30, G03 11h, G04 11h30, G05 16h20. Convites enviados por e-mail",
          "30 min par groupe le 18/11, tous les membres présents : G01 10 h, G02 10 h 30, G03 11 h, G04 11 h 30, G05 16 h 20. Invitations envoyées par e-mail")),
        (("Presenters", "Apresentadores", "Présentateurs"),
         ("The advisor chooses 2 per group on the morning of 19/11; everyone must be ready to present",
          "O orientador escolhe 2 por grupo na manhã de 19/11; todos devem estar preparados para apresentar",
          "L'encadrant choisit 2 par groupe le matin du 19/11 ; tous doivent être prêts à présenter")),
        (("Artificial assessment", "Avaliação artificial", "Évaluation artificielle"),
         ("Open from today, 4 pm, to Thursday, 12/11, 11:59 pm. Plan ahead and do not leave it to the last hour",
          "Disponível de hoje, 16h, até quinta-feira, 12/11, 23h59. Organizem-se e não deixem para a última hora",
          "Ouverte d'aujourd'hui, 16 h, à jeudi 12/11, 23 h 59. Organisez-vous et ne la laissez pas pour la dernière heure")),
    ]
    trs = "\n".join(
        f'            <tr>\n              <th scope="row">{L(*a)}</th>\n              <td>{L(*b)}</td>\n            </tr>'
        for a, b in linhas)
    corpo = f"""        <table class="ref-tabela grande">
          <tbody>
{trs}
          </tbody>
        </table>"""
    return slide_conteudo(n, titulo, corpo, id_="avisos")


def atividade_board(n):
    titulo = L("Activity: each group reviews its planning and creates the cards on the board, by 6 pm",
               "Atividade: cada grupo revisa a planning e cria os cards no board, até 18h",
               "Activité : chaque groupe revoit son planning et crée les cartes dans le tableau, avant 18 h")
    passos = [
        ("Read the group's planning file and raise doubts with the advisor in the room.",
         "Ler o arquivo de planning do grupo e tirar dúvidas com o orientador na sala.",
         "Lire le fichier de planning du groupe et poser les questions à l'encadrant dans la salle."),
        ("Elect the Sprint 3 Scrum Master and write the name in the canvas.",
         "Eleger o scrum master da Sprint 3 e escrever o nome no canvas.",
         "Élire le Scrum Master du sprint 3 et écrire son nom dans le canvas."),
        ("Create one card per task in GitLab, with size, owner, and the planning ID in the title.",
         "Criar um card por tarefa no GitLab, com tamanho, dono e o ID da planning no título.",
         "Créer une carte par tâche dans GitLab, avec taille, responsable et l'ID du planning dans le titre."),
        ("Move the first card of each member to Doing before leaving.",
         "Mover o primeiro card de cada integrante para Doing antes de sair.",
         "Passer la première carte de chaque membre en Doing avant de partir."),
    ]
    lis = "\n".join(f"          <li><span>{L(*p)}</span></li>" for p in passos)
    corpo = f"""        <ol class="passos">
{lis}
        </ol>
{nota("Delivery: board with every planning task as a card with an owner, checked by the advisor at 6 pm.",
      "Entrega: board com todas as tarefas da planning como cards com dono, conferido pelo orientador às 18h.",
      "Livrable : tableau avec toutes les tâches du planning en cartes avec responsable, vérifié par l'encadrant à 18 h.")}"""
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
          {L("Sprint Planning 3", "Sprint Planning 3", "Sprint Planning 3")}
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
    _, ativ, trad, _ = base.carregar()
    slides = []

    def pos():
        return len(slides) + 1

    slides.append(capa())
    slides.append(agenda(pos()))
    slides.append(secao(pos(), ("Part A", "Parte A", "Partie A"),
                        ("Sprint 2 reflection", "Reflexão sobre a Sprint 2", "Réflexion sur le sprint 2"),
                        ("Board of post-its per group and risk matrix", "Quadro de post-its por grupo e matriz de risco",
                         "Tableau de post-it par groupe et matrice des risques")))
    slides.append(review2(pos()))
    slides.append(atividade_quadro(pos()))
    slides.append(perguntas(pos()))
    slides.append(matriz_risco(pos()))
    slides.append(secao(pos(), ("Part B", "Parte B", "Partie B"),
                        ("Executive presentation", "Apresentação executiva", "Présentation exécutive"),
                        ("Rebuilding the Sprint 2 presentation", "Reconstrução da apresentação da Sprint 2",
                         "Reconstruction de la présentation du sprint 2")))
    slides.append(academica_executiva(pos()))
    slides.append(estrutura(pos()))
    slides.append(atividade_reconstrucao(pos()))
    slides.append(secao(pos(), ("Part C", "Parte C", "Partie C"),
                        ("Situational leadership", "Liderança situacional", "Leadership situationnel"),
                        ("Autonomy follows maturity", "A autonomia acompanha a maturidade", "L'autonomie suit la maturité")))
    slides.append(lideranca(pos()))
    slides.append(mudanca_estilo(pos()))
    slides.append(leitura(pos()))
    slides.append(secao(pos(), ("Part D", "Parte D", "Partie D"),
                        ("Sprint 3", "Sprint 3", "Sprint 3"),
                        ("Calendar, artifacts, planning, and daily", "Calendário, artefatos, planning e daily",
                         "Calendrier, livrables, planning et daily")))
    slides.append(semana5(pos()))
    slides.append(semana6(pos()))
    slides.append(entregas(pos(), ativ, trad))
    slides.append(cubo(pos()))
    slides.append(planning_entregue(pos()))
    slides.append(daily(pos()))
    slides.append(avisos(pos()))
    slides.append(atividade_board(pos()))
    slides.append(encerramento())

    return f"""<!doctype html>
<html lang="en" data-lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sprint Planning 3 &middot; SI08 T18</title>

  <!-- Gerado por tools/gerar_sprint_planning_3.py (nao editar a mao). Deck trilingue
       (ADR-001); quadro de post-its em quadro/reflexao-sprint2.html (ADR-006). -->

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
