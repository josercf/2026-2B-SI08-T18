# ADR-002: Entregas e grupos extraídos do export da Adalove, com grupos publicados

- **Data:** 14/10/2026
- **Status:** Aceita
- **Decisores:** José Romualdo (orientação SI08 T18)

## Contexto

O deck precisa mostrar as entregas ponderadas por sprint e a composição dos grupos. A API da
Adalove nega ao perfil de orientador a listagem das atividades da turma
(`list_sections_activites_admin`). O orientador forneceu o export da turma (`Turma (N).xlsx`), que
traz atividades, pesos, semanas e a relação aluno-grupo.

## Decisão

`tools/extrair_lbl.py` gera, a partir do export, `dados/atividades_ponderadas.csv` (sem dado de
aluno) e `dados/grupos.js` (nomes por grupo); os dois são versionados e o slide de grupos é
publicado no GitHub Pages, com autorização explícita do orientador em 14/10/2026.

## Motivações

- Uma fonte única para pesos e prazos: o teste `test_slide_de_entregas_bate_com_o_csv` falha se o
  slide divergir do CSV, e o CSV soma 100% do peso do módulo.
- Regerar tudo quando o LBL mudar é um comando: `python3 tools/extrair_lbl.py "<export>.xlsx"`.

## Riscos conhecidos e mitigações

| Risco | Mitigação |
|---|---|
| Nomes de alunos ficam públicos e indexáveis | Decisão do orientador. A planilha em si continua fora do git (`*.xlsx` no `.gitignore`) e só nome e grupo saem dela; notas e presença nunca são extraídas |
| Revogação da autorização | Apagar `dados/grupos.js`: `assets/js/grupos.js` remove o slide e o item da agenda sem alterar a numeração (teste `test_sem_dados_de_grupo_o_slide_some_sem_mexer_na_numeracao`). O histórico do git ainda guarda o arquivo e exigiria reescrita |
| Export desatualizado | O commit que regera os dados registra a data do export |

## Consequências

- Positivas: prazos e pesos do slide são rastreáveis ao plano do módulo; grupos atualizáveis por script.
- Negativas: dados pessoais no repositório público; a remoção completa exige reescrever o histórico.

## ADRs relacionadas

ADR-001 (deck trilíngue).
