# Sprint 3 planning: G03

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
| Presentation | Delivered on 18/11 and validated with the advisor at 11:00 on 18/11, with every member present |
| Sprint Review 3 | 19/11, morning; the advisor picks the group's 2 presenters on the spot |
| Members | 7 |

## 2. Group status on 09/11

| Indicator | Value | Source |
|---|---|---|
| Sprint 2 issues | 49, all closed, each with 1 assignee (7 per member) | GitLab, milestone Sprint 02 |
| Merge requests | 70 merged (66 into `develop`, 4 into `main`) and 5 closed without merge | GitLab |
| Current analytical database | ClickHouse 24.8.14.39 in Docker Compose, with RustFS as object storage | `infra/docker-compose.yml`, `infra/README.md` (MR !48) |
| Raw JSON ingestion table | `raw.records`, one table for every source, plus `raw.ingestion_log` and the view `raw.records_committed` | `infra/clickhouse/init/01_raw_schema.sql` (MR !48) |
| Loaded volume | 2,367,521 rows over 24 sources in the clean-clone run of 06/11, all 1,167 log lines with status `success` | MR !67, `infra/README.md` |
| Type maps for the CAST | 52 keys of the monthly execution; 472 source and key pairs over 9 document families and 10 reference tables, whose SQL has not run on the server yet | `etl/type_maps/` (MRs !74 and !65) |
| Fact and dimension views | None; the cube views and the DataAPP are described as planned | `documents/documentation.md` section 5.1 (MR !63) |
| DataApp queries | None; the L1 cards, the 19 L2 views and the L3 records are specified | `docs/Information_Architecture.md` (MR !73) |
| One-command start (#66) | Issue closed, command not built | MR !67 |
| Sprint 3 milestone | `Sprint 03` exists, with no issues yet | GitLab |

**What this changes in Sprint 3.** The artifact requires the cube to be implemented in ClickHouse
and built only from views over the raw JSON ingestion table. G03 already has both: ClickHouse runs in
the Compose stack, `raw.records` holds the JSON payload of every source as text, and Sprint 2 left a
type map of every JSON key with its target type and guarded conversion. The planning therefore drops
the ClickHouse setup, the raw table, and the loader, and starts from the replay of the full load, the
run of the type maps on the full table, and the views (block B). The model starts from the L1 cards
and L2 views of the Information Architecture and from the 52 keys of the monthly execution (block A).
Issue #66 closed without the one-command start, so it returns as task S3-B02.

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
- View: script in `infra/clickhouse/cube/`, run on the group's local ClickHouse, with the matching validation query passing.
- Document: section in `docs/Data_Cube.md`, linked from the README and from `documents/documentation.md`.

## 5. Backlog

### A. Dimensional modeling

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-A01 | List the questions the dataApp must answer with the cube, starting from the L1 cards and L2 views in `docs/Information_Architecture.md` | M | |
| S3-A02 | Define the fact grain and the measures (the six amounts and the line count) from `etl/type_maps/monthly_execution.csv`, and decide whether the document families enter as a second fact for the L3 records | M | A01 |
| S3-A03 | Group the 40 codes and labels of the monthly execution into dimensions: time, UGE, military organization and RM, programmatic classification, expense nature, correction index | L | A02 |
| S3-A04 | Choose between star and snowflake, given the UGE, OM and RM bridges in `data/04_REFERENCE/`, and record the decision in `docs/Data_Cube.md` | M | A03 |
| S3-A05 | Draw the dimensional model diagram | M | A04 |
| S3-A06 | Review the model with the advisor at the follow-up on 13/11 | M | A05 |

### B. ClickHouse views over `raw.records`

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-B01 | Replay the full load from the package as delivered and compare the row count per source with the 2,367,521 rows of MR !67 | M | |
| S3-B02 | Build the one-command start and load that issue #66 left open | L | B01 |
| S3-B03 | Record the decision on where the cube lives: a `cube` database with views only, reading only the committed batches of `raw.records` | M | |
| S3-B04 | Run the guarded SQL of both type maps on the full `raw.records` and list every value that fails to convert | L | B01 |
| S3-B05 | Create the base view of committed records per source, over `raw.records_committed` | M | B03 |
| S3-B06 | Create the time dimension view, with JSON extraction and CAST | M | B05, A03 |
| S3-B07 | Create the UGE dimension view | M | B05, A03 |
| S3-B08 | Create the military organization dimension view, with the RM, through the reference bridges | L | B05, A04 |
| S3-B09 | Create the programmatic classification dimension view | L | B05, A03 |
| S3-B10 | Create the expense nature dimension view | L | B05, A03 |
| S3-B11 | Create the correction index dimension view (IPCA and the candidate health index), keeping nominal and real values separate | M | B05, A03 |
| S3-B12 | Create the monthly execution fact view, with JSON extraction, CAST from the type map, and dimension keys | XL | B04, B06 to B11 |
| S3-B13 | Create the document view for the L3 records, as decided in A02 | L | B04, A02 |
| S3-B14 | Organize the scripts in `infra/clickhouse/cube/` with the execution order and apply them in the `clickhouse-init` service | M | B12 |
| S3-B15 | Write the validation queries: counts, nulls, orphan keys, types, and conversion failures | L | B12 |
| S3-B16 | Check the cube's monthly totals against the control panels loaded by #86 | L | B12 |
| S3-B17 | Write the queries of the L1 cards over the cube | L | B12 |
| S3-B18 | Time the L1 queries on the full load and record the numbers | M | B17 |
| S3-B19 | Write automated tests for the views and the validation queries in `etl/tests/` | L | B15 |

### C. Cube documentation

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-C01 | Document the chosen model and its rationale | L | A04 |
| S3-C02 | Document the JSON parsing and CAST strategy | M | B12 |
| S3-C03 | Document how the fact and dimension views derive from the raw table | M | B12 |
| S3-C04 | Write the instructions to start the stack, load, run, and validate the views | M | B15 |
| S3-C05 | Record the technical decisions and the limitations, with the numbers from B16 and B18 | M | B18 |
| S3-C06 | Update the README with the cube path | S | C04 |

### D. Sprint Review 3

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-D01 | Update the risk matrix for Sprint 3, with an owner and a mitigation for each risk | M | |
| S3-D02 | Write the Sprint 2 goal, the Sprint 3 goal, and the status report (planned versus delivered) | M | |
| S3-D03 | Build the increment slides: what was done to reach the cube, per block | L | B17 |
| S3-D04 | Prepare the script of the live demonstration: start, load, query | M | B17 |
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
| B. ClickHouse views | 19 | 16 |
| C. Documentation | 6 | 3.25 |
| D. Review | 7 | 3.75 |
| E. Process | 28 (7 dailies, 14 reviews, 7 preparations) | 12.25 |
| **Total** | **66** | **38.75** |

With 7 members, that is 66 cards for 49 member-days, about 9.4 cards per member.

Critical path: B01, B04, B12, B17, D03, D06, with A01 to A04 and B05 to B11 feeding B12. The fact
view (B12) is the only XL task and depends on the type maps running on the full table (B04); if B04
is not closed by 11/11, the Scrum Master records the blocker in the canvas and tells the advisor the
same day.

| Day | Expected milestone |
|---|---|
| 10/11 | A01 to A03 closed; full load replayed (B01) |
| 11/11 | Model decided (A04, A05); type maps run on the full table (B04) |
| 12/11 | Base view and first dimension views (B05 to B08) |
| 13/11 | Model reviewed at the follow-up (A06); remaining dimension views (B09 to B11) |
| 16/11 | Fact and document views (B12, B13); scripts in `clickhouse-init` (B14) |
| 17/11 | Validation, reconciliation with the control panels, and L1 queries (B15 to B18); documentation |
| 18/11 | Presentation delivered and pre-validation at 11:00 (D06, D07) |

## 7. Distribution

The group fills in the owner of every card on the board today, by 6 pm. The repository has no
review rotation: the working rules (`rules.md`, MR !41) were closed without merge, and 8 of the 70
merged merge requests of Sprints 1 and 2 were merged by their own author. S3-E02 follows a cyclic
rotation by first name:

| Author | Reviewer |
|---|---|
| Andre | Antoine |
| Antoine | Danilo |
| Danilo | Guilherme |
| Guilherme | Johlan |
| Johlan | Leticia |
| Leticia | Mélina |
| Mélina | Andre |
