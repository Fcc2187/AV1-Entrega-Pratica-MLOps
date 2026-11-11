# Project memory

A Markdown file the skill keeps in the repository so each interview starts from what earlier interviews learned. It lives at `.best-prompt-ever/context.md`, at the root of the git repository (or the current folder when the project is not a git repository), and is committed with the code: the team shares it, and reviewers can read it.

The memory is a set of hints, not a source of truth. The code wins whenever they disagree.

## Reading (reconnaissance step 0)

1. If `.best-prompt-ever/context.md` does not exist, skip this step. The interview runs as usual.
2. Read it whole. When reconnaissance is delegated to a subagent, pass it a summary of the memory so it checks those facts instead of rediscovering them.
3. **Check every fact you will use, cheaply:** the path still exists, the version still matches the lockfile or manifest, the command is still in the scripts, the branch still exists. Do not re-audit the whole repository.
4. A fact that passes the check counts as discovered: mark the point complete and show it in the panel with the source `memory (YYYY-MM-DD)`.
5. A fact that fails the check is not used. Say so in the panel in one line ("memory says `src/billing/`; not found") and correct it at delivery.
6. Facts from the user's earlier answers (preferences, PR split, delegation criteria) cannot be checked in the code. Use them as the recommended option of the matching question, never as an answer the user did not give.

## Writing (at delivery, only with the user's OK)

1. After the final prompt, show the proposed change to the memory: the whole file on the first run, otherwise only the sections that change. Keep it separate from the prompt.
2. Ask whether to save it. Write `.best-prompt-ever/context.md` only if the user says yes; if they decline or ignore it, change nothing. Saving the memory is the one write the interview allows, and it does not authorize executing the prompt.
3. **Update in place, curate instead of accumulating.** Rewrite a fact when it changed, add what this interview learned, and remove what no longer holds: tasks that were finished, branches that no longer exist, facts reconnaissance disproved. Keep the template's sections and order.
4. Every fact carries its source (a path, a command, or `user answer`) and the date it was last confirmed (`YYYY-MM-DD`). Refresh the date of each fact this interview checked.
5. Write in English, like the rest of the skill's files, unless the file already uses another language; keep that one.

## Never record

- Secrets or any value read from a secret file: tokens, passwords, keys, connection strings. Refer to configuration by name (`the API_TOKEN env var`).
- Personal data: names, e-mails or handles of people. Preferences are recorded as the repository's conventions ("PRs are split per unit"), not as a person's profile.
- Code copied from the repository. Cite files by path, with a symbol when it helps.
- Agent-specific instructions: tool names, slash commands, skill names.
- Anything about other repositories beyond this repository's own connections to them.

## Template

Drop a section only when it does not apply to the repository (for example, *Connections* in a standalone library). Leave a section with "Nothing recorded yet." when it applies but nothing is known.

```markdown
# Project context

Maintained by the best-prompt-ever skill and by the team. Hints for agents: check against the code before relying on them.

## Architecture
- <area or service>: <what it does> — `<path>` (source, YYYY-MM-DD)

## Connections
- Calls <service or system> via <HTTP, queue, webhook, SDK> — `<path>` (source, YYYY-MM-DD)
- Called by <service or system> via <…> — `<path>` (source, YYYY-MM-DD)
- External integrations: <Zapier, payment provider, …> — `<path>` (source, YYYY-MM-DD)

## Stack and versions
- <tech> <version> (`<lockfile or manifest>`, YYYY-MM-DD)

## Conventions
- Base branch: `<branch>` (source, YYYY-MM-DD)
- Branch names: <pattern, e.g. `feat/<topic>`>, learned from <chosen names | `git branch -a`> (YYYY-MM-DD)
- Commits: <convention> (`git log`, YYYY-MM-DD)
- Pull requests: <how work is usually split into PRs and units, merge order> (source, YYYY-MM-DD)
- Migrations: <how they are created, run and rolled back> — `<path or command>` (source, YYYY-MM-DD)
- Lint: `<command scoped to files>` (source, YYYY-MM-DD)
- Tests: `<command with test paths>` (source, YYYY-MM-DD)

## Patterns
- Follow: <pattern> — `<path>` (source, YYYY-MM-DD)
- Avoid: <pattern> — <reason or alternative> (source, YYYY-MM-DD)

## Preferences
- <recurring answer or delegation criterion, e.g. "follow the existing flow that has tests"> (user answer, YYYY-MM-DD)

## Work in progress
- <task title> — branch `<name>`, <PR link or "no PR yet">, <status> (YYYY-MM-DD)
```
