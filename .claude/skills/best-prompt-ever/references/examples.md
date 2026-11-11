# Examples

Two end-to-end interviews on the same fictional project, `shop-admin`: an Express + knex API and a React admin, with `AGENTS.md`, vitest tests next to the files, a UI kit in `src/web/components/ui`, and branches like `feat/ORD-40-report-filters`.

- [Example 1 — small bugfix (English)](#example-1--small-bugfix-english)
- [Example 2 — large migration + feature with UI (Portuguese)](#example-2--large-migration--feature-with-ui-portuguese)

They show the shape of each step. Real interviews adapt the wording; the structure stays.

---

## Example 1 — small bugfix (English)

### Input

> users are getting logged out a minute before they should. help me write a prompt for an agent to fix it

### Reconnaissance (silent)

Read, without asking:

- `AGENTS.md`: tests next to the file with vitest; errors via `AppError`.
- `package.json`: express 4.19.2, vitest 1.6.0, typescript 5.4.5; scripts `lint` (eslint) and `test` (vitest run). `.nvmrc`: 20.11.1.
- `src/server/auth/session.ts`: `isExpired` returns true at `SESSION_TTL_MINUTES - 1` minutes. Matches the symptom.
- `src/server/auth/session.test.ts`: one test, fresh session only; no boundary test.
- `git log`: `feat(ORD-7): …`, `fix(…)` style; Conventional Commits with an `ORD-<n>` key. Default branch `main`. Branches: `feat/ORD-40-report-filters`, `fix/ORD-31-orders-pagination`.
- `.env` exists. Not opened.

### Gap analysis

- Type: `bugfix`. One unit, one file and its test, no schema change → **small**, 2 rounds.
- Defaults in small, filled from the repo: base `main`, Conventional Commits with `ORD-<n>` (git log), verify with `npm run lint` / `npm test` (package.json), evidence = passing output of both + what was not verified, one PR.

### Round 1

```
Type: bugfix · Size: small · Units: 1) bugfix · Round 1/2
complete   stack (package.json, .nvmrc), area (src/server/auth), base main, commits (git log),
           verify (package.json), evidence (default), PR (one)
partial    objective, files, scenarios
empty      branch name, out of scope, edge cases
```

Questions:

1. **Cause.** `isExpired` in `src/server/auth/session.ts` expires sessions at 29 minutes (`SESSION_TTL_MINUTES - 1`). Is the rule "expire after exactly 30 minutes of inactivity"?
   - Yes, expire at 30 minutes, not before *(recommended: matches the constant's name)*
   - Expire strictly after 30 minutes
   - The TTL itself should change
2. **Ticket and branch.** Which branch name?
   - `fix/ORD-<n>-session-expiry` *(recommended: matches `fix/ORD-31-…`; give me the ticket number)*
   - `fix/session-expires-early`
   - Write your own
3. **Scope.** The only test is for a fresh session. What should the agent do?
   - Fix the comparison and add boundary tests at 29, 30 and 31 minutes *(recommended)*
   - Fix only, no new tests
   - Fix and also review other callers of `isExpired`

Answers: "yes, at 30", "fix/ORD-58-session-expiry", "first option".

### Round 2

```
Type: bugfix · Size: small · Units: 1) bugfix · Round 2/2
complete   objective, files, branch, scenarios, edge cases, + defaults from round 1
empty      out of scope
```

1. **Out of scope.** While reading I saw duplicated date helpers in `src/server/utils/date.ts` and `src/web/utils/formatDate.ts`. Leave them alone?
   - Yes, out of scope *(recommended: unrelated to sessions)*
   - Include them

Answer: "yes". All required points resolved: stop.

### Delivery

```markdown
# Fix sessions expiring one minute early

## Objective
A session expires after exactly 30 minutes of inactivity, not at 29. Users stay signed in until the 30-minute mark.

## Task context
- Trigger: users report being logged out a minute early.
- Ticket: ORD-58.

## Repository context
- **Stack and versions:** Node 20.11.1 (`.nvmrc`), express 4.19.2, typescript 5.4.5, vitest 1.6.0 (`package.json`).
- **Area:** `src/server/auth`.
- **Instruction files to follow:** `AGENTS.md` (tests next to the file with vitest).
- **Files to change:**
  - Modify `src/server/auth/session.ts` — `isExpired` compares against `SESSION_TTL_MINUTES - 1`; it must expire at `SESSION_TTL_MINUTES`.
  - Tests: `src/server/auth/session.test.ts` — add boundary tests.
- **Patterns to follow:** vitest `describe`/`it` style already in `session.test.ts`.
- **Out of scope:** the duplicated date helpers in `src/server/utils/date.ts` and `src/web/utils/formatDate.ts`; changing the TTL value.

## Execution
- **Base branch:** `main` (default branch)
- **Branch name:** `fix/ORD-58-session-expiry` (chosen by the developer)
- **Commit convention:** Conventional Commits with the ticket key, e.g. `fix(ORD-58): …` (git log)
- **Pull requests:** one PR.

## Validation
**Scenarios**
1. Last seen 29 minutes ago → `isExpired` returns false.
2. Last seen 30 minutes ago → returns true.
3. Last seen 31 minutes ago → returns true.

**Edge cases**
- Last seen 29 minutes 59 seconds ago → false.

**How to verify**
- Lint: `npm run lint -- src/server/auth/session.ts src/server/auth/session.test.ts` (`package.json`)
- Tests: `npm test -- src/server/auth/session.test.ts` (`package.json`)

**Expected evidence**
- Scenarios 1–3 and the edge case: passing test output with the test names.
- Lint output for the changed files.
- A list of what was not verified.

## Open questions and assumptions
None.
```

> I have the context I need. Can I go ahead and execute this?

---

## Example 2 — large migration + feature with UI (Portuguese)

The conversation is in Portuguese because the request is. The reference file is in English; the interview is not.

### Input

> preciso de um ticket pra um agente: os pedidos precisam de histórico de status. tabela nova, backfill a partir do status atual e uma timeline na tela de pedidos. me ajuda a montar o prompt

### Reconnaissance (silent)

- `AGENTS.md`: data access only through `src/server/repositories/*`; reuse `src/web/components/ui`; strings in `src/web/locales/<lang>/*.json` (en, pt-BR); no imports from `src/legacy/`.
- `package.json`: knex 3.1.0, express 4.19.2, react 18.3.1; script `migrate` (`knex migrate:latest`).
- `migrations/`: knex JS migrations named `YYYYMMDD_description.js` with `up`/`down`.
- `src/server/repositories/OrderRepository.ts`: `updateStatus` writes `orders.status` directly.
- `src/web/pages/OrdersPage.tsx`: uses `Table`, `EmptyState`, `ErrorBanner`, `Button`; strings from `locales/en/orders.json`.
- `src/web/styles/breakpoints.ts`: `sm 480`, `md 768`, `lg 1200`.
- `git log` / `git branch -a`: Conventional Commits with `ORD-<n>`; branches `feat/ORD-…`, `fix/ORD-…`, `chore/ORD-…`.

### Gap analysis

- Units: 1) `migration` with backfill, 2) `feature` that writes history on status change and shows a timeline (UI).
- Migration with backfill + new UI → **large**, 6 rounds.
- Required beyond the base set: task context with visual reference, UI and design system, constraints, migration order, one branch or several, PR split, risks, edge cases.

### Round 1

```
Tipo: migration + feature (palpite) · Tamanho: large · Unidades: 1) migration 2) feature (UI) · Rodada 1/6
completo   stack (package.json), área (migrations, repositories, OrdersPage), padrões (AGENTS.md)
parcial    objetivo, arquivos
vazio      contexto/referência visual, UI, restrições, ordem da migration, branches, PRs, riscos,
           cenários, casos de borda
```

1. **Objetivo.** O que a timeline precisa mostrar?
   - Cada mudança de status com data/hora e quem mudou *(sugestão: é o que um histórico costuma responder)*
   - Só status e data/hora
   - Outro
2. **Dados.** Hoje `OrderRepository.updateStatus` grava direto em `orders.status`. Como o histórico deve ser gravado?
   - Na mesma transação de `updateStatus`, no repositório *(sugestão: segue o AGENTS.md, dados só pelos repositórios)*
   - Por trigger no banco
   - Decide você
3. **Referência visual.** Existe design para a timeline?
   - Arquivo de design (Figma, Claude Design ou outro): mande o link
   - Seguir o estilo de `OrdersPage` com os componentes de `src/web/components/ui` *(sugestão, se não houver design)*
   - Print de referência

Respostas: "status, data/hora e usuário", "mesma transação", "não tem design, segue a OrdersPage".

### Round 2

```
Tipo: migration + feature · Tamanho: large · Unidades: 1) migration 2) feature (UI) · Rodada 2/6
completo   objetivo, contexto (referência: OrdersPage), stack, área, padrões, arquivos (unidade 2)
parcial    UI (componentes ok; estados, responsividade, textos pendentes), arquivos (unidade 1)
vazio      restrições, ordem da migration, branches, PRs, riscos, cenários, casos de borda
```

1. **Backfill.** Quantos pedidos existem hoje, aproximadamente, e o backfill pode rodar dentro da migration?
   - Poucos (até ~100 mil): dentro da migration *(sugestão)*
   - Muitos: script separado, em lotes
   - Não sei
2. **Ordem e PRs.** Como dividir?
   - 2 PRs empilhados: (1) tabela + backfill, (2) gravação + timeline; o 2 só depois do 1 em produção *(sugestão: o backfill precisa existir antes da UI)*
   - 1 PR com tudo
   - 3 PRs: tabela, backfill, feature
3. **Estados da timeline.** O que mostrar em cada estado?
   - Carregando: skeleton; vazio: `EmptyState` "Sem histórico"; erro: `ErrorBanner` com tentar de novo *(sugestão: igual à OrdersPage)*
   - Outro

Respostas: "uns 40 mil, dentro da migration", "2 PRs empilhados", "igual à OrdersPage".

### Round 3

```
Tipo: migration + feature · Tamanho: large · Unidades: 1) migration 2) feature (UI) · Rodada 3/6
completo   objetivo, contexto, stack, área, arquivos, padrões, ordem da migration, PRs, UI (estados)
parcial    UI (responsividade, textos), riscos
vazio      nome das branches, cenários, casos de borda
```

1. **Nomes das branches** (empilhadas, padrão `feat|chore/ORD-<n>-…`):
   - `chore/ORD-<n>-order-status-history-table` e `feat/ORD-<n>-order-status-timeline` *(sugestão; me passe o número do ticket)*
   - `feat/ORD-<n>-status-history-db` e `feat/ORD-<n>-status-history-ui`
   - Escrever os meus
2. **Responsividade e textos.** Abaixo de `md` (768) a timeline vira lista vertical simples? Textos em en e pt-BR em `locales/*/orders.json`?
   - Sim aos dois *(sugestão)*
   - Outro
3. **Validação.** Quais cenários provam que funcionou? Proponho: (1) mudar status grava 1 linha no histórico, (2) backfill cria 1 linha por pedido existente, (3) timeline mostra as mudanças em ordem, (4) pedido sem histórico mostra o vazio.
   - Esses 4 *(sugestão)*
   - Adicionar outros

Respostas: "ORD-77, primeira opção", "sim", "esses 4 + o down da migration funciona".

The user then says "chega". Edge cases beyond those listed and the risk detail go to open questions.

### Delivery

```markdown
# Histórico de status dos pedidos com timeline

## Objetivo
Toda mudança de status de um pedido fica registrada (status, data/hora, usuário), os pedidos existentes ganham o histórico inicial por backfill, e a tela de pedidos mostra a timeline de cada pedido.

## Contexto da tarefa
- Gatilho: pedido do produto; hoje só existe o status atual.
- Referência visual: sem design; seguir `src/web/pages/OrdersPage.tsx` e os componentes de `src/web/components/ui`.

## Contexto do repositório
- **Stack e versões:** knex 3.1.0, express 4.19.2, react 18.3.1 (`package.json`).
- **Área:** `migrations/`, `src/server/repositories/`, `src/server/routes/orders.ts`, `src/web/pages/OrdersPage.tsx`.
- **Arquivos de instrução:** `AGENTS.md` (dados só pelos repositórios; reutilizar a UI kit; textos nos locales; nada de `src/legacy/`).
- **Arquivos a alterar:**
  - Unidade 1 (migration)
    - Criar `migrations/<YYYYMMDD>_create_order_status_history.js` — tabela + backfill com um registro por pedido a partir de `orders.status`, com `down`.
  - Unidade 2 (feature)
    - Alterar `src/server/repositories/OrderRepository.ts` — `updateStatus` grava o histórico na mesma transação; novo método para ler o histórico de um pedido.
    - Alterar `src/server/routes/orders.ts` — rota para o histórico de um pedido.
    - Alterar `src/web/pages/OrdersPage.tsx` — timeline do pedido.
    - Alterar `src/web/locales/en/orders.json` e `src/web/locales/pt-BR/orders.json`.
    - Testes ao lado de cada arquivo alterado (`*.test.ts`).
- **Fluxo parecido:** migrations em `migrations/` (formato e nomes); acesso a dados como em `OrderRepository`.
- **Padrões proibidos:** query fora de `src/server/repositories/`; trigger no banco; nova biblioteca de UI; imports de `src/legacy/`.
- **UI e design system:**
  - Componentes: `Table`, `EmptyState`, `ErrorBanner`, `Button` de `src/web/components/ui`.
  - Tela de referência: `src/web/pages/OrdersPage.tsx`.
  - Estados: carregando com skeleton; vazio com `EmptyState` "Sem histórico"; erro com `ErrorBanner` e tentar de novo; sucesso com a lista em ordem cronológica.
  - Responsividade: abaixo de `md` (768, `src/web/styles/breakpoints.ts`) vira lista vertical simples.
  - Textos: en e pt-BR em `locales/*/orders.json`.
- **Restrições:** o backfill roda dentro da migration (~40 mil pedidos); a migration precisa ter `down` funcional.
- **Fora do escopo:** filtros por status na timeline; editar ou apagar histórico; helpers de data duplicados.

## Execução
- **Branch base:** `main` (branch padrão)
- **Branches:** `chore/ORD-77-order-status-history-table`, e `feat/ORD-77-order-status-timeline` empilhada sobre ela (escolhidas pelo desenvolvedor)
- **Convenção de commit:** Conventional Commits com a chave, ex.: `feat(ORD-77): …` (git log)
- **PRs:** PR 1 = unidade 1, vai primeiro e precisa estar em produção antes do merge do PR 2; PR 2 = unidade 2.
- **Ordem da migration:** 1) criar a tabela; 2) backfill na mesma migration; 3) deploy; 4) só então o código que grava e lê o histórico. Rollback: `down` remove a tabela; seguro enquanto o PR 2 não estiver em produção.
- **Riscos:** backfill lento travando o deploy → medir em staging com volume parecido antes.

## Validação
**Cenários**
1. Mudar o status de um pedido → uma linha nova no histórico com status, data/hora e usuário.
2. Rodar a migration num banco com pedidos → uma linha de histórico por pedido existente.
3. Abrir um pedido com mudanças → timeline em ordem cronológica.
4. Abrir um pedido sem histórico → `EmptyState` "Sem histórico".
5. Rodar o `down` da migration → tabela removida sem erro.

**Como verificar**
- Lint: `npm run lint -- <arquivos alterados>` (`package.json`)
- Testes: `npm test -- <arquivos de teste alterados>` (`package.json`)
- Migration: `npm run migrate` num banco de teste com dados semeados; nunca dados de produção.

**Evidência esperada**
- Cenários 1, 3 e 4: saída dos testes passando com os nomes dos testes.
- Cenários 2 e 5: saída da migration e do rollback no banco de teste.
- Saída do lint dos arquivos alterados.
- Lista do que não foi verificado.

## Perguntas em aberto e suposições
- Casos de borda (mudança de status concorrente, pedido apagado): não discutidos → Suponha: gravação na mesma transação; histórico apagado junto com o pedido.
- Duração do backfill em produção: desconhecida → Suponha: ~40 mil linhas cabem na migration; se em staging passar de 1 minuto, pare e reporte.
```

> Já tenho o contexto necessário. Posso executar? Como a tarefa é grande e a entrevista já usou parte do contexto, posso também deixar o prompt pronto para você colar numa sessão nova.
