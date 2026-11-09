# Sprint 3 planning: G01

Planning prepared by the advisor from the group's board and repository (read on 09/11/2026), the
Sprint 3 artifacts in Adalove, and the week's graded activities. The group reviews this file during
Sprint Planning 3 and creates one card per task on the board by 6 pm today.

## 1. Sprint context

| Item | Value |
|---|---|
| Period | 10/11 to 18/11, 7 working days (planning on 09/11 and review on 19/11 are excluded) |
| Sprint goal | Deliver the project's data cube as ClickHouse views derived from a raw JSON ingestion table, documented and demonstrated at Sprint Review 3 |
| Project artifact | Automated Data Cube, weight 7%, on main by 20/11 and demonstrated at Sprint Review 3 (19/11) |
| Individual graded activity | Who Decides What? (3%), graded activity done in class, individual and handwritten |
| Presentation | Delivered on 18/11 and validated with the advisor at 10:00 on 18/11, with every member present |
| Sprint Review 3 | 19/11, morning; the advisor picks the group's 2 presenters on the spot |
| Members | 8 |

## 2. Group status on 09/11

| Indicator | Value | Source |
|---|---|---|
| Sprint 2 issues | 81, all closed, each with 1 assignee | GitLab, milestone Sprint 02 |
| Merge requests | 70 merged and 11 closed without merge | GitLab |
| Current analytical database | Embedded DuckDB, local file | `docs/data_ingestion/decision_record.md` |
| Existing fact table | `fact_financial_execution_monthly`: period, UG, 18 classification codes, flow type, amount, and line count | `olap/sql/schema_v1.sql` |
| DataApp queries | 3 queries in `sql/dataapp/` | repository |
| ClickHouse | Absent; compared by architecture only, without measurement | `decision_record.md` |
| Sprint 3 milestone | `Sprint 03` exists, with no issues yet | GitLab |

**What this changes in Sprint 3.** The artifact requires the cube to be implemented in ClickHouse
and built only from views over the raw JSON ingestion table. G01 has a dimensional model implicit in
its DuckDB fact table, but has neither ClickHouse nor a raw JSON table. The planning therefore starts
with the ClickHouse infrastructure and the raw table load (block B), and reuses the grain and the
codes of the current fact table as the starting point of the model (block A). The DuckDB pipeline
stays as it is; Sprint 3 adds the ClickHouse path and records the decision in an ADR.

## 3. Planning rules

1. Every task becomes a card on the board, with this planning's ID in the title, as in `[S3-B04] Fact view`, and the milestone `Sprint 03`.
2. Sizes: S 15 min, M 30 min, L 60 min, XL 120 min. A task larger than XL is split before entering Doing.
3. Each card has exactly one owner. WIP of 1 card in Doing per member.
4. No member has fewer than 7 cards in the sprint, one per working day.
5. Every merge request is reviewed by a member other than the author, following the rotation in section 7, before the merge.
6. Changing, splitting, or dropping a task requires the advisor's approval in the group's channel and a record in the Scrum Master canvas.

## 4. Definition of Done

- Code or document on main through a merge request reviewed by another member.
- Card linked to the merge request (`Refs #number`) and closed by its owner.
- View: script in `clickhouse/sql/`, run on the group's local ClickHouse, with the matching validation query passing.
- Document: section in `docs/data_cube/`, linked from the README.

## 5. Backlog

### A. Dimensional modeling

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-A01 | List the questions the dataApp must answer with the cube, starting from the 3 queries in `sql/dataapp/` | M | |
| S3-A02 | Define the fact grain and the measures (amount, line count), starting from `fact_financial_execution_monthly` | M | A01 |
| S3-A03 | Group the 18 classification codes into dimensions: time, UG, agency, program, expense nature, location, flow type | L | A02 |
| S3-A04 | Choose between star and snowflake and record the decision in `docs/data_cube/adr_model.md` | M | A03 |
| S3-A05 | Draw the dimensional model diagram | M | A04 |
| S3-A06 | Review the model with the advisor at the follow-up on 13/11 | M | A05 |

