# ADR-004: Animações dos decks em SVG inline com CSS, sem biblioteca

- **Data:** 15/10/2026 (atualizada no mesmo dia com as cenas por fragment)
- **Status:** Aceita
- **Decisores:** José Romualdo (orientação SI08 T18)

## Contexto

O orientador pediu um deck sobre planning e gestão de projeto no GitLab
(`aulas/planning-gitlab.html`), com cards e ilustrações SVG animadas que mostrem o
processo: o card atravessando o quadro, a branch, os commits, o merge request, a revisão e
o merge. O repositório não tem build nem package manager, e o mesmo deck precisa sair em
PDF e funcionar nos três idiomas (ADR-001).

## Decisão

As ilustrações são SVG inline no próprio HTML, animadas só com CSS
(`assets/css/planning-anim.css`). Um script de 60 linhas (`assets/js/passos.js`) traduz os
fragments do Reveal em classes `p1`, `p2`, ... na `section`.

## Motivações

- Sem dependência nova: nada de GSAP, Lottie ou bundler, coerente com o restante do
  repositório.
- Três modos de animação cobrem o pedido. **Autoplay**, que dispara quando o slide entra
  (`section.present`); **por passos**, em que o professor avança cada etapa com a seta e
  a legenda numerada mostra o passo atual; e **cena por fragment**, em que o próprio bloco é
  um fragment e roda uma sequência curta quando o Reveal o marca como `.visible` (usado nas
  cenas de desvio da daily, com o "antes" em coral e o "depois" no estilo base).
- Toda keyframe descreve só o `from`. O estado final é o estilo normal do elemento, então
  desligar a animação já mostra o resultado.
- Rótulos dentro do SVG usam `data-l`, como o restante do deck, e o teste de cobertura
  trilíngue vale para eles.
- Cores vêm de classes (`f-roxo`, `s-verde`, ...) que consomem os tokens. Nenhum hex fora
  de `inteli-brand.css`, e o `check_brand.py` continua válido.

## Riscos conhecidos e mitigações

| Risco | Mitigação |
|---|---|
| PDF captura a animação no meio | Com `?print-pdf`, `passos.js` aplica todos os passos e `html.anim-final` desliga keyframes e transições. `pdfSeparateFragments: false` evita uma página por fragment. Teste `test_pdf_mostra_o_estado_final` |
| Quem configura movimento reduzido vê animação | `prefers-reduced-motion` leva ao mesmo estado final. Teste `test_movimento_reduzido_mostra_o_estado_final` |
| SVG escalado pela largura da coluna estoura 720px | Altura fixa nas ilustrações de coluna (`grade-tarefas`, `anel`); `check_slides.py` roda nos três idiomas em `test_planning.py` |
| Passo e posição do card divergem | `test_passos_movem_o_card_pelo_quadro` confere a coluna do card em cada passo |
| `check_slides.py` só mede o estado inicial | Screenshots do início e do fim de cada slide animado antes de publicar |
| Bloco que é fragment não é medido pelo `check_slides.py` (fica oculto no estado inicial) | Screenshot com todos os fragments revelados nos três idiomas antes de publicar |

## Consequências

- Positivas: animação sem build, legível no PDF, testável com Playwright; o padrão serve para
  os próximos decks do repositório.
- Negativas: geometria escrita à mão no SVG (coordenadas em `viewBox`), e mudar o layout de
  um quadro exige ajustar os `translate` correspondentes no CSS. `@property` (contador de 0 a
  64) depende de navegador recente; sem suporte, o contador mostra 64 direto.

## ADRs relacionadas

- ADR-001 (deck trilíngue com seletor), que define o padrão `data-l` usado também dentro do SVG.
- ADR-002 (dados do LBL e grupos), fonte dos tamanhos de grupo usados no slide de 64 tarefas.
