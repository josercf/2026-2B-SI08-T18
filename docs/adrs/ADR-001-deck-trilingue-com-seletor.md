# ADR-001: Deck único trilíngue com seletor de idioma

- **Data:** 14/10/2026
- **Status:** Aceita
- **Decisores:** José Romualdo (orientação SI08 T18)

## Contexto

O Módulo 08 de SI (2026-2B, turma T18) é conduzido em inglês. A turma tem alunos lusófonos e 19
alunos francófonos. O orientador pediu que o material de orientação ofereça os três idiomas.

## Decisão

Cada deck é um único arquivo HTML em que todo texto visível aparece três vezes, marcado com
`data-l="en|pt|fr"`, e um seletor (`assets/js/idioma.js`) mostra apenas o idioma ativo.

## Motivações

- Um arquivo por deck mantém conteúdo, numeração de slides e layout sincronizados entre os idiomas.
  Três arquivos paralelos divergiriam na primeira correção feita em só um deles.
- O professor troca o idioma ao vivo na projeção (botões EN/PT/FR ou tecla `L`), e o aluno abre
  direto no idioma dele com `?lang=fr` ou `?lang=pt`.
- Inglês é o padrão, porque é o idioma de condução do módulo.

## Riscos conhecidos e mitigações

| Risco | Mitigação |
|---|---|
| Um texto novo entra em só um idioma | `test_todo_texto_existe_nos_tres_idiomas` exige en, pt e fr em cada grupo |
| O francês, mais longo, estoura o slide ou colide com a marca | `check_slides.py` roda uma vez por idioma em `test_layout_cabe_em_1280x720_em_cada_idioma` |
| Idioma salvo no navegador surpreende quem abre o link | `?lang=` na URL tem precedência sobre a escolha salva |

## Consequências

- Positivas: um ponto de edição por slide; validação automática de cobertura e layout nos três idiomas.
- Negativas: o HTML fica três vezes mais verboso; o PDF exportado sai em um idioma por vez
  (abrir com `?lang=xx&print-pdf`).

## ADRs relacionadas

Nenhuma. O tema visual segue o padrão do repositório `2026-2A-M03` (brandbook Inteli 2025,
segmento Graduação).
