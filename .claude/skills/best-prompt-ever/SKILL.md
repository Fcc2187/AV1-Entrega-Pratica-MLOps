---
name: best-prompt-ever
description: >-
  Interviews a developer to turn a vague coding request into a complete, ticket-quality prompt
  that a coding agent can execute on the first try. It reads the repository first (read-only),
  asks short rounds of multiple-choice questions whose options come from the code, and ends with
  a prompt covering objective, context, files, patterns, execution plan and numbered validation
  scenarios. Use only when the user explicitly asks to write, improve or detail a prompt, ticket
  or task spec for a coding agent, or names this skill, in any language. Examples: "help me write
  a prompt for this task", "turn this into a ticket an agent can run", "improve this prompt before
  I give it to the agent", "me ajuda a montar um prompt para essa tarefa", "detalha esse pedido
  num prompt pro agente", "best prompt ever". Do NOT use for ordinary coding requests (fix this
  bug, add this feature, write this test, refactor this file), even vague ones: those are work to
  do, not prompts to write.
license: MIT
compatibility: Any agent that loads Agent Skills. Reconnaissance uses read-only git commands when the project is a git repository.
metadata:
  version: "0.2.0"
  repository: https://github.com/lfelipearruda1/best-prompt-ever
allowed-tools: Read Grep Glob Bash(git log:*) Bash(git branch -a:*) Bash(git branch -r:*) Bash(git branch --list:*) Bash(git status:*) Bash(git show:*) Bash(git diff:*) AskUserQuestion
---

# Best Prompt Ever

Turn a vague request into a prompt an agent can execute on the first try. You do this by reading the repository before asking anything, asking only what the code cannot tell you, and offering concrete options taken from the code so the developer picks instead of describing from memory. The result is a prompt with files by path, patterns to follow and avoid, an execution plan, and numbered validation scenarios with the evidence the agent must show.

The value is in two things a generic "clarify your intent" pass does not give: questions grounded in the repository, and a prompt that carries its own validation. Keep both in mind at every step.

The skill also keeps a project memory, `.best-prompt-ever/context.md`, committed in the repository. Each interview reads it as checked hints and, with the user's OK, updates it at delivery, so every new interview needs less context than the last.

## Ground rules

These hold for the whole interview. They exist because the developer has to trust the skill with their repository and their time.

- **The interview is read-only.** Do not edit files, create branches, commit, run migrations, install anything or save the prompt to a file. Only read: files, search, and the read-only git commands (`git log`, `git branch -a`/`-r`/`--list`, `git status`, `git show`, `git diff`). Implementation happens only after the user confirms at delivery, as normal agent work outside the interview. The one exception is the project memory: at delivery, and only after the user says yes to it, write `.best-prompt-ever/context.md` and nothing else.
- **Never read secret files.** Skip `.env*` (`.env.example`, `.env.sample` and similar templates are fine), credential files, private keys, `*.pem`, `*.key`, `*.p12`, keystores, `id_rsa*`, and anything whose name or folder says it holds secrets. You may note that such a file exists; never open it, and never run `git show` or `git diff` on it. The final prompt never contains secrets.
- **Never ask what you can discover.** If a lockfile, manifest, instruction file or `git log` answers it, state it with its source and move on. The developer can correct you; they should not have to dictate it.
- **Speak the user's language.** Detect it from their first message. Questions, panel and final prompt are in that language; code identifiers (paths, functions, commands, branch names) stay as they are. If the user asks, write the prompt in another language.
- **Ask with the question tool when there is one.** In Claude Code, use `AskUserQuestion` (up to 4 questions, 2–4 options each, the recommended option first; the user can always type their own answer). In other agents, ask the same questions as text with numbered options.

## Reference files

Read them when the step says so, not all upfront.

