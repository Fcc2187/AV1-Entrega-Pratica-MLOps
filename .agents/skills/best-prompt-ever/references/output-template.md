# Output template

The final prompt the skill shows at delivery. It must work when pasted into a fresh session of any coding agent, with no access to this conversation.

## Filling rules

1. **Language.** Write in the conversation language, headings included. Code identifiers (paths, functions, commands, branch names) stay exactly as in the code.
2. **Paths, not code.** Cite files by path, with a symbol or line when it helps (`src/auth/session.ts` `isExpired`). Never paste code blocks from the repository; the agent can read them.
3. **No secrets.** No tokens, passwords, keys, connection strings, personal data, or values read from secret files. Refer to configuration by name (`the API_TOKEN env var`), never by value.
4. **Agent-agnostic.** No tool names, slash commands, skill names or agent-only features. Describe actions ("run the tests in `src/auth/`"), not tools. No references to this conversation ("as discussed above").
5. **Concrete or absent.** Each line must be something the agent can act on. If a point is not applicable, write one line saying so and why (or drop the subsection when that is obvious). Do not pad sections.
6. **Sources for discovered facts.** When a value came from the repository (versions, scripts, conventions), name the file it came from, so the agent can re-check it.
7. **Delegated decisions** appear where they belong, marked as delegated, with the criterion the agent must use.
8. **Open questions and assumptions** is always present. If nothing is open, write "None."
9. **Units of work.** For a composite task, keep the shared sections once and split *Files to change*, *Execution* and *Validation* by unit where they differ.
10. **Length.** As long as the task needs and no longer. A small bugfix prompt usually fits in one screen.

## Template

Headings are shown in English; translate them to the conversation language.

```markdown
# <Short task title>

## Objective
<One or two sentences: who can do what, and what is observable when it is done.>

## Task context
- Trigger: <bug report, request, incident, debt…>
- Who is affected: <…>
- References: <ticket, design file, thread — by name or link, no secrets>
- Visual reference (UI only): <design file, screenshot, or existing screen to follow>
- Already tried: <…, or omit>

## Repository context
- **Stack and versions:** <tech version (source file)>, …
- **Area:** <directories and layers>
- **Instruction files to follow:** <CLAUDE.md, AGENTS.md, … with the sections that matter>
- **Files to change:**
  - Modify `<path>` — <what changes>
  - Create `<path>` — <purpose>
  - Tests: `<path>`
- **Similar flow to follow:** `<path>` — <what to copy from it>. Do not copy `<path>` — <why>.
- **Patterns to follow:** <pattern> (see `<path>`), …
- **Forbidden patterns:** <what not to do> — <reason or alternative>, …
- **UI and design system (UI only):**
  - Components to reuse: `<path>`, …
  - Screen to follow: `<path>`
  - States: loading <…>; empty <…>; error <…>; success <…>
  - Responsiveness: <breakpoints and behavior>
  - Accessibility: <expectations>
  - Motion: <none / reuse `<…>` / new: purpose>
  - Copy and i18n: <where strings go, languages, who provides copy>
- **Constraints:** <measurable or checkable limits>
- **Out of scope:** <adjacent work not to do>, …

## Execution
- **Base branch:** `<branch>` (<source>)
- **Branch name:** `<name>` (chosen by the developer)
- **Commit convention:** <convention> (<source, e.g. git log>)
- **Units and branches:** <one branch | one per unit, stacked or independent>
- **Pull requests:** <PR 1: contents, merge order, deploy dependency; PR 2: …>
- **Migration order:** <ordered steps relative to deploys, with rollback per step>
- **Risks:** <risk> — <mitigation or detection signal>, …

## Validation
**Scenarios**
1. <Action> → <expected result>
2. …

**Edge cases**
- <Edge> → <expected behavior>

**How to verify**
- Lint: `<command scoped to the changed files>` (<source>)
- Tests: `<command with test paths>` (<source>)
- Manual: <steps, environment, test data — never production data>

**Expected evidence**
- Scenarios <n–m>: <passing test output with test names | screenshot | response body | log line>
- Lint output for the changed files
- A list of what was not verified

## Open questions and assumptions
- <Point>: <what is still unknown> → Assume: <what the agent should do if no one answers>
- Delegated: <decision> → Criterion: <how the agent decides>
- …or "None."
```

## After the prompt

Below the prompt, outside it, say in the conversation language that you now have the context you need and ask whether you may execute it.

Then, also outside the prompt, show the proposed update to `.best-prompt-ever/context.md` (the whole file on the first run, otherwise the sections that change) and ask whether to save it, following `project-memory.md`. Saving the memory and executing the prompt are separate answers. In **large** tasks, also offer to copy the prompt into a fresh session instead, because the interview has already used part of the context window.
