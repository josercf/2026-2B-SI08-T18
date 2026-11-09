# Sprint 3 planning: G04

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
| Presentation | Delivered on 18/11 and validated with the advisor at 11:30 on 18/11, with every member present |
| Sprint Review 3 | 19/11, morning; the advisor picks the group's 2 presenters on the spot |
| Members | 8 |

## 2. Group status on 09/11

| Indicator | Value | Source |
|---|---|---|
| Sprint 2 issues | 77, all closed, each with 1 assignee (8 to 14 per member) | GitLab, milestone Sprint 02 |
| Open issues | None; the 144 issues of the project are closed | GitLab |
| Merge requests | 107 merged (85 into `develop`, 3 into `main`, 19 into feature branches) and 5 closed without merge; 14 of the merged were merged by their own author | GitLab |
| Current analytical database | ClickHouse 26.8 in Docker Compose, with Silo (MinIO fork) as object storage | `docker-compose.yml` |
| Raw JSON ingestion table | `ingestion`, one table for D01, D03 and D04, with each source row as JSON text in `data_value` and amounts as strings; 10,570,406 rows on 05/11 | `sql/clickhouse/001_create_ingestion_table.sql` |
| Enriched table | `silver.enriched`, JSON type, reloaded from the Parquet lake with the tags `ssex.monthly_execution.v1`, `ssex.unit.v1` and `quarantine.v1` | `sql/clickhouse/002_create_silver_enriched.sql`, `docs/data_ingestion/json-key-dictionary.md` section 4.6, MR !111 |
| Load checks | 3 `check_*` and 4 `report_*` queries, run after every load | `sql/clickhouse/validation_queries.sql` |
| Type map for the CAST | 47 D01 keys, each with its target type | `docs/data_ingestion/json-key-dictionary.md` section 4.1 |
| Fact and dimension views | None; section 7 of the documentation is still the template, and the Gold views are planned over `silver.enriched` | `docs/documentation.md` section 7, `docs/Data_Ingestion.md` section 7.7 |
| DataApp queries | None; the L2 views NAV-03, NAV-04, NAV-05 and NAV-08 and the L3 views NAV-06, NAV-07, NAV-09 and NAV-10 are specified | `docs/information_architecture/wireframes/` |
| Decision records | Tables 18 to 22 of the technical decisions section; the repository has no `docs/adrs/` folder | `docs/Data_Ingestion.md` section 7 |
| Sprint 3 milestone | `Sprint 03` exists, with no issues yet | GitLab |

**What this changes in Sprint 3.** The artifact requires the cube to be implemented in ClickHouse
and built only from views over the raw JSON ingestion table, parsing and CASTing the JSON fields.
G04 already runs ClickHouse in the Compose stack and has the raw table `ingestion`, so the planning
drops the ClickHouse setup and the loader. The Sprint 2 design places the Gold views over
`silver.enriched`, which is filled from Parquet written by the Python and DuckDB enrichment, so the
typing and the joins with D04 happen outside ClickHouse. The planning therefore starts with a recorded
decision that the cube views read `ingestion` (B01), rebuilds in SQL the enrichment the cube needs
(latest file per month, base UG and RM from D04, health scope), and uses `silver.enriched` to check
the totals (B15). The model starts from the 47 D01 keys of the JSON key dictionary and from the L2 and
L3 views of the Information Architecture (block A). The README still states that ClickHouse is not
loaded from the Silver lake, which MR !111 changed on 07/11; C06 corrects it.

## 3. Planning rules

1. Every task becomes a card on the board, with this planning's ID in the title, as in `[S3-B12] Fact view`, and the milestone `Sprint 03`.
2. Sizes: S 15 min, M 30 min, L 60 min, XL 120 min. A task larger than XL is split before entering Doing.
3. Each card has exactly one owner. WIP of 1 card in Doing per member.
4. No member has fewer than 7 cards in the sprint, one per working day.
5. Every merge request is reviewed by a member other than the author, following the rotation in section 7, before the merge.
6. Changing, splitting, or dropping a task requires the advisor's approval in the group's channel and a record in the Scrum Master canvas.

## 4. Definition of Done

- Code or document on `develop` through a merge request reviewed by another member, and `develop` merged into `main` by 20/11.
- Card linked to the merge request (`Closes #number`) and closed by its owner.
- View: script in `sql/clickhouse/cube/`, run on the ClickHouse of `docker-compose.yml`, with the matching `check_*` query returning no row.
- Document: subsection of section 7 of `docs/documentation.md`, linked from the README.

## 5. Backlog

### A. Dimensional modeling

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-A01 | List the questions the dataApp must answer with the cube, starting from the L2 views NAV-03, NAV-04, NAV-05 and NAV-08 and the L3 views NAV-06 and NAV-07 | M | |
| S3-A02 | Define the fact grain and the measures (the six `valor_*` amounts and the line count), keeping the spending stages in separate measures | M | A01 |
| S3-A03 | Group the 41 code and name keys of D01 into dimensions: time, management unit with base UG and RM, agency, programmatic classification, expense nature, location, health scope | L | A02 |
| S3-A04 | Choose between star and snowflake, given the UG, base UG and RM hierarchy of `D04_01` and `D04_02`, and record the decision in section 7.1 of `docs/documentation.md` | M | A03 |
| S3-A05 | Draw the dimensional model diagram | M | A04 |
| S3-A06 | Review the model with the advisor at the follow-up on 13/11 | M | A05 |

