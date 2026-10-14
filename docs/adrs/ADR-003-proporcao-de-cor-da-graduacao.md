# ADR-003: Proporção de cor do segmento Graduação

- **Data:** 14/10/2026
- **Status:** Aceita
- **Decisores:** José Romualdo (orientação SI08 T18)

## Contexto

Conferência contra o Brandbook Inteli 2025 (`INTELI - INSTITUCIONAL/MANUAL DA MARCA`). Os hex do
deck estavam todos na paleta da Graduação (p.66 e p.68), sem lilás nem verde escuro, mas a
proporção medida no deck renderizado divergia da p.68. Também havia cinza médio nos layouts, cor
que a p.68 não lista para a Graduação.

| Cor | Referência p.68 (medida na página) | Deck antes | Deck depois |
|---|---|---|---|
| Branco | 23% | 67% | 48% |
| Roxo | 27% | 11% | 16% |
| Verde | 23% | 4% | 20% |
| Cinza claro | 12% | 10% | 9% |
| Cinza escuro | 12% | 3% | 2% |
| Coral | 3% (filete) | 0% | filetes de título |

Medição: screenshots dos 17 slides em 1280x720, cada pixel atribuído à cor da paleta mais próxima.

## Decisão

Bordas de layout passam a cinza escuro; cinza médio fica restrito ao grafismo (p.77: verde, roxo e
cinza médio); separadores de bloco em verde, agenda em roxo, cabeçalhos de tabela em roxo e filete
de título em coral.

## Motivações

- A p.68 pede a proporção "sempre que possível"; os slides de conteúdo continuam brancos porque
  tabelas e textos de 14 a 18px precisam de fundo claro para leitura na projeção.
- O template de PPT institucional (`TEMPLATE PPT/`) usa a combinação Institucional (roxo e coral,
  mais cores fora da paleta como `#E60064`) e não serve de referência para Graduação.

## Riscos conhecidos e mitigações

| Risco | Mitigação |
|---|---|
| Roxo e cinza escuro seguem abaixo da referência | Aceito: aumentar exigiria fundos escuros em slides de tabela |
| Texto sobre roxo com contraste baixo | Só branco e coral sobre roxo; marca na versão negativa (p.43) |

## Consequências

- Positivas: verde e roxo passam a ser os blocos de peso, como a p.68 prevê para a Graduação.
- Negativas: três slides a mais (separadores); a numeração do rodapé mudou.

## ADRs relacionadas

ADR-001, ADR-002.
