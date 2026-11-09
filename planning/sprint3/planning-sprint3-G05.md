# Sprint 3 planning: G05

Planning prepared by the advisor from the group's board and repository (read on 09/11/2026), the
Sprint 3 artifacts in Adalove, and the week's graded activities. The group reviews this file during
Sprint Planning 3 and creates one card per task on the board by 6 pm today.

## 1. Sprint context

| Item | Value |
|---|---|
| Period | 10/11 to 18/11, 7 working days (planning on 09/11 and review on 19/11 are excluded) |
| Sprint goal | Deliver the project's data cube as ClickHouse views derived from the raw JSON ingestion table, run on the full series, documented and demonstrated at Sprint Review 3 |
| Project artifact | Automated Data Cube, weight 7%, on main by 20/11 and demonstrated at Sprint Review 3 (19/11) |
| Individual graded activity | Who Decides What? (3%), graded activity done in class, individual and handwritten |
| Presentation | Delivered on 18/11 and validated with the advisor at 16:20 on 18/11, with every member present |
| Sprint Review 3 | 19/11, morning; the advisor picks the group's 2 presenters on the spot |
| Members | 8 |

## 2. Group status on 09/11

| Indicator | Value | Source |
|---|---|---|
| Sprint 2 issues | 84: 74 closed and 10 open, each with 1 assignee (Matheus 15, Paul 14, Célestin 11, Rose 11, Nathália 10, Alice 9, Viktor 9, Iris 5) | GitLab, milestone Sprint 02 |
| Merge requests | 85: 68 merged (62 into `develop`, 4 into `main`, 2 into `docs/163-orchestration`), 10 closed without merge, 7 open | GitLab |
| Current analytical database | ClickHouse 26.8 in Docker Compose, with RustFS 1.0.0 as object storage | `docker-compose.yml`, `docs/data_ingestion/olap_engine.md` |
| Raw JSON ingestion table | `bronze.raw_records`, one row per source row of any family, with the JSON in `payload` | `sql/clickhouse/01_bronze/010_raw_records.sql` |
| Silver and Gold | 13 Silver views and 12 Gold views (5 dimensions, 2 facts, 2 bridges, 3 perspectives), all `CREATE OR REPLACE VIEW`; the only table the views read outside Bronze and `ops` is `silver.config_scope`, loaded from `config/pipeline.yaml` | `sql/clickhouse/02_silver/` to `05_perspectives/` |
| JSON parsing and CAST | `JSONExtractString` per key, money to `Decimal(18,2)` through `silver_parse_brl_money`, codes kept as `String`, failed values to NULL and listed in `silver.execution_type_errors` | `sql/clickhouse/02_silver/030_execution_typed.sql` |
| Dimensional model | Two stars sharing `dim_month`, `dim_ug` and `dim_rm`; `dim_om` reached through `dim_ug`, and it has only the link data until a `silver.om` view exists | `docs/data_ingestion/star_schema.md` |
| Real run | January 2026 only, on 04/11: 74,036 Bronze rows, 48,520 Silver rows, 2,812 fact rows; check S154 fails with 1 of 150 months and G158 was not executed | `docs/data_ingestion/load.md` |
| DataApp queries | The 3 perspective views `gold.v_kpi_national`, `v_kpi_regional` and `v_kpi_local` | `docs/data_ingestion/dataapp_contract.md` |
| Open work | 10 Sprint 02 issues, all assigned to Viktor (#163 to #171 and #173); 7 open MRs: 4 drafts (!54, !76, !77, !78), !79, !69 marked for Sprint 3, and !85 (`develop` into `main`) open since 07/11 | GitLab |
| Sprint 3 milestone | `Sprint 03` exists, with no issues yet | GitLab |

**What this changes in Sprint 3.** The artifact requires the cube to be implemented in ClickHouse
and built only from views over the raw JSON ingestion table. G05 already has both, and its Gold layer
is a star schema of views over Silver views that parse and CAST `bronze.raw_records`. The planning
therefore drops the ClickHouse setup, the raw table, and the view creation, and concentrates block B
on three gaps: the cube has run on a single month, `dim_om` lacks the organization attributes, and the
views read the configuration table `silver.config_scope`, which does not come from the raw table. The
model starts from `star_schema.md` and needs only the explicit star versus snowflake justification
and the updated diagram (block A). The 10 open Sprint 2 issues and their MRs enter as block F; the
decision for each one is in that block.

## 3. Planning rules

1. Every task becomes a card on the board, with this planning's ID in the title, as in `[S3-B04] silver.om view`, and the milestone `Sprint 03`.
2. Sizes: S 15 min, M 30 min, L 60 min, XL 120 min. A task larger than XL is split before entering Doing.
3. Each card has exactly one owner. WIP of 1 card in Doing per member.
4. No member has fewer than 7 cards in the sprint, one per working day.
5. Every merge request is reviewed by a member other than the author, following the rotation in section 7, before the merge.
6. Changing, splitting, or dropping a task requires the advisor's approval in the group's channel and a record in the Scrum Master canvas.

## 4. Definition of Done

- Code or document on `develop` through a merge request reviewed by another member, and `develop` merged into `main` by 20/11.
- Card linked to the merge request (`Closes #number`) and closed by its owner.
- View: script in `sql/clickhouse/`, run on a clean ClickHouse with the full series, with the matching check in `sql/clickhouse/06_quality/` passing.
- Document: section in `docs/data_cube.md`, linked from the README and from `docs/data_ingestion/star_schema.md`.

## 5. Backlog

### A. Dimensional modeling

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-A01 | List the questions the dataApp must answer with the cube, starting from the 3 perspective views in `dataapp_contract.md` and the canvas questions in `star_schema.md` | M | |
| S3-A02 | Check the grain and the 12 measures of `gold.fact_execution_month` (six stages, nominal and real) and the grain of `gold.fact_document` against the questions of A01 | M | A01 |
| S3-A03 | Choose between star and snowflake, given that `dim_om` is reached through `dim_ug` and `bridge_ug_om`, and record the decision in `docs/data_cube.md` | M | A02 |
| S3-A04 | Update the dimensional model diagram with the document star and the `dim_om` branch | M | A03 |
| S3-A05 | Review the model with the advisor at the follow-up on 13/11 | M | A04 |

### B. ClickHouse views over `bronze.raw_records`

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-B01 | Load every month of the Data Package into `bronze.raw_records` on a clean ClickHouse and record the row count per family | XL | |
| S3-B02 | Run the Silver and Gold checks on the full series, G158 included, and record each result | L | B01 |
| S3-B03 | Record the decision on `silver.config_scope`: keep it as a configuration table read by the views, or load the scope lists into `bronze.raw_records` | M | |
| S3-B04 | Create the `silver.om` view from the reference records of `bronze.raw_records`, with JSON extraction and CAST | L | A03 |
| S3-B05 | Add the name, analytical level, and health classification to `gold.dim_om` from `silver.om` | M | B04 |
| S3-B06 | List every value in `silver.execution_type_errors` on the full series and decide each case | L | B01 |
| S3-B07 | Write the lineage query that shows every Gold view reading only views derived from `bronze.raw_records`, plus the tables decided in B03 | M | B03 |
| S3-B08 | Check the cube's monthly totals against the control files (`silver.reconciliation`) on the full series | L | B02 |
| S3-B09 | Run the 3 perspective views on the full series and repeat the `DESCRIBE` contract of `dataapp_contract.md` section 5 | M | B02 |
| S3-B10 | Time the 3 perspective views and the fact view on the full series and record the numbers | M | B09 |
| S3-B11 | Write automated tests for `silver.om` and the completed `dim_om` in `src/tests/load/` | L | B05 |
| S3-B12 | Check that one command applies `sql/clickhouse/01_bronze/` to `06_quality/` in file order on a clean ClickHouse, and fix any gap found | M | |

### C. Cube documentation

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-C01 | Document the chosen model and its rationale, starting from `star_schema.md` and `dimension_history.md` | L | A03 |
| S3-C02 | Document the JSON parsing and CAST strategy, from `030_execution_typed.sql` and the decisions of B06 | M | B06 |
| S3-C03 | Document how the fact and dimension views derive from `bronze.raw_records`, with the lineage of B07 | M | B07 |
| S3-C04 | Write the instructions to start the stack, load, run, and validate the views, finishing the reproduction guide of #169 (MR !77) | M | B12 |
| S3-C05 | Record the technical decisions and the limitations, with the numbers from B08 and B10 and the unknown member `rm = '-1'` | M | B10 |
| S3-C06 | Update the README with the cube path | S | C04 |

### D. Sprint Review 3

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-D01 | Update the risk matrix for Sprint 3, with an owner and a mitigation for each risk | M | |
| S3-D02 | Write the Sprint 2 goal, the Sprint 3 goal, and the status report (planned versus delivered) | M | |
| S3-D03 | Build the increment slides: what was done to reach the cube, per block | L | B09 |
| S3-D04 | Prepare the script of the live demonstration: start, load, query | M | B09 |
| S3-D05 | Record the demonstration video as plan B | M | D04 |
| S3-D06 | Deliver the presentation (maximum 10 slides) by 18/11 | S | D03 |
| S3-D07 | Timed 5-minute rehearsal with every member | M | D06 |

### E. Process

| ID | Task | Size | Owner |
|---|---|---|---|
| S3-E01 | Open the daily thread and fill in the Scrum Master canvas (one card per working day, 7 in total) | S | Scrum Master |
| S3-E02 | Review another member's merge request (one card per review, 2 per member) | M | Everyone |
| S3-E03 | Revisit the Sprint 1 risk matrix before the Who Decides What? graded activity | M | Each member |

### F. Sprint 2 carry-over

The 10 open issues of Sprint 2 are all assigned to Viktor. The deliverables of #165 to #168 and #170
are already on `main` (`docs/data_ingestion/uml/`, `docs/data_ingestion/dataapp_contract.md`,
`docs/Data_Ingestion.md`), so those issues close after a check. The Sprint 2 slides (#171, #173) lost
their purpose with Sprint Review 2 and close without carry-over. The reproduction guide (#169) is
folded into S3-C04. The orchestration (#163) and the telemetry (#164) carry into Sprint 3, because the
artifact asks for an automated cube. The carry-over cards keep Viktor as owner only where his draft MR
already exists; the checks and closures go to other members.

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-F01 | Review and merge MR !69, which registers `ops.api_watermark` in the layer contract test | M | |
| S3-F02 | Check the files of #165, #166, #167, #168, and #170 on `main` and close each issue with the link to its file | M | |
| S3-F03 | Close #171 and #173 and the draft MR !78 with a note in each | S | |
| S3-F04 | Review and merge MR !79 (shared Prefect environment for #163) | M | |
| S3-F05 | Finish the live acceptance of the orchestration in MR !54 (#163) and merge it | XL | F04 |
| S3-F06 | Finish the telemetry of MR !76 (#164) and merge it | L | F05 |
| S3-F07 | Decide on MR !85 (`develop` into `main`): merge it after review or close it as replaced by !82 and !83 | S | F01 |

## 6. Volume and critical path

| Block | Cards | Planned hours |
|---|---|---|
| A. Modeling | 5 | 2.5 |
| B. ClickHouse views | 12 | 10 |
| C. Documentation | 6 | 3.25 |
| D. Review | 7 | 3.75 |
| E. Process | 31 (7 dailies, 16 reviews, 8 preparations) | 13.75 |
| F. Sprint 2 carry-over | 7 | 5 |
| **Total** | **68** | **38.25** |

With 8 members, that is 68 cards for 56 member-days, about 8.5 cards per member.

Critical path: B01, B02, B09, D03, D06, with B08 and B10 feeding the numbers of C05. The full load
(B01) and the orchestration acceptance (F05) are the two XL tasks; if B01 is not closed by 11/11,
the Scrum Master records the blocker in the canvas and tells the advisor the same day.

| Day | Expected milestone |
|---|---|
| 10/11 | A01 and A02 closed; full load started (B01); MRs !69 and !79 merged (F01, F04) |
| 11/11 | Full series loaded (B01); `config_scope` decision (B03); star versus snowflake decided (A03) |
| 12/11 | Checks on the full series (B02); `silver.om` view (B04); diagram updated (A04) |
| 13/11 | Model reviewed at the follow-up (A05); `dim_om` completed (B05); type errors decided (B06) |
| 16/11 | Lineage, reconciliation, and perspectives on the full series (B07 to B09); orchestration merged (F05) |
| 17/11 | Timing and tests (B10, B11); documentation (C01 to C06) |
| 18/11 | Presentation delivered and pre-validation at 16:20 (D06, D07) |

## 7. Distribution

The group fills in the owner of every card on the board today, by 6 pm. The review rotation of
`docs/processo.md` (section 3.7) orders the members alphabetically and moved one place in week 1 and
two places in week 2. Sprint 3 keeps that rule and moves three places in the week of 10/11 and five
places in the week of 16/11; four places would form reciprocal pairs. The release MR to `main` keeps
two reviewers, as `processo.md` requires.

| Author | Reviewer, 10/11 to 13/11 | Reviewer, 16/11 to 18/11 |
|---|---|---|
| Alice | Matheus | Paul |
| Célestin | Nathália | Rose |
| Iris | Paul | Viktor |
| Matheus | Rose | Alice |
| Nathália | Viktor | Célestin |
| Paul | Alice | Iris |
| Rose | Célestin | Matheus |
| Viktor | Iris | Nathália |
