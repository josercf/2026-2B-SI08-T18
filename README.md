# SI08 T18, 2026-2B: decks de orientação

Módulo 08 de Sistemas de Informação, "Integration, management, and analysis of big data".
Parceiro: Exército Brasileiro. Decks em Reveal.js, trilíngues (EN, PT, FR), ver
`docs/adrs/ADR-001-deck-trilingue-com-seletor.md`.

## Abrir

```bash
python3 -m http.server 8000      # a partir desta pasta
```

- `http://localhost:8000/aulas/onboarding.html` (inglês, padrão)
- `?lang=pt` ou `?lang=fr` abre em português ou francês
- Na projeção: botões EN/PT/FR no canto superior esquerdo, ou tecla `L`
- PDF: `?lang=fr&print-pdf`, imprimir com margem zero e gráficos de fundo ligados

## Validar antes de usar em aula

```bash
python3 tools/check_brand.py
python3 tools/check_slides.py "aulas/onboarding.html?lang=fr"
python3 -m pytest tools/tests/ -v
```

## Estrutura

- `aulas/`: decks
- `assets/css/`: `inteli-brand.css` (tokens), `inteli-theme.css`, `inteli-print.css` (copiados do
  `2026-2A-M03`) e `orientacao.css` (blocos e seletor de idioma deste projeto)
- `assets/js/idioma.js`: seletor de idioma
- `assets/img/docentes/`: fotos da equipe docente
- `tools/`: validadores (`check_brand.py`, `check_slides.py`) e testes