### B. ClickHouse views over `ingestion`

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-B01 | Record the decision that the cube views read `ingestion`, and the role left to `silver.enriched` and to the refreshable materialized view of section 7.7 | M | |
| S3-B02 | Run the full load on a clean volume and compare the rows per `data_tag` (`report_rows_per_tag`) with the 10,570,406 rows of 05/11 | M | |
| S3-B03 | Create the cube database with a read-only role for the views, following `003_silver_loader_role.sql` | M | B01 |
| S3-B04 | Run the CAST of each D01 key of the JSON key dictionary on the full `ingestion` and list every value that fails to convert | L | B02, A03 |
| S3-B05 | Create the base view of valid D01 rows, keeping only the latest file of each month | L | B01 |
| S3-B06 | Create the time dimension view, with JSON extraction and CAST | M | B05, A03 |
| S3-B07 | Create the management unit dimension view, with base UG, RM, and unit type from the `D04_01` and `D04_02` rows of `ingestion` | L | B05, A04 |
| S3-B08 | Create the agency dimension view (superior body, subordinate body, budget unit, management) | M | B05, A03 |
| S3-B09 | Create the programmatic classification dimension view (function, subfunction, program, action, budget plan, subtitle, locator) | L | B05, A03 |
| S3-B10 | Create the expense nature dimension view (economic category, group, element, modality) | M | B05, A03 |
| S3-B11 | Create the health scope dimension view (executor context, action 2004, candidate scope), with the rule version of `config/health_scope.yaml` | M | B07 |
| S3-B12 | Create the monthly execution fact view, with JSON extraction, CAST of the six amounts to Decimal, and dimension keys | XL | B04, B06 to B11 |
| S3-B13 | Organize the scripts in `sql/clickhouse/cube/` with the execution order and run them after the load | M | B12 |
| S3-B14 | Write the validation queries in the `-- name: check_*` format: counts, nulls, orphan keys, types, and conversion failures | L | B12 |
| S3-B15 | Check the cube's monthly totals against `silver.enriched` and against the 708,642 rows of the 12 validated months | L | B12 |
| S3-B16 | Write the queries of NAV-03, NAV-04 and NAV-05 over the cube | L | B12 |
| S3-B17 | Time the queries on the full series and record the numbers | M | B16 |
| S3-B18 | Write automated tests for the views and the validation queries in `tests/` | L | B14 |

### C. Cube documentation

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-C01 | Document the chosen model and its rationale | L | A04 |
| S3-C02 | Document the JSON parsing and CAST strategy | M | B12 |
| S3-C03 | Document how the fact and dimension views derive from the raw table | M | B12 |
| S3-C04 | Write the instructions to start the Compose stack, load, run, and validate the views | M | B14 |
| S3-C05 | Record the technical decisions and the limitations, with the numbers from B15 and B17 | M | B17 |
| S3-C06 | Update the README with the cube path and the current state of `silver.enriched` | S | C04 |

### D. Sprint Review 3

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-D01 | Update the risk matrix for Sprint 3, with an owner and a mitigation for each risk | M | |
| S3-D02 | Write the Sprint 2 goal, the Sprint 3 goal, and the status report (planned versus delivered) | M | |
| S3-D03 | Build the increment slides: what was done to reach the cube, per block | L | B16 |
| S3-D04 | Prepare the script of the live demonstration: start, load, query | M | B16 |
| S3-D05 | Record the demonstration video as plan B | M | D04 |
| S3-D06 | Deliver the presentation (maximum 10 slides) by 18/11 | S | D03 |
| S3-D07 | Timed 5-minute rehearsal with every member | M | D06 |

### E. Process

| ID | Task | Size | Owner |
|---|---|---|---|
| S3-E01 | Open the daily thread and fill in the Scrum Master canvas (one card per working day, 7 in total) | S | Scrum Master |
| S3-E02 | Review another member's merge request (one card per review, 2 per member) | M | Everyone |
| S3-E03 | Revisit the Sprint 1 risk matrix before the Who Decides What? graded activity | M | Each member |

## 6. Volume and critical path

| Block | Cards | Planned hours |
|---|---|---|
| A. Modeling | 6 | 3.5 |
| B. ClickHouse views | 18 | 14.5 |
| C. Documentation | 6 | 3.25 |
| D. Review | 7 | 3.75 |
| E. Process | 31 (7 dailies, 16 reviews, 8 preparations) | 13.75 |
| **Total** | **68** | **38.75** |

With 8 members, that is 68 cards for 56 member-days, 8.5 cards per member.

Critical path: B02, B04, B12, B16, D03, D06, with A01 to A04, B05, and B06 to B11 feeding B12. The
fact view (B12) is the only XL task and depends on the CAST run on the full table (B04); if B04 is not
closed by 11/11, the Scrum Master records the blocker in the canvas and tells the advisor the same day.

| Day | Expected milestone |
|---|---|
| 10/11 | A01 to A03 closed; table decision recorded (B01); full load run (B02) |
| 11/11 | Model decided (A04, A05); CAST run on the full table (B04); cube database and role (B03) |
| 12/11 | Base view and first dimension views (B05 to B08) |
| 13/11 | Model reviewed at the follow-up (A06); remaining dimension views (B09 to B11) |
| 16/11 | Fact view (B12); scripts in `sql/clickhouse/cube/` (B13) |
| 17/11 | Validation, check against `silver.enriched`, and dataApp queries (B14 to B17); documentation |
| 18/11 | Presentation delivered and pre-validation at 11:30 (D06, D07) |

## 7. Distribution

The group fills in the owner of every card on the board today, by 6 pm. The repository has no
review rotation file; 105 of the 107 merged merge requests name one reviewer, and 14 were merged by
their own author. S3-E02 follows a cyclic rotation by first name:

| Author | Reviewer |
|---|---|
| Aira | Aurélien |
| Aurélien | Eduardo |
| Eduardo | Giorgia |
| Giorgia | Lukas |
| Lukas | Nina |
| Nina | Thomas |
| Thomas | Vinícius |
| Vinícius | Aira |
