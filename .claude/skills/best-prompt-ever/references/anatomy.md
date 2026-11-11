# Anatomy of the final prompt

Every point the interview tracks. For each point:

- **Means** — what the point is, in one line.
- **Levels** — what makes it vague, partial or complete, with examples. (`empty`, `delegated` and `not applicable` work the same for every point; see "Shared rules".)
- **Depends on** — points that should be settled first. A parked point is worth retrying once one of these changes.
- **Questions** — the question bank. Questions marked `[code]` must be filled with options found during reconnaissance; never ask them with invented options.
- **Required for** — task types that need this point resolved before the interview can stop, and how task size changes that. For other types it is optional: ask only if reconnaissance shows it matters.

Task types: `feature`, `bugfix`, `refactor`, `migration`, `performance`, `dependency-upgrade`, `config-infra`, `tests`, `docs`. `all` means every type. A unit that changes UI also requires *UI and design system*, whatever its type.

Task sizes: `small`, `medium`, `large` (see `task-types.md`, "Task size"). Round limits: small 2, medium 4, large 6.

## Contents

1. [Shared rules](#shared-rules)
2. [Objective](#1-objective)
3. [Task context](#2-task-context)
4. Repository context
   - [Stack and versions](#3-stack-and-versions)
   - [Area](#4-area)
   - [Files to change](#5-files-to-change)
   - [Similar flows](#6-similar-flows)
   - [Patterns to follow](#7-patterns-to-follow)
   - [Forbidden patterns](#8-forbidden-patterns)
   - [UI and design system](#9-ui-and-design-system)
   - [Constraints](#10-constraints)
   - [Out of scope](#11-out-of-scope)
5. Execution
   - [Base branch, branch name and commit convention](#12-base-branch-branch-name-and-commit-convention)
   - [One branch or several](#13-one-branch-or-several)
   - [PR split](#14-pr-split)
   - [Migration order](#15-migration-order)
   - [Risks](#16-risks)
6. Validation
   - [Scenarios](#17-scenarios)
   - [Edge cases](#18-edge-cases)
   - [How to verify](#19-how-to-verify)
   - [Expected evidence](#20-expected-evidence)

---

## Shared rules

Every point has one of six levels. Vague, partial and complete have per-point criteria below; the general meaning is:

| Level | Meaning |
|---|---|
| empty | Nothing known yet. |
| vague | Something was said, but an agent could not act on it without guessing. |
| partial | Actionable for part of the work; a specific piece is still missing. |
| complete | An agent can act on it without asking anything. |
| delegated | The user said "you decide"; recorded with the criterion the agent will use. Counts as resolved. |
| not applicable | The point does not apply to this task. Counts as resolved. |

- **empty** — nothing said and nothing found in the code.
- **delegated** — the user said "you decide". Record the decision criterion the agent will use (e.g. "follow whichever existing flow has tests"). A delegation without a criterion is still **vague**.
- **not applicable** — the point does not apply to this task. Record why in a few words (e.g. "no schema change").
- **Discovered beats asked.** If reconnaissance settles a point, mark it complete and show it in the panel as found, with its source path. A project memory fact that passed its check against the code counts as discovered, with the source `memory (YYYY-MM-DD)`; a remembered user preference only sets the recommended option (see `project-memory.md`). The user can correct it; they should not have to dictate it.
- **Each question carries a guess.** Put the option you would pick first and say why in one line.
- **Discovered default (small tasks).** In `small` tasks, a point marked "default in small" below is not asked: fill it from what reconnaissance found, mark it complete and show its source in the panel. The user can still override it.
- **Never read secret files.** Questions and `[code]` options never come from `.env*` (except `.env.example` and similar templates), credential files, private keys, `*.pem` or `*.key` files.

---

## 1. Objective

**Means:** the observable outcome when the work is done, in one or two sentences.

| Level | Criterion | Example |
|---|---|---|
| vague | An activity or topic, no outcome. | "Improve the reports." |
| partial | An outcome, but not observable or with no actor. | "Reports should be exportable." |
| complete | Who can do what, and what is observable afterwards. | "A signed-in user can export the current report table as CSV from the report page; the file has the same columns and filters as the screen." |

**Depends on:** none. Always first.

**Questions:**
1. When this is done, what can someone do that they cannot do today?
2. Who notices the change: end users, other developers, operators, nobody (internal)?
3. `[code]` I found `<entry point A>` and `<entry point B>` related to this. Is the outcome visible in one of them, or somewhere new?
4. How would you know, in one sentence, that this worked?
5. Is this one outcome or several? (If several, list them; they may become separate units of work.)

**Required for:** all.

---

## 2. Task context

**Means:** why the change is needed now: the trigger, who is affected and any background an agent cannot see in the code.

| Level | Criterion | Example |
|---|---|---|
| vague | A reason with no detail. | "Customers asked for it." |
| partial | The trigger is known but impact or source is missing. | "Support tickets about duplicated invoices." |
| complete | Trigger, who is affected and links or facts the agent needs. When the task changes UI, also the visual reference: a design file (Figma, Claude Design or another design tool), a screenshot, or an existing screen to follow. | "Since release 4.2, invoices are duplicated when a payment is retried; affects card payments only; ticket reference in the issue tracker; reproduced on staging." / UI: "New filter bar per the design file linked in the ticket; spacing and states follow the existing `OrdersPage` filters." |

**Depends on:** Objective.

**Questions:**
1. What triggered this: a bug report, a product request, tech debt, an incident, a deadline?
2. Who is affected, and how badly (blocked, annoyed, at risk)?
3. Is there an issue, ticket, design or thread the agent should read? (Paste the reference, not secrets.)
4. `[code]` The recent history of `<path>` shows `<commit or change>`. Is this related?
5. Has anything been tried already? What happened?
6. (UI) Is there a visual reference: a design file (Figma, Claude Design, another tool), a screenshot, or `[code]` an existing screen such as `<screen A>` or `<screen B>` to follow?

**Required for:** `bugfix`, `performance`, `migration`, and any unit that changes UI (including the visual reference). Optional elsewhere.

---

## 3. Stack and versions

**Means:** languages, frameworks, runtimes and key libraries, with the versions the code actually uses.

| Level | Criterion | Example |
|---|---|---|
| vague | Names without versions or source. | "It's a Node app." |
| partial | Some versions, or versions from memory rather than the repo. | "Node 20, React 18 I think." |
| complete | Versions read from lockfiles, manifests or runtime files, with their path, for every technology the change touches. | "Runtime from `.nvmrc`: 20.11; framework 14.2.3 and ORM 5.9.1 from the lockfile; language target from the compiler config." |

**Depends on:** Area (in a monorepo, versions differ per package).

**Questions:** this point is normally discovered, not asked. Ask only to resolve conflicts or gaps.
1. `[code]` The manifest says `<lib> ^X` but the lockfile resolves `<lib> Y`. Should the agent target Y?
2. `[code]` I found two versions of `<framework>` in `<package A>` and `<package B>`. Which one does this change run in?
3. Is any upgrade in progress that the agent should code toward (or away from)?
4. Any runtime constraint not visible in the repo (deployed runtime version, browser support, device targets)?

**Required for:** all.

---

## 4. Area

**Means:** where in the repository the change lives: package, service, module, layer.

| Level | Criterion | Example |
|---|---|---|
| vague | A product area, not a code location. | "The billing part." |
| partial | A code location, but too broad or ambiguous. | "The backend." / "`src/`" |
| complete | Specific directories or modules, and the layer(s) involved. | "`services/billing/` (API layer and domain) and `apps/web/src/features/invoices/` (UI)." |

**Depends on:** Objective.

**Questions:**
1. `[code]` I found `<dir A>` and `<dir B>` that look related. Which one is it, or both?
2. Which layers change: UI, API, domain logic, data access, jobs, infrastructure?
3. Does this touch more than one package or service?
4. Is there an owner or team boundary the agent should not cross?

**Required for:** all.

---

## 5. Files to change

**Means:** the files (or file patterns) the agent is expected to create or modify, cited by path.

| Level | Criterion | Example |
|---|---|---|
| vague | No paths, or "whatever is needed". | "The export code." |
| partial | Some paths, but key layers missing, or only directories. | "`src/reports/` somewhere." |
| complete | Paths per layer, marked as modify or create, including tests. Line or symbol when it helps. | "Modify `src/reports/ReportPage.tsx` (add button), `src/reports/api.ts` (`fetchReport`); create `src/reports/exportCsv.ts` and `src/reports/exportCsv.test.ts`." |

**Depends on:** Area, Similar flows.

**Questions:**
1. `[code]` Based on `<similar flow>`, I expect changes in `<file 1>`, `<file 2>` and a new `<file 3>`. Correct, or anything to add or remove?
2. `[code]` Should the new code go in `<existing file>` or in a new file next to it, like `<sibling example>`?
3. Which test files should cover this, and do they exist yet?
4. Are there generated files (clients, schemas, snapshots) that must be regenerated instead of edited?
5. Any file the agent must not touch? (Moves to Forbidden patterns or Out of scope.)

**Required for:** `feature`, `bugfix`, `refactor`, `performance`, `tests`. Partial is acceptable for `migration`, `config-infra`, `docs`, `dependency-upgrade` when Area is complete.

---

## 6. Similar flows

**Means:** existing code that already solves a similar problem and that the agent should mirror.

| Level | Criterion | Example |
|---|---|---|
| vague | "There's something like this somewhere." | "Billing has an export, I think." |
| partial | A flow named, but not chosen among alternatives, or no path. | "Like the billing export." |
| complete | One flow chosen by path, with what to copy from it (and, if several existed, why this one). | "Follow `src/billing/export.ts` (streaming + header mapping); ignore `src/legacy/csv.js` (old, untested)." |

**Depends on:** Area, Objective.

**Questions:**
1. `[code]` I found similar flows in `<path A>` and `<path B>`. Which one should this follow? (Guess: `<A>`, because it has tests / is newer / matches the layer.)
2. `[code]` `<path A>` does `<X>` and `<path B>` does `<Y>`. Which behavior is right here?
3. Is there a flow that looks similar but must **not** be copied? Why?
4. If none fits: is this the first of its kind? Should the agent establish a pattern others will follow?

**Required for:** `feature`, `refactor`, `tests`. Optional elsewhere (ask when reconnaissance finds candidates).

---

## 7. Patterns to follow

**Means:** conventions the code must respect: architecture, naming, error handling, state, data access, testing style.

| Level | Criterion | Example |
|---|---|---|
| vague | A slogan. | "Clean code." / "Follow the project standards." |
| partial | Some patterns named without where they come from. | "Use the repository pattern." |
| complete | Each pattern stated concretely, with a source path or instruction file. | "Data access only through `src/db/repositories/*` (see `UserRepository.ts`); errors via the `AppError` hierarchy in `src/errors.ts`; tests use the factories in `test/factories/`; rules from `AGENTS.md` §Testing." |

**Depends on:** Similar flows, Area. Often settled automatically once a similar flow is chosen.

**Questions:**
1. `[code]` `<instruction file>` says `<rule>`. Does it apply here as written?
2. `[code]` `<flow A>` handles errors with `<pattern X>` and `<flow B>` with `<pattern Y>`. Which one should this use?
3. How should this be tested: unit, integration, end-to-end? `[code]` Existing tests in `<area>` use `<style>`.
4. Any naming, folder or layering convention not written down anywhere?

**Required for:** `feature`, `refactor`, `bugfix`, `tests`.

---

## 8. Forbidden patterns

**Means:** things the agent must not do or use, even if they look convenient.

| Level | Criterion | Example |
|---|---|---|
| vague | A general prohibition. | "Don't break anything." |
| partial | Prohibitions without a reason or a replacement. | "No raw SQL." |
| complete | Each prohibition with the reason or the allowed alternative. | "No raw SQL: use the query builder in `src/db/`. Don't import from `src/legacy/`: it is being removed. No new dependencies without approval." |

**Depends on:** Patterns to follow, Similar flows.

**Questions:**
1. `[code]` `<path>` still uses `<old approach>`. Is it deprecated, so the agent should avoid copying it?
2. Are new dependencies allowed? If yes, under what conditions?
3. `[code]` I see both `<API A>` and `<API B>` for the same job. Is one of them banned?
4. Any shortcut that has caused incidents before (e.g. disabling a check, skipping a hook)?

**Required for:** `refactor`, `dependency-upgrade`. Optional elsewhere; record "none beyond instruction files" when the user confirms there are none.

---

## 9. UI and design system

**Means:** how the UI change fits the project's design system, components and existing screens, and which UI states and qualities it must cover.

| Level | Criterion | Example |
|---|---|---|
| vague | A look, not a spec. | "Make it look nice, like the rest of the app." |
| partial | Components or a reference screen chosen, but states, responsiveness, accessibility or copy are missing. | "Use the shared `Table` and `Button`; copy the orders page." |
| complete | Components to reuse (by path), the reference screen, every state, breakpoints, accessibility expectations, motion and copy/i18n handling. | "Reuse `ui/Table`, `ui/Button`, `ui/EmptyState`; layout like `pages/OrdersPage`. States: loading skeleton, empty with CTA, error toast with retry, success. Stacks below `md` breakpoint. Keyboard reachable, labelled controls, focus returns to the trigger. No new animation; reuse the existing fade. All strings in `locales/*/reports.json`." |

**Covers:**
- **Design system or component library:** whether the project has one, and which components to reuse instead of creating new ones.
- **Similar screen:** an existing screen whose layout and behavior to follow.
- **States:** loading, empty, error, success (and partial or disabled when relevant).
- **Responsiveness:** breakpoints and how the layout changes at each.
- **Accessibility:** keyboard use, focus, labels, contrast, screen reader announcements.
- **Animations and transitions:** none, reuse existing ones, or new ones with their purpose.
- **Copy and i18n:** where strings live, which languages, who provides the copy.

**Depends on:** Task context (visual reference), Area, Similar flows.

**Questions:**
1. `[code]` I found a component library in `<path>` with `<Component A>`, `<Component B>`, `<Component C>`. Should the change reuse these? Any component that must not be used?
2. `[code]` `<screen A>` and `<screen B>` look closest to this. Which one should the layout follow?
3. What should the user see while loading, when there is no data, on error and on success? `[code]` `<screen A>` uses `<EmptyState>` and `<ErrorBanner>`; same here?
4. Which breakpoints matter, and what changes at each? `[code]` The project defines breakpoints in `<path>`.
5. Accessibility and motion: any requirement beyond the project's current practice? Reuse existing transitions or none?
6. `[code]` Strings live in `<i18n path>` with `<languages>`. Who provides the copy, and must every language be filled?

**Required for:** any unit that changes UI, in every size. **Not applicable** otherwise.

---

## 10. Constraints

**Means:** limits the solution must respect: compatibility, performance budgets, security, deadlines, environments, data rules.

| Level | Criterion | Example |
|---|---|---|
| vague | An adjective. | "It has to be fast and secure." |
| partial | A constraint without a number or a scope. | "Must stay backward compatible." |
| complete | Measurable or checkable limits, with scope. | "Public API `v1` response shape unchanged; p95 of `GET /reports` stays under 300 ms with 10k rows; no personal data in logs; must run on the runtime from `.nvmrc`." |

**Depends on:** Objective, Stack and versions.

**Questions:**
1. Must anything stay backward compatible: API, file format, database, config, CLI flags?
2. Is there a performance or size budget? (Number, not adjective.)
3. Security or data rules: authorization, personal data, audit logging?
4. `[code]` `<config or CI file>` enforces `<limit>`. Does the change need to stay within it?
5. Any deadline or release window that limits the approach?

**Required for:** `performance`, `migration`, `dependency-upgrade`, `config-infra`.

---

## 11. Out of scope

**Means:** what the agent must not do in this task, even if it looks related.

| Level | Criterion | Example |
|---|---|---|
| vague | "Just this, nothing else." | |
| partial | Some exclusions, but the obvious temptations are not covered. | "Don't touch the UI." |
| complete | The adjacent work an agent would likely be tempted to do, listed explicitly. | "No PDF export; don't refactor `ReportTable`; don't fix the unrelated date-format bug in `utils/date.ts` (separate issue)." |

**Depends on:** Objective, Files to change.

**Questions:**
1. `[code]` While reading `<path>` I noticed `<nearby problem>`. Leave it alone?
2. Is there a follow-up task this one should not start?
3. Should the agent refactor what it touches, or keep the diff minimal?
4. Anything a reviewer would reject as "not part of this ticket"?

**Required for:** all.

---

## 12. Base branch, branch name and commit convention

**Means:** the branch to start from, the name of the new branch(es) chosen by the user, and the commit message convention.

| Level | Criterion | Example |
|---|---|---|
| vague | "The usual." | |
| partial | Base known, but the name not chosen or the commit convention unknown. | "From `main`." |
| complete | Base branch, a branch name the user chose, and the commit convention with its source. | "Base `develop` (default branch); branch `feat/PROJ-123-report-csv-export` (chosen); Conventional Commits with the ticket key, as in `git log`." |

**How it is resolved:**
- **Base branch:** discovered (default branch, or the branch recent work starts from).
- **Branch name:** never decided by the skill. Always offer 2 or 3 names that follow the pattern recorded in the project memory and found in `git branch -a` and `git log`, plus the option to write a custom name. The user picks.
- **Commit convention:** usually discovered from `git log` (e.g. Conventional Commits, a ticket key prefix). Ask only when there is no clear pattern.

**Depends on:** Task type, One branch or several.

**Questions:**
1. `[code]` Branch name: which one? `<option 1>`, `<option 2>`, `<option 3>` (all follow `<pattern>` from `git branch -a`), or write your own.
2. `[code]` The default branch is `<branch>`, but recent work starts from `<other branch>`. Which base should this use?
3. Is there a ticket key that must appear in the branch name and commits?
4. `[code]` `git log` mixes `<style A>` and `<style B>`. Which commit convention should the agent follow? (Ask only when there is no clear pattern.)

**Required for:** all except `docs` (optional there). Default in small: base branch and commit convention. The branch name is asked in every size.

---

## 13. One branch or several

**Means:** whether the units of work share a branch or each gets its own (stacked or independent).

| Level | Criterion | Example |
|---|---|---|
| vague | Undecided. | |
| partial | Several branches chosen, but how they relate is unclear. | "Separate branches." |
| complete | The branches, which unit goes in each and whether they are stacked or independent. | "Two stacked branches: `chore/report-schema` (migration), then `feat/report-csv-export` on top of it." |

**Depends on:** units of work (task type split), PR split.

**Questions:**
1. This splits into `<unit 1>` and `<unit 2>`. One branch, or one per unit? (Guess: `<choice>`, because `<reason>`.)
2. If several: stacked (each on top of the previous) or independent from the base?
3. Does any unit need to ship before the others can start?

**Required for:** composite tasks (two or more units of work). Mark **not applicable** for single-unit tasks.

---

## 14. PR split

**Means:** how the work is divided into pull requests and in what order they are reviewed and merged.

| Level | Criterion | Example |
|---|---|---|
| vague | "Some PRs." | |
| partial | Number of PRs known, contents or order not. | "Two PRs." |
| complete | Each PR with its contents, order and merge dependency. | "PR 1: migration only, merges first. PR 2: feature, depends on PR 1 being deployed." |

**Depends on:** units of work, One branch or several, Migration order.

**Questions:**
1. One PR, or split by unit of work? (Guess based on expected diff size and risk.)
2. `[code]` Recent merged PRs in this area are around `<size>`. Should this stay within that size?
3. Must any PR be deployed (not just merged) before the next one?
4. Should the agent open the PRs, or stop when the branches are ready?

**Required for:** composite tasks and `migration`. Optional for single-unit tasks (default: one PR). Default in small: one PR.

---

## 15. Migration order

**Means:** the sequence of schema/data changes relative to code changes and deploys.

| Level | Criterion | Example |
|---|---|---|
| vague | "Run the migration." | |
| partial | Steps known, ordering or rollback missing. | "Add the column, then backfill." |
| complete | Ordered steps relative to deploys, compatible with old and new code during rollout, with rollback. | "1) Add nullable `exported_at` (deploy). 2) Code writes it. 3) Backfill script. 4) Set NOT NULL in a later release. Rollback: drop column is safe until step 4." |

**Depends on:** Stack and versions, units of work, Constraints.

**Questions:**
1. `[code]` Migrations live in `<path>` and use `<tool>`. Should this follow the same format?
2. Must old and new code run against the schema at the same time (rolling deploy)?
3. Is there a data backfill? How many rows, and can it run in the request path or does it need a job?
4. What is the rollback for each step?

**Required for:** `migration`, and any unit that changes a schema or stored data format. **Not applicable** otherwise.

---

## 16. Risks

**Means:** what could go wrong in production or during rollout, and how to limit it.

| Level | Criterion | Example |
|---|---|---|
| vague | "Should be fine." | |
| partial | A risk named without mitigation. | "Might be slow on large reports." |
| complete | Each risk with likelihood or impact and a mitigation or detection signal. | "Large reports could time out: stream the response and cap at 100k rows; watch the endpoint's error rate after deploy." |

**Depends on:** Constraints, Migration order, Files to change.

**Questions:**
1. What is the worst thing this change could break, and for whom?
2. `[code]` `<path>` is used by `<callers>`. Are those callers at risk?
3. Is a feature flag or gradual rollout needed? `[code]` Flags in this repo use `<mechanism>`.
4. How would you notice a problem after deploy (metric, log, alert)?

**Required for:** `migration`, `performance`, `dependency-upgrade`, `config-infra`. Optional elsewhere, and optional in small tasks of any type.

---

## 17. Scenarios

**Means:** numbered validation scenarios in the form *action → expected result* that prove the objective is met.

| Level | Criterion | Example |
|---|---|---|
| vague | "It should work." / "Test it." | |
| partial | Scenarios listed without expected results, or only the happy path. | "1. Export a report." |
| complete | Numbered, each with a concrete action and an observable expected result, covering the main path and the failure path. | "1. Open a report with filters → click Export → CSV downloads with the filtered rows only. 2. Export with no rows → file has only the header. 3. User without access → 403, no file." |

**Depends on:** Objective, Task context.

**Questions:**
1. Walk me through the main path: what does the user (or caller) do, and what should they see?
2. What should happen when it fails (invalid input, no permission, dependency down)?
3. `[code]` Existing tests in `<test file>` cover `<cases>`. Should the new scenarios mirror them?
4. For a bug: what are the exact steps to reproduce, and what is the correct behavior?

**Required for:** all except `docs` (optional there; use a review scenario instead).

---

## 18. Edge cases

**Means:** boundary inputs and unusual states that the scenarios must also cover.

| Level | Criterion | Example |
|---|---|---|
| vague | "Handle edge cases." | |
| partial | Some edges named without expected behavior. | "Empty reports, big reports." |
| complete | Each edge with its expected behavior. | "Empty → header only. 100k+ rows → streamed, no timeout. Commas and quotes in values → escaped per RFC 4180. Non-ASCII → UTF-8 with BOM." |

**Depends on:** Scenarios, Constraints.

**Questions:**
1. Empty, huge, duplicate, concurrent: which of these can happen here, and what should each do?
2. `[code]` `<similar flow>` handles `<edge>` by `<behavior>`. Same here?
3. Any special characters, time zones, locales or units involved?
4. What happens if the action is repeated or interrupted halfway?

**Required for:** `feature`, `bugfix`, `migration`, `performance`.

---

## 19. How to verify

**Means:** the concrete commands and steps the agent runs to check its work.

| Level | Criterion | Example |
|---|---|---|
| vague | "Run the tests." | |
| partial | Commands named, but scope or environment missing. | "`npm test`." |
| complete | Exact commands scoped to the changed files, plus any manual or environment steps. | "Lint: `<lint command> <changed files>`. Tests: `<test command> src/reports/exportCsv.test.ts`. Manual: run the dev server, open `/reports/123`, click Export." |

**Depends on:** Stack and versions, Files to change, Scenarios.

**Questions:**
1. `[code]` The repo defines `<lint script>` and `<test script>` in `<manifest>`. Use these, scoped to the changed files?
2. Does any scenario need a manual check (UI, staging, external service)?
3. Is there test data or a seed the agent should use? (Never production data.)
4. Do any checks need services running locally (database, queue)? `[code]` I found `<compose file or script>`.

**Required for:** all. Default in small: the project's own lint and test scripts, scoped to the changed files.

---

## 20. Expected evidence

**Means:** what the agent must show at the end to prove each scenario passed.

| Level | Criterion | Example |
|---|---|---|
| vague | "Show it works." | |
| partial | Evidence for some scenarios, or no format. | "Test output." |
| complete | Evidence per scenario, in a checkable form. | "Scenarios 1–3: passing test output with the test names. Scenario 4: screenshot of the downloaded file opened. Lint output for changed files. A list of what was not verified." |

**Depends on:** Scenarios, How to verify.

**Questions:**
1. For each scenario, what convinces you: test output, a screenshot, a log line, a response body?
2. Should the agent list what it could not verify?
3. Do you want the final diff summarized, or only the evidence?

**Required for:** all. Default in small: passing output of the lint and test commands from *How to verify*, plus a list of what was not verified.