### B. ClickHouse and raw JSON table

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-B01 | Run a local ClickHouse in `infra/clickhouse/compose.yaml`, following the RustFS setup | L | |
| S3-B02 | Record the ADR adopting ClickHouse for the cube, keeping DuckDB in the current pipeline | M | B01 |
| S3-B03 | Create the raw ingestion table with one JSON record per Silver row | L | B01 |
| S3-B04 | Write the loader that reads Silver and writes the raw JSON table | XL | B03 |
| S3-B05 | Load the confirmed common sample and check the row count against Silver | M | B04 |
| S3-B06 | Map each JSON field to its target type (string, integer, Decimal(38,2), date) | L | B03, A03 |
| S3-B07 | Create the time dimension view, with JSON extraction and CAST | M | B06 |
| S3-B08 | Create the UG dimension view | M | B06 |
| S3-B09 | Create the agency dimension view (superior body, subordinate body, management unit) | L | B06 |
| S3-B10 | Create the program dimension view (function, subfunction, program, action, budget plan) | L | B06 |
| S3-B11 | Create the expense nature dimension view (category, group, element, modality) | L | B06 |
| S3-B12 | Create the location dimension view (state, municipality, localizer) | M | B06 |
| S3-B13 | Create the fact view, with JSON extraction, CAST, and dimension keys | XL | B07 to B12 |
| S3-B14 | Organize the scripts in `clickhouse/sql/` with the execution order | M | B13 |
| S3-B15 | Write the validation queries: counts, nulls, orphan keys, and types | L | B13 |
| S3-B16 | Check the cube's monthly totals against the DuckDB totals on the same sample | L | B13 |
| S3-B17 | Rewrite the 3 dataApp queries over the ClickHouse cube | L | B13 |
| S3-B18 | Time the 3 queries on ClickHouse and on DuckDB and record the numbers | M | B17 |
| S3-B19 | Write automated tests for the validation queries | L | B15 |

### C. Cube documentation

| ID | Task | Size | Depends on |
|---|---|---|---|
| S3-C01 | Document the chosen model and its rationale | L | A04 |
| S3-C02 | Document the JSON parsing and CAST strategy | M | B13 |
| S3-C03 | Document how the fact and dimension views derive from the raw table | M | B13 |
| S3-C04 | Write the instructions to start ClickHouse, load, run, and validate the views | M | B15 |
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
| B. ClickHouse and views | 19 | 17.5 |
| C. Documentation | 6 | 3.25 |
| D. Review | 7 | 3.75 |
| E. Process | 31 (7 dailies, 16 reviews, 8 preparations) | 13.75 |
| **Total** | **69** | **41.75** |

With 8 members, that is 69 cards for 56 member-days, about 8.6 cards per member.

Critical path: B01, B03, B04, B05, B06, B07 to B12, B13, B17, D03, D06. The raw table loader (B04)
and the fact view (B13) are the two XL tasks on the path; if B04 is not in review by 12/11, the Scrum
Master records the blocker in the canvas and tells the advisor the same day.

| Day | Expected milestone |
|---|---|
| 10/11 | A01 to A03 closed; local ClickHouse running (B01) |
| 11/11 | Model decided (A04, A05); raw table created (B03) |
| 12/11 | Loader in review (B04); type mapping (B06) |
| 13/11 | Sample loaded (B05); model reviewed at the follow-up (A06) |
| 16/11 | Dimension and fact views (B07 to B13) |
| 17/11 | Validation, comparison with DuckDB, and dataApp queries (B15 to B18); documentation |
| 18/11 | Presentation delivered and pre-validation at 10:00 (D06, D07) |

## 7. Distribution

The group fills in the owner of every card on the board today, by 6 pm. The Sprint 2 review
rotation (`PROCESS.md`) still applies to S3-E02:

| Author | Reviewer |
|---|---|
| Adrien | Giovanna |
| Patrick | Adrien |
| Raphael | Patrick |
| Giovanna | Raphael |
| Henri | Lívia |
| Paulo | Henri |
| Emma | Paulo |
| Lívia | Emma |
