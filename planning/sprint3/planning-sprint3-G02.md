# Sprint 3 planning: G02

Planning prepared by the advisor from the group's board and repository (read on 09/11/2026), the
Sprint 3 artifacts in Adalove, and the week's graded activities. The group reviews this file during
Sprint Planning 3 and creates one card per task on the board by 6 pm today.

## 1. Sprint context

| Item | Value |
|---|---|
| Period | 10/11 to 18/11, 7 working days (planning on 09/11 and review on 19/11 are excluded) |
| Sprint goal | Deliver the project's data cube as ClickHouse views derived from the raw JSON ingestion table, documented and demonstrated at Sprint Review 3 |
| Project artifact | Automated Data Cube, weight 7%, on main by 20/11 and demonstrated at Sprint Review 3 (19/11) |
| Individual graded activity | Who Decides What? (3%), graded activity done in class, individual and handwritten |
| Presentation | Delivered on 18/11 and validated with the advisor at 10:30 on 18/11, with every member present |
| Sprint Review 3 | 19/11, morning; the advisor picks the group's 2 presenters on the spot |
| Members | 8 |

## 2. Group status on 09/11

| Indicator | Value | Source |
|---|---|---|
| Sprint 2 issues | 64: 55 closed and 9 open, each with 1 assignee (5 to 10 per member) | GitLab, milestone Sprint 02 |
| Merge requests | 96 merged (92 into `develop`, 4 into `main`) and 7 closed without merge | GitLab |
| Current analytical database | ClickHouse 25.8.33.6 in the `warehouse` profile of Docker Compose, with RustFS as object storage | `docker-compose.yml`, `document/documentation.md` section 5.1.11.1 |
| Raw JSON ingestion table | `ssex_raw.silver_json` (`index_epoch`, `data` as JSON text, `tag`), holding the 66 keys written by the Transform; only the tag `execution` is loaded | `src/data_ingestion_structure/olap_warehouse/ddl/01_tables.sql` |
| Loaded volume | 10,227,887 rows read and 1,938,109 Army rows written over 150 months, reconciled to the cent at every level (R$ 646,724,072,788.04 committed) | `document/documentation.md` sections 5.6.4 and 5.6.7 |
| Fact and dimension views | `stg_execution`, `fact_execution`, `dim_ug`, and `dim_budget_classification` in `ddl/`; `dim_month` and `dim_military_region` in `dimensions/`, created by `load_dimensions.py` | `src/data_ingestion_structure/olap_warehouse/README.md` |
| Views outside the JSON table | `dim_month` reads the calendar and `ref_ipca`; `dim_military_region` is a fixed list of 3 rows; `dim_ug` takes its attributes from `ref_universe` | `dimensions/dim_month.sql`, `dimensions/dim_military_region.sql`, `ddl/03_dim_ug.sql` |
| CAST in the views | Only the six amounts (`toDecimal64`); codes, names, dates, year, month, and flags are read as text | `ddl/02_stg_execution.sql`, section 5.3.7 |
| Open checks | The natural key of the fact repeats in 39,168 extra rows over 37,881 keys (check 10, warning); the ten sample queries take 692 s on the full series | sections 5.6.4 and 5.6.7 |
| DataApp queries | 10 in `sample_queries.sql`: the 9 L1 cards and the health coverage strip | `src/data_ingestion_structure/olap_warehouse/sample_queries.sql` |
| Cube documentation | Section 6 of the documentation has the headings 6.1.1 to 6.1.13 with template text only | `document/documentation.md` |
| Reproduction by a second member (#82) | Not recorded | section 5.7.6 |
| Sprint 3 milestone | `Sprint 03` exists, with no issues yet | GitLab |

**What this changes in Sprint 3.** The artifact requires the cube to be implemented in ClickHouse
and built only from views over the raw JSON ingestion table, with JSON parsing and CAST. G02 already
has ClickHouse, the JSON table loaded with the full series, a star model with one snowflake level
(section 5.2.5), and four views that extract and cast the execution. The planning therefore drops the
ClickHouse setup, the raw table, and the loader, and concentrates on three gaps: two dimensions and
the attributes of `dim_ug` come from typed reference tables instead of the JSON table, the CAST covers
only the six amounts, and section 6 of the documentation is empty. Block A resolves the grain warning
of check 10 and records the star or snowflake decision; block B moves the reference data into
`silver_json` under its own tags, extends the CAST, and reruns the load and the reconciliation.

**Sprint 2 open issues.** Of the 9 open issues, 7 have a merged merge request that references them
(#139 in !101, #88 in !87, #130 and #129 in !98, #125 in !91, #85 in !82, #81 in !102) and are
still labeled Waiting Review or Review; their owners close them after checking the content on
`develop` (S3-F01). Issue #128 (IA-13.4) has no merge request that references it; its owner checks it
against section 4.1.3, which already lists spending concentration as an L2 view, and closes or
finishes it (S3-F02). Issue #82, the reproduction by a second member, is referenced by !102, but
section 5.7.6 states that no reproduction has been recorded, so it carries into Sprint 3 as S3-F03.

## 3. Planning rules

1. Every task becomes a card on the board, with this planning's ID in the title, as in `[S3-B09] Fact view grain`, and the milestone `Sprint 03`.
2. Sizes: S 15 min, M 30 min, L 60 min, XL 120 min. A task larger than XL is split before entering Doing.
3. Each card has exactly one owner. WIP of 1 card in Doing per member.
4. No member has fewer than 7 cards in the sprint, one per working day.
5. Every merge request is reviewed by a member other than the author, following the rotation in section 7, before the merge.
6. Changing, splitting, or dropping a task requires the advisor's approval in the group's channel and a record in the Scrum Master canvas.

## 4. Definition of Done

- Code or document on `develop` through a merge request reviewed by another member, and `develop` merged into `main` by 20/11.
- Card linked to the merge request (`Closes #number`) and closed by its owner.
- View: script in `src/data_ingestion_structure/olap_warehouse/ddl/`, applied by `apply_ddl.py` on the group's local ClickHouse, with the matching validation query passing.
- Document: subsection of section 6 of `document/documentation.md`, linked from the README.

## 5. Backlog

### A. Dimensional modeling

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-A01 | List the questions the dataApp must answer with the cube, starting from the 9 L1 cards in `sample_queries.sql` and the L2 views of section 4.1.3.6 | M | |
| S3-A02 | Resolve the grain warning of check 10 (39,168 extra rows over 37,881 keys): find the source of the repetition and decide between aggregating in the fact view and adding a degenerate key | L | A01 |
| S3-A03 | Check each L2 filter of section 4.1.3.6 against the attributes of `dim_month`, `dim_ug`, `dim_military_region`, and `dim_budget_classification`, and list the missing attributes | M | A01 |
| S3-A04 | Choose between star and snowflake, given the `dim_ug` to `dim_military_region` level of section 5.2.5, and record the decision in section 6.1.3 | M | A02, A03 |
| S3-A05 | Update the model diagram (`assets/sprint2/er_diagram_data_warehouse.png`) to the Sprint 3 model, in `assets/sprint3/` | M | A04 |
| S3-A06 | Review the model with the advisor at the follow-up on 13/11 | M | A05 |

### B. ClickHouse views over `silver_json`

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-B01 | Record the decision to load the IPCA and the universe of executors into `silver_json` under their own tags, so that every dimension derives from the JSON table | M | |
| S3-B02 | Change `load_dimensions.py` to write the IPCA (144 rows) and the universe (69 rows) into `silver_json` as JSON, under the tags of B01 | L | B01 |
| S3-B03 | Map each of the 66 JSON keys to its target type (string, integer, Decimal, date, boolean) and record the conversion rule for null and invalid values | L | |
| S3-B04 | Extend the CAST of `stg_execution` to the dates, the year, the month, and the flags, with guarded conversion, and count the values that fail to convert | L | B03 |
| S3-B05 | Rewrite `dim_month` over the IPCA tag of `silver_json`, keeping the 150 months and the flags `is_ipca_missing` and `is_vcmh_missing` | M | B02 |
| S3-B06 | Rewrite `dim_ug` to read the attributes of the 69 executors from the universe tag of `silver_json` | L | B02, A03 |
| S3-B07 | Derive `dim_military_region` from the region values of the universe tag, replacing the fixed list | M | B06, A04 |
| S3-B08 | Add to `dim_budget_classification` the attributes listed in A03 | M | A03, B04 |
| S3-B09 | Apply the grain decision of A02 in `fact_execution` | L | A02, B04 |
| S3-B10 | Move `dim_month.sql` and `dim_military_region.sql` into `ddl/` with the execution order, applied by `apply_ddl.py` | M | B05, B07 |
| S3-B11 | Rerun the full load and the reconciliation, and compare with the 1,938,109 rows and the totals of Table 103 | XL | B09, B10 |
| S3-B12 | Write the validation queries: nulls per key, CAST failures, orphan keys of the new dimensions, and column types | L | B09, B10 |
| S3-B13 | Write automated tests for the views with invented records, as in section 5.3.7, in `tests/test_views.py` | L | B12 |
| S3-B14 | Time the ten sample queries on the full load, decide whether to materialize `stg_execution`, and record the numbers | M | B11 |
| S3-B15 | Compare the 27 structural signals of card 8 with the 28 of the notebook and fix or document the difference | M | B09 |
| S3-B16 | Run the ten sample queries over the revised views and compare with step 8 of Table 106 | M | B11 |

### C. Cube documentation

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-C01 | Document the chosen model and its rationale (sections 6.1.1 to 6.1.6) | L | A04 |
| S3-C02 | Document the raw JSON source and the parsing and CAST strategy (sections 6.1.7 and 6.1.8) | M | B04 |
| S3-C03 | Document how the fact and dimension views derive from the raw table, with the diagram (sections 6.1.9 and 6.1.10) | M | B10, A05 |
| S3-C04 | Write the instructions to start the stack, load, run, and validate the views (section 6.1.11) | M | B12 |
| S3-C05 | Record the tests, the technical decisions, and the limitations, with the numbers from B11 and B14 (sections 6.1.12 and 6.1.13) | M | B14 |
| S3-C06 | Update the README with the cube path | S | C04 |

### D. Sprint Review 3

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-D01 | Update the risk matrix for Sprint 3, with an owner and a mitigation for each risk | M | |
| S3-D02 | Write the Sprint 2 goal, the Sprint 3 goal, and the status report (planned versus delivered) | M | |
| S3-D03 | Build the increment slides: what was done to reach the cube, per block | L | B16 |
| S3-D04 | Prepare the script of the live demonstration: start, load two months, query | M | B16 |
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

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-F01 | Close #139, #130, #129, #125, #88, #85, and #81 after checking their content on `develop`, linking each to its merged merge request | S | |
| S3-F02 | Check #128 (IA-13.4) against section 4.1.3 and close it, or finish the missing classification | S | |
| S3-F03 | Reproduce the pipeline as a member other than the authors, following section 5.7.6, and record the result (#82) | XL | |

## 6. Volume and critical path

| Block | Cards | Planned hours |
|---|---|---|
| A. Modeling | 6 | 3.5 |
| B. ClickHouse views | 16 | 13 |
| C. Documentation | 6 | 3.25 |
| D. Review | 7 | 3.75 |
| E. Process | 31 (7 dailies, 16 reviews, 8 preparations) | 13.75 |
| F. Carry-over | 3 | 2.5 |
| **Total** | **69** | **39.75** |

With 8 members, that is 69 cards for 56 member-days, about 8.6 cards per member.

Critical path: B01, B02, B06, B07, B10, B11, B16, D03, D06, with A01 to A04 feeding B06, B07, and
B09. The rerun of the load and the reconciliation (B11) is the XL task on the path and takes about
one hour of machine time (section 5.7.6); if B10 is not closed by 13/11, the Scrum Master records the
blocker in the canvas and tells the advisor the same day.

| Day | Expected milestone |
|---|---|
| 10/11 | A01 to A03 closed; JSON tags decided (B01); type map started (B03); carry-over closed (F01, F02) |
| 11/11 | Grain and model decided (A02, A04); reference data in `silver_json` (B02) |
| 12/11 | Extended CAST (B04); `dim_month` and `dim_ug` over the JSON table (B05, B06) |
| 13/11 | Model reviewed at the follow-up (A06); `dim_military_region`, fact grain, and scripts in `ddl/` (B07 to B10) |
| 16/11 | Full rerun and reconciliation (B11); validation queries and tests (B12, B13); reproduction (F03) |
| 17/11 | Timing, card 8, and sample queries (B14 to B16); documentation |
| 18/11 | Presentation delivered and pre-validation at 10:30 (D06, D07) |

## 7. Distribution

The group fills in the owner of every card on the board today, by 6 pm. The repository has no
review rotation: the reviewers of the 96 merged merge requests vary by merge request, and 1 of them
has no reviewer recorded. S3-E02 follows a cyclic rotation by first name:

| Author | Reviewer |
|---|---|
| Alessandra | Alexis |
| Alexis | Evie |
| Evie | Guilherme |
| Guilherme | Isiah |
| Isiah | Luana |
| Luana | Pedro |
| Pedro | Romain |
| Romain | Alessandra |