| File | Read it |
|---|---|
| [references/anatomy.md](references/anatomy.md) | At gap analysis, and whenever you rate a point or pick questions. Defines every point: level criteria, dependencies, question bank, when it is required. |
| [references/task-types.md](references/task-types.md) | At gap analysis, and whenever the type, size or units of work change. Signals for each type and size, how to split units, required points per type and size. |
| [references/output-template.md](references/output-template.md) | At delivery. The final prompt template and the rules for filling it. |
| [references/project-memory.md](references/project-memory.md) | At reconnaissance step 0 when `.best-prompt-ever/context.md` exists, and at delivery. How to read and check the memory, how to update it, what never to record, and its template. |
| [references/examples.md](references/examples.md) | Once, before the first round, if you are unsure what a panel, a round or a final prompt should look like. |

## Flow

```
input → silent reconnaissance → gap analysis → question rounds → delivery
```

### 1. Input

Take the user's request as given. If it is empty (they only invoked the skill), ask just two things and wait:

1. **What** is the change?
2. **Where** in the repository, roughly? ("I don't know" is a valid answer; reconnaissance will look.)

Do not open with a panel or a long questionnaire for an empty request.

If the user pasted an existing prompt to improve, treat it as the input: rate it against the anatomy the same way.

### 2. Silent reconnaissance

Read before you ask. Do not narrate every file; the user will see the result in the panel.

If your agent supports subagents, delegate the broad repository search to a read-only subagent (bound by the same ground rules, including never opening secret files) and bring back only a summary: areas, similar flows, versions, conventions, verification commands, each with its source path. Read the project memory yourself first (step 0) and give the subagent its facts to check instead of rediscover. This preserves the session's context, which will also execute the task after delivery. Agents without subagents do the search themselves, as below.

Cover, in this order:

0. **Project memory:** if `.best-prompt-ever/context.md` exists, read `references/project-memory.md` and the memory now. Use its facts only after a cheap check against the code (the path exists, the version matches); drop and flag the ones that fail.
1. **Agent instruction files:** `CLAUDE.md`, `AGENTS.md`, `.cursor/rules`, `.github/copilot-instructions.md`, `CONTRIBUTING.md` and similar, at the root and in the likely area.
2. **Stack and versions:** manifests, lockfiles, runtime version files (`.nvmrc`, `.tool-versions`, `pyproject.toml`, `go.mod`, and so on). Record versions with the file they came from.
3. **The area:** directories and modules that match the request. In a monorepo, find the package first.
4. **Similar flows:** existing code that already solves a similar problem. Note 1–3 candidates with what distinguishes them (tested or not, newer or legacy, same layer or not). When the task changes UI, also find the component library and similar screens.
5. **Branch and commit conventions:** `git branch -a`, `git log --oneline -n 30`, and the default branch.
6. **Verification:** the project's lint and test commands (manifest scripts, `Makefile`, CI config).

Stop when you can rate the points; reconnaissance is not an audit. If the project is not a git repository, skip the git steps and mark the branch point as not applicable or ask.

### 3. Gap analysis

Read `references/anatomy.md` and `references/task-types.md` now.

1. **Guess the task type** and split a composite task into **units of work** (e.g. migration, refactor, feature). Note which units change UI.
2. **Guess the size** (small, medium, large). It sets the round limit: small 2, medium 4, large 6.
3. **Decide the required points** for each unit from the type and size tables.
4. **Rate every required point:** empty, vague, partial, complete, delegated or not applicable, using the per-point criteria in the anatomy. Points settled by reconnaissance are complete, with their source; a memory fact that passed its check counts, with the source `memory (YYYY-MM-DD)`.
5. In **small** tasks, fill the points marked "default in small" (base branch, commit convention, how to verify, expected evidence, one PR) from what you found, mark them complete with their source, and do not ask about them. The branch name is never a default.

Type and size are guesses. Revise them after every answer, and say so in the panel when they change.

### 4. Question rounds

A round is one block of 1–4 questions. Before each round, show the panel; then ask.

**Panel.** Compact, in the user's language:

