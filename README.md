# SI08 T18, 2026-2B: decks de orientação

Módulo 08 de Sistemas de Informação, "Integration, management, and analysis of big data".
Parceiro: Brazilian Army (Exército Brasileiro). Decks em Reveal.js, trilíngues (EN, PT, FR), ver
`docs/adrs/ADR-001-deck-trilingue-com-seletor.md`.

## Abrir

```bash
python3 -m http.server 8000      # a partir desta pasta
```

- `http://localhost:8000/`: portal do módulo, com os decks nos três idiomas, o calendário
  das sprints e os links da turma (`index.html`, estilos em `assets/css/portal.css`)
- `http://localhost:8000/aulas/onboarding.html` (inglês, padrão)
- `http://localhost:8000/aulas/planning-gitlab.html`: kickoff, planning, corte por valor, DoR e DoD,
  daily e scrum master, WIP, throughput, pirâmide de code review e merge requests no GitLab, com ilustrações animadas (ver ADR-004). Na projeção, a seta avança os passos de
  cada animação; com `?print-pdf` ou movimento reduzido, cada slide mostra o estado final
- `http://localhost:8000/aulas/sprint-planning-2.html`: retrospectiva da Sprint 1 por grupo (números do
  GitLab, sem nomes), documento do processo de trabalho, calendário e entregas da Sprint 2,
  tópicos sugeridos e arguições. Gerado por script (ver "Sprint Planning 2" abaixo, ADR-005)
- `?lang=pt` ou `?lang=fr` abre em português ou francês
- Na projeção: botões EN/PT/FR no canto superior esquerdo, ou tecla `L`
- PDF: `?lang=fr&print-pdf`, imprimir com margem zero e gráficos de fundo ligados

## Atualizar entregas e grupos

Com um export novo da turma na Adalove (`Turma (N).xlsx`):

```bash
python3 tools/extrair_lbl.py "~/Downloads/Turma (N).xlsx"
```

Isso regera `dados/atividades_ponderadas.csv` e `dados/grupos.js` (ver ADR-002). O slide de
entregas é escrito à mão a partir do CSV, e o teste `test_slide_de_entregas_bate_com_o_csv`
acusa qualquer divergência.

## Sprint Planning 2

O deck `aulas/sprint-planning-2.html` é gerado, não editado à mão. As métricas vêm do GitLab:

```bash
GITLAB_TOKEN=<token com read_api> python3 tools/coletar_gitlab.py --sprint 1 --inicio 2026-10-14 --fim 2026-10-23
python3 tools/gerar_sprint_planning.py
```

O token vem só do ambiente e nunca é gravado. `dados/metricas_sprint1.json` agrega por grupo e não
contém nome nem e-mail de aluno (ADR-005). O texto do plano da Sprint 2 (calendário, tópicos,
arguições) está em `tools/gerar_sprint_planning.py`; recoletar as métricas e rodar o gerador de novo
atualiza os números.

## Validar antes de usar em aula

```bash
python3 tools/check_brand.py
python3 tools/check_slides.py "aulas/onboarding.html?lang=fr"
python3 tools/check_slides.py "aulas/planning-gitlab.html?lang=fr"
python3 tools/check_slides.py "aulas/sprint-planning-2.html?lang=fr"
python3 -m pytest tools/tests/ -v
```

## Estrutura

- `aulas/`: decks
- `assets/css/`: `inteli-brand.css` (tokens), `inteli-theme.css`, `inteli-print.css` (copiados do
  `2026-2A-M03`), `orientacao.css` (blocos e seletor de idioma deste projeto) e
  `planning-anim.css` (ilustrações animadas do deck de planning)
- `assets/js/idioma.js`: seletor de idioma; `assets/js/passos.js`: passos das animações
- `assets/img/docentes/`: fotos da equipe docente
- `tools/`: validadores (`check_brand.py`, `check_slides.py`) e testes
