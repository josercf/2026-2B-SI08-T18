# ADR-006: Quadro de post-its por grupo, identificado, no Supabase do M08

- **Data:** 09/11/2026
- **Status:** Aceita
- **Decisores:** José Romualdo (orientação SI08 T18)

## Contexto

Na Sprint 2 a turma não entregou os slides antes da review e decidiu, sem consultar o orientador,
fazer uma apresentação única de mais de 50 slides, que durou 1h30. A Sprint Planning 3 abre com uma
reflexão individual sobre essa sprint: cada aluno responde cinco perguntas (objetivo, entrega
própria, quem decidiu, riscos mapeados, compromisso), ao mesmo tempo que os colegas do grupo, e o
orientador precisa saber quem escreveu cada resposta. O repositório é estático e publicado no
GitHub Pages, sem servidor próprio.

## Decisão

O quadro é a página estática `quadro/reflexao-sprint2.html`, que lê e grava pelas funções `refl_*`
do projeto Supabase `m08-quiz`, o mesmo do quiz e da ADR online do 2026-2B-M08, com tabelas próprias
(`supabase/reflexao.sql`).

## Motivações

- O projeto `m08-quiz` já está ativo e já tem `quiz_chave_ok`, a chave do professor que a ADR
  online da Aula 02 do M08 usa. O mesmo modelo de token por grupo foi testado em sala em 05/11.
- O GitHub Pages do M08 e o deste repositório estão no mesmo domínio (`josercf.github.io`), então
  a chave do professor salva no navegador vale para os dois.
- Um bloco por aluno, com o nome dele, deixa a autoria visível para o grupo e para o orientador sem
  login. O nome é escolhido pelo próprio aluno; o banco recusa nome que não seja do grupo.

## Riscos conhecidos

- **Leitura entre grupos.** As tabelas têm RLS sem policy: a chave publicável não lê nada direto.
  O quadro só abre com o token do grupo, e o painel só com a chave do professor.
- **Aluno escrevendo em nome de outro.** A identificação é declarada, sem senha. Mitigação: o
  orientador acompanha a participação por integrante no painel, e a discussão em sala é presencial.
- **Banco fora do ar em sala.** O modo `&demo=1` roda em memória; o plano B é o mesmo quadro em
  papel, com as perguntas do slide 6.
- **Fotos dos alunos.** O banco guarda em `foto_url` o endereço da foto de perfil no CDN do Slack
  (192 px), e só o quadro do próprio grupo ou o painel a recebem. Nenhuma foto entra no git nem
  no Pages. Sem foto, ou com o endereço quebrado, o bloco mostra as iniciais.
- **Token exposto no projetor.** Os links vão para o canal de cada grupo no Slack, não para a tela.

## Consequências

- Positivas: a reflexão fica registrada por aluno e por pergunta, e serve de evidência para a
  mudança de estilo de orientação da Sprint 3.
- Negativas: este repositório passa a depender de um projeto Supabase de outro repositório. O SQL
  fica versionado aqui e só cria objetos com prefixo `refl_`.

## ADRs relacionadas

- ADR-001 (deck trilíngue), ADR-002 (nomes de alunos publicados nos grupos), ADR-005 (métricas por
  grupo, sem nomes). No 2026-2B-M08: ADR-016 (ADR online por grupo com token).
