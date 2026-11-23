# ADR-007: Notas das ponderadas publicadas no deck, agregadas por grupo e sem nomes

- **Data:** 23/11/2026
- **Status:** Aceita
- **Decisores:** José Romualdo (orientação SI08 T18)

## Contexto

A Sprint Planning 4 traz números da sprint anterior, entre eles as notas dos artefatos e das
ponderadas. A ADR-002 diz que notas nunca são extraídas do export da Adalove, porque o
repositório é publicado no GitHub Pages. O orientador decidiu levar as notas para o deck,
agregadas por grupo e sem nomes, no mesmo critério das métricas do GitLab (ADR-005).

A nota de grupo dos artefatos de projeto vem da API da Adalove
(`listAssessmentProjectGroupGrades`). A nota individual não tem rota em lote na API para o perfil
de orientador e vem do export da turma (`Turma (N).xlsx`). O relatório da turma pelo MCP da
Adalove chega corrompido (o xlsx é entregue como texto), então o export é baixado à mão.

## Decisão

`tools/extrair_notas.py` grava `dados/notas_sprints.json` com, por artefato de projeto, a nota
do grupo e a lista ordenada da razão nota individual / nota do grupo e, por autoestudo, as médias
da turma e de cada grupo e as contagens de notas abaixo de 6 e iguais a zero; nenhuma nota é
associada a nome. A nota de grupo da API fica em `dados/notas_grupo_adalove.json`, sem o feedback.

## Motivações

- A nota do grupo e a média de cada grupo bastam para a discussão em sala e são conhecidas pelos
  próprios grupos.
- A razão individual / grupo mostra o efeito do fator individual sem expor quem recebeu qual nota.
- Coleta e geração por script mantêm o número rastreável e testável, como na ADR-005.

## Riscos conhecidos e mitigações

| Risco | Mitigação |
|---|---|
| Lista ordenada de fatores permitir inferir a nota de um aluno num grupo de 7 ou 8 | Aceito pelo orientador, como na ADR-005; sem nomes no deck nem nos dados. Se um grupo pedir, o slide sai do deck público |
| Feedback dos professores, que pode citar nomes, ir para o repositório | Só a nota numérica é transcrita; o teste `test_dados_versionados_nao_trazem_feedback` impede |
| Nome de aluno vazar no JSON ou no deck | `test_deck_e_dados_nao_trazem_nome_de_aluno` compara com `dados/grupos.js` |
| Export desatualizado em relação à Adalove | O deck cita a data do export; regerar com um export novo atualiza tudo |
| Artefato ainda sem nota publicada | Fica em `pendentes` e aparece só como "ainda não publicada" |

## Consequências

- Positivas: o deck mostra notas reais da turma sem expor alunos; um comando atualiza os números.
- Negativas: duas fontes (API para nota de grupo, export para nota individual); a ADR-002 deixa de
  valer para notas agregadas.

## ADRs relacionadas

- ADR-002: dados do LBL e grupos publicados (esta ADR abre exceção para notas agregadas).
- ADR-005: métricas do GitLab por grupo, sem nomes (mesmo critério de privacidade).
