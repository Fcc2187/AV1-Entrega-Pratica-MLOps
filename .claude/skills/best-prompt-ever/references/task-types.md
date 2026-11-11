# Task types, size and units of work

How to guess the task type and size, how to split a composite task into units of work, and which points each type and size requires. Point numbers refer to `anatomy.md`.

## Contents

1. [Task types](#task-types)
2. [Guessing the type](#guessing-the-type)
3. [Units of work](#units-of-work)
4. [Task size](#task-size)
5. [Required points](#required-points)

---

## Task types

| Type | What it is | Typical signals in the request | Typical signals in the code |
|---|---|---|---|
| `feature` | New behavior a user or caller can observe. | "add", "allow", "support", "new screen", "export", "endpoint" | No existing code for the behavior; a similar flow exists elsewhere. |
| `bugfix` | Existing behavior is wrong and must be corrected. | "broken", "wrong", "error", "sometimes", "since release X", "users report" | A specific function or path matches the symptom; recent commits nearby. |
| `refactor` | Change structure without changing behavior. | "clean up", "mess", "duplicated", "extract", "split", "rename", "move" | Duplication, long files, mixed patterns for the same job. |
| `migration` | Change a schema or stored data format, often with a backfill. | "new table", "column", "store", "history", "backfill", "rename field" | A migrations folder and tool; models or repositories that read the data. |
| `performance` | Same behavior, measurably faster or lighter. | "slow", "timeout", "too many queries", "memory", "p95" | Queries in loops, missing indexes, large payloads. |
| `dependency-upgrade` | Move a library, framework or runtime to another version. | "upgrade", "bump", "deprecated", "security advisory", "vX to vY" | Manifest and lockfile entries; deprecated API usage. |
| `config-infra` | Build, CI, deploy, environment or tooling configuration. | "CI", "pipeline", "Docker", "env var", "deploy", "lint config" | CI files, Dockerfiles, infra folders. |
| `tests` | Add or fix tests without changing production behavior. | "add tests", "cover", "flaky", "coverage" | Test folders and runner config; untested modules. |
| `docs` | Documentation only. | "document", "README", "explain in the docs" | Docs folders, README files. |

**Changing UI is a trait, not a type.** A `feature`, `bugfix` or `refactor` unit can change UI. When it does, *Task context* must include the visual reference and *UI and design system* (point 9) becomes required for that unit.

---

## Guessing the type

1. **Start from the request's verbs and nouns**, using the signals above. Ignore politeness and framing ("can you help me…").
2. **Check against the code.** A "bug" with no matching code may be a missing feature; a "feature" whose code already exists may be a bug or a refactor.
3. **Look for more than one type.** Words like "and", "also", "then show it on…" usually mean a composite task. Split it (next section).
4. **Show the guess in the panel** with "(guess)" until the user confirms it or an answer makes it obvious.
5. **Revise after every answer.** Common revisions:
   - `bugfix` → `feature` when the "wrong" behavior was never implemented.
   - `refactor` → `refactor` + `bugfix` when the user wants a behavior fixed along the way. Ask whether to split; mixing them hides behavior changes inside a refactor.
   - `feature` → `migration` + `feature` when the feature needs data that is not stored yet.

When two types fit equally, pick the one whose required points are a superset, so nothing required is skipped.

---

## Units of work

A **unit of work** is a part of the task that could be reviewed, merged or rolled back on its own. A task with one unit is simple; a task with two or more is **composite**.

**How to split:**

- One unit per type involved: a schema change is a `migration` unit, the screen that uses it is a `feature` unit.
- Split further when parts have different risk or different reviewers (e.g. backend and a separately deployed frontend).
- Do not split for its own sake: two small changes in the same file for the same outcome are one unit.

**Each unit has its own required points.** Points like *Migration order* or *UI and design system* belong to the unit that needs them and are not applicable to the others.

**Execution comes out of the split:**

- *One branch or several* (point 13) and *PR split* (point 14) become required for composite tasks.
- Order units by dependency: schema before code that reads it, refactor before the feature that builds on it, backend contract before the UI that calls it.
- A unit that must be **deployed**, not only merged, before the next one starts must say so in the execution section.

**In the panel**, list units in their order: `Units: 1) migration 2) feature (UI)`.

---

## Task size

Deduce the size at gap analysis from the objective, the area and the units of work. Adjust it as answers come in.

| Size | Signals | Round limit |
|---|---|---|
| **small** | One unit. One area and one layer (or a UI change confined to one component). A few files. No schema or stored-data change. No new screen. | 2 |
| **medium** | One or two units. One area across a few layers (e.g. API + UI). A contained schema change with no backfill. A refactor touching several callers in one package. | 4 |
| **large** | Composite task with migration plus code, or three or more units. Several packages or services. A migration with backfill. New screens. Public API or contract changes. | 6 |

**Rules of thumb:**

- Call it **small** only when every small signal holds. If one is missing, start at **medium**.
- Size up as soon as an answer reveals a new unit, a new package or a backfill. Size down when the user narrows the scope.
- When the size changes, the round limit changes; rounds already used still count. Show the change in the panel (`Size: medium → large · Round 3/6`).

**What size changes:**

| | small | medium | large |
|---|---|---|---|
| Round limit | 2 | 4 | 6 |
| Base branch, commit convention (12) | Default from repo, not asked | Discovered, confirmed as the guess | Discovered, confirmed as the guess |
| Branch name (12) | Asked: 2–3 options + own name | Same | Same |
| PR split (14) | Default: one PR | Asked if composite or migration | Asked if composite or migration |
| Risks (16) | Optional | Required for the types in the table below | Required for the types in the table below |
| How to verify (19) | Default: project's lint and test scripts on changed files | Confirmed | Confirmed |
| Expected evidence (20) | Default: passing output of those scripts + what was not verified | Confirmed | Confirmed |
| Delivery | Show prompt, ask to execute | Same | Same, plus offer to copy into a fresh session |

A default is marked **complete** with its source (e.g. "`npm run lint`, `npm test` from `package.json`"). The user sees it in the panel and can override it.

---

## Required points

`R` required · `P` partial is acceptable when *Area* is complete · `·` optional (ask only if reconnaissance shows it matters) · `—` not applicable.

| # | Point | feature | bugfix | refactor | migration | performance | dep-upgrade | config-infra | tests | docs |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Objective | R | R | R | R | R | R | R | R | R |
| 2 | Task context | · | R | · | R | R | · | · | · | · |
| 3 | Stack and versions | R | R | R | R | R | R | R | R | R |
| 4 | Area | R | R | R | R | R | R | R | R | R |
| 5 | Files to change | R | R | R | P | R | P | P | R | P |
| 6 | Similar flows | R | · | R | · | · | · | · | R | · |
| 7 | Patterns to follow | R | R | R | · | · | · | · | R | · |
| 8 | Forbidden patterns | · | · | R | · | · | R | · | · | · |
| 9 | UI and design system | UI | UI | UI | — | — | — | — | — | — |
| 10 | Constraints | · | · | · | R | R | R | R | · | · |
| 11 | Out of scope | R | R | R | R | R | R | R | R | R |
| 12 | Base branch, branch name, commits | R | R | R | R | R | R | R | R | · |
| 13 | One branch or several | C | C | C | C | C | C | C | C | C |
| 14 | PR split | C | C | C | R | C | C | C | C | C |
| 15 | Migration order | S | S | S | R | S | S | S | — | — |
| 16 | Risks | · | · | · | R | R | R | R | · | · |
| 17 | Scenarios | R | R | R | R | R | R | R | R | · |
| 18 | Edge cases | R | R | · | R | R | · | · | · | — |
| 19 | How to verify | R | R | R | R | R | R | R | R | R |
| 20 | Expected evidence | R | R | R | R | R | R | R | R | R |

- `UI` — required when the unit changes UI; not applicable otherwise. When it applies, *Task context* (2) is also required, including the visual reference.
- `C` — required for composite tasks (two or more units); not applicable for single-unit tasks.
- `S` — required for any unit that changes a schema or stored data format; not applicable otherwise.

**Then apply the size column** from the previous section: in small tasks, points 12 (base branch and commit convention only), 14, 19 and 20 are filled from defaults, and 16 becomes optional.

**For composite tasks**, required points are the union over units, rated per unit where they differ (e.g. *Files to change* for the migration unit and for the feature unit).