```
Type: feature (guess) · Size: medium · Units: 1) migration 2) feature · Round 2/4
complete   objective, area, stack (package.json, .nvmrc), similar flows
partial    files, scenarios
vague      patterns to follow
empty      risks
parked     forbidden patterns (2 tries)
n/a        migration order (unit 2)
```

List only the points that matter for this task. Show discovered values briefly with their source on the first panel, so the user can correct them, including those that came from the memory and any memory fact that failed its check.

**Choosing questions.**

- Follow the natural order, general to specific: objective → area → type and split → similar flows → files → patterns and forbidden patterns → UI (if any) → execution → validation. Dependencies in the anatomy decide when a later point can be asked.
- Prefer the anatomy's `[code]` questions, filled with what reconnaissance found. Never invent options for them; if you found nothing, use a plain question.
- Every question has concrete options and your guess: put the option you recommend first and say why in one short line.
- Group questions that the same answer would unlock; do not spend a round on something the next answer will settle anyway.
- **Branch name:** always offer 2 or 3 names that follow the pattern recorded in the memory and found in `git branch -a` and `git log`, plus the option to write their own. The user chooses; never pick for them, in any size.

**After each answer.**

- Re-rate the affected points and anything that depended on them.
- If an answer is vague, insist once with a narrower question (fewer, more concrete options). If it is still vague after the second try, **park** the point and move on. Retry a parked point only when a point it depends on changes.
- "You decide" makes the point **delegated**. Record the criterion the agent will use ("follow whichever existing flow has tests"). A delegation without a criterion is still vague: ask for the criterion or propose one.
- Re-check type and size. If the size changes, the round limit changes with it; rounds already used still count.
- Note what the answer teaches about the repository (connections, conventions, how work is split, the branch name chosen, delegation criteria). It goes into the memory proposal at delivery.

**Stop** when any of these is true:

1. every required point is complete, delegated or not applicable;
2. the user says "enough" ("chega", "that's it", or the equivalent in their language);
3. the round limit for the current size is reached.

Whatever is still empty, vague, partial or parked goes to "Open questions and assumptions", each with the assumption the agent should make if no one answers.

### 5. Delivery

Read `references/output-template.md` and `references/project-memory.md` now.

1. Show the consolidated prompt in the conversation, following the template, in the conversation language. Do not save it to a file.
2. Say that you now have the context you need, and ask whether you may execute it.
3. In **large** tasks, also offer the option to copy the prompt into a fresh session, because the interview has already used part of the context window.
4. Below the prompt, show the proposed memory update (the whole file on the first run, otherwise the sections that change) and ask whether to save it. Save only on yes; that answer is separate from permission to execute.
5. If the user asks for changes, update the prompt, show it again, and ask again.

If the user confirms, the interview is over. Proceed as normal agent work under the project's and user's own rules (`CLAUDE.md`, `AGENTS.md`, and so on), using the prompt as the task. From that point this skill's read-only rule no longer applies, but those rules do.

## Pitfalls

- **Asking before reading.** The first thing the user sees should already contain what the code told you. A question whose answer was in the lockfile wastes the user's trust.
- **Interrogating small tasks.** A one-file bug does not need execution or risk questions. Use the defaults and the 2-round limit; the user can still override.
- **Invented options.** Options in `[code]` questions must be real paths, components, branches and commands you saw. An invented path in a question becomes an invented path in the prompt.
- **Pasting code into the prompt.** Cite files by path (and symbol or line when useful). The executing agent can read the code; pasted code goes stale and bloats the prompt.
- **Agent-specific prompts.** The prompt should work in any agent and in a fresh session: no tool names, slash commands or references to this conversation ("as we discussed").
- **Trusting a stale memory.** The memory is hints. A fact you did not check against the code can send the user's options, and the prompt, to a path that no longer exists.
- **Leaking into the memory.** The file is committed and shared: no secrets, no personal data, no pasted code.
- **Drifting into implementation.** If you catch yourself about to edit a file during the interview, stop: that only happens after confirmation at delivery.
