# ADR-005: Métricas da sprint coletadas do GitLab e publicadas por grupo, sem nomes

- **Data:** 26/10/2026
- **Status:** Aceita
- **Decisores:** José Romualdo (orientação SI08 T18)

## Contexto

A Sprint Planning 2 abre com a retrospectiva da Sprint 1: commits por aluno, issues abertas e
fechadas, revisão de merge requests e lead time, com uma seção por grupo. Os dados vivem no
GitLab do Inteli (`git.inteli.edu.br`), um projeto por grupo. O repositório do deck é publicado no
GitHub Pages, que expõe o repositório inteiro (ADR-002 já trata nomes de alunos como risco).

## Decisão

`tools/coletar_gitlab.py` consulta a API do GitLab e grava `dados/metricas_sprint1.json` agregado
por grupo, sem nome nem e-mail de aluno; `tools/gerar_sprint_planning.py` gera
`aulas/sprint-planning-2.html` só a partir desse JSON, e os gráficos por integrante saem como
listas numéricas ordenadas, sem identificação.

## Motivações

- Número escrito à mão envelhece e pode divergir da fonte. Com coleta e geração por script, o
  deck se atualiza com dois comandos e os testes comparam o HTML com o JSON.
- Mostrar a distribuição por integrante sem nomes cumpre o objetivo da retrospectiva (o grupo se
  reconhece e discute a concentração de commits e revisões) sem expor um aluno específico num
  site público.
- O casamento entre autor de commit e aluno usa `dados/grupos.js`, o que inclui no gráfico o
  aluno com zero commit. Contar só autores que aparecem no log esconderia justamente esse caso.

## Riscos conhecidos e mitigações

| Risco | Mitigação |
|---|---|
| Token do GitLab vazar | O token vem só de `GITLAB_TOKEN` no ambiente, nunca de arquivo; o teste `test_nenhum_token_gitlab_versionado` varre o repositório atrás de `glpat-`. Usar escopo `read_api` e revogar depois do uso |
| Autor de commit não casar com nenhum aluno (e-mail pessoal, apelido) | O coletor imprime cada commit sem aluno e `ALIASES` mapeia contas conhecidas; o JSON guarda `commits_de_nao_integrantes` para o desvio ficar visível |
| "Revisão" medida por comentário não captura aprovação sem texto | O deck define revisão como comentário de outro integrante no MR; a definição aparece na nota de cada slide |
| Commits de docente entrarem na conta dos alunos | Autores sem correspondência em `grupos.js` ficam fora dos vetores por integrante |
| Distribuição ordenada ainda permitir inferir quem é quem | Aceito: a turma não vê nomes, e o docente já tem acesso direto ao GitLab. Se o grupo pedir, o slide por grupo pode sair do deck público |

## Consequências

- Positivas: números rastreáveis à API; uma coleta por sprint alimenta tabela e slides; testes
  impedem nome de aluno e token no repositório.
- Negativas: o gerador concentra o texto do deck num script Python em vez de HTML editável à mão;
  a coleta depende de acesso do orientador a todos os grupos.

## ADRs relacionadas

- ADR-001: deck trilíngue com seletor (o gerador emite os três idiomas por slide).
- ADR-002: dados do LBL e grupos publicados (origem de `dados/grupos.js` e dos pesos).
