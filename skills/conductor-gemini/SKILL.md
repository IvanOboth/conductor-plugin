---
name: conductor-gemini
description: Orchestrate Gemini-first Conductor runs in Antigravity with Gemini 4 Neon (high) as orchestrator and primary builder, native Antigravity subagents and Python workflows for parallel work, subscription-clean cross-family checks via ask-codex (GPT-6.2 Sol) and ask-claude (Opus 5.5 / Fable 5.2), and desktop-and-phone HTML report artifacts. Use for /conductor-gemini, $conductor-gemini, "conductor gemini", "Gemini-first orchestration", or Antigravity-led multi-lane builds.
---

# Conductor Gemini

Run the full Conductor workflow in Antigravity with **Gemini 4 Neon High** (`gemini-4-neon-high`) as the orchestrator and primary builder. For multi-lane `/conductor-gemini` runs, keep the parent Antigravity session on **standalone Gemini 4 Neon High** (`gemini-4-neon-high`) — or, if using Antigravity Orchestrator mode, explicitly pin both Planner and Executor via `"orchestrator"` settings (see **The 3-layer stack** below) so `invoke_subagent` and `run_workflow` (`model="inherit"`) never silently drop critical work onto a lighter model. Gemini 4 Neon handles grounding, planning, work orders, implementation, refactors, migrations, tests, high-stakes writing, volume writing, media inspection, integration, and final acceptance. Independent cross-family verification goes to **GPT-6.2 Sol (`high`)** through `ask-codex` and/or **Claude Opus 5.5 (`high`) / Fable 5.2 (`high`)** through `ask-claude`.

**This profile exists to finish ambitious work on Google AI Ultra while keeping every provider subscription-clean.** Long-running migrations, multi-surface features, high-stakes client documents, media-heavy QA, vault work, and epics across sessions all belong here. Verification is part of the machinery that lets large work ship safely, not a reason to attempt less.

**The orchestrator never delegates three things: the plan, the work orders, the final review.** That holds in every profile.

## The 3-layer stack

Pick the lightest layer that matches the work's complexity and risk — do not over-orchestrate bounded lanes, and do not under-verify high-stakes forks:

| Layer | Role | Model setup & when to use |
|---|---|---|
| **1. Antigravity Orchestrator** | Within-lane `plan -> execute -> remand` loop | Explicitly pin both Planner and Executor in Antigravity `"orchestrator"` settings — never leave them on default auto-selection. Use **`Neon High` (Planner) + `Hydrogen High` (Executor)** for bounded CRUD, mechanical sweeps, and test-writing lanes. Use **`Neon High` (Planner) + `Neon Medium/High` (Executor)** — or **standalone `Neon High`** — for money, auth/RBAC, schema/data migrations, production data, and all filmmaking work. |
| **2. `/conductor-gemini`** *(this skill)* | Multi-lane orchestration, parallel fan-out, and cross-family verification | Parent on **standalone `Neon High`** coordinating parallel `invoke_subagent` / `run_workflow` lanes plus subscription-clean cross-family handoffs to **Opus 5.5 / Fable 5.2 (`ask-claude`)** for frontend taste, design critique, and high-stakes cold reads, and **GPT-6.2 Sol (`ask-codex`)** for independent code review and runtime verification. |
| **3. [`/council`](../council/SKILL.md)** | High-stakes multi-model audit & peer-review consensus | Use for hard architecture forks, ambiguous root causes, major design bets, or high-risk PRs where one reviewer is not enough. **Mode A (Review Council)** runs 3 independent model families read-only in parallel for `/10` PR scorecard rounds; **Mode B (Consensus Deliberation Council)** runs blind Round 1 investigation -> anonymized Round 2 peer review (`Proposal A/B/C`) -> Round 3 consensus verdict & dissent ledger. Never use `/council` for filmmaking (Gemini 4 Neon only) or trivial 1-file fixes. |

## Profile and shared authority

Set `profile: conductor-gemini` in the run and in every work order. This file owns model routing, fan-out transport, and review policy within the run. The mixed-model default assignments in [Conductor](../conductor/SKILL.md), the Codex-first assignments in [Conductor Core](../conductor-core/SKILL.md), and the single-family substitutes in [Conductor Claude](../conductor-claude/SKILL.md) do not override `profile: conductor-gemini`.

Read the current [shared Conductor source](../conductor/SKILL.md) for **What earns an agent**, **Sizing the fan-out**, **Review gates** (including **Review rounds: decide by round 2** and the significant-findings rule), **Closing step: run-report**, and the **Browser video evidence** block (**Choose evidence before recording**), and read [references/report-design.md](../conductor/references/report-design.md) for the **Report design contract** (including **Help Ivan understand**). Those shared contracts govern dispatch discipline, fan-out sizing, review round stops, report structure, and evidence selection without change. Reread the report design contract and the browser-evidence block from disk before authoring or revising any report.

## Subscription-clean transport rule (critical)

Every family bills to its own subscription. Never cross-bill a model onto the wrong quota pool:

- **Gemini 4 Neon (`high`, default; `xhigh` only to retry a thin `high` pass)** runs natively in Antigravity on Ivan's **Google AI Ultra** subscription:
  - **Inline** for scouting (`read_file`, `run_command`), single-tool mutations, or tightly-coupled edits where subagents would thrash the same files.
  - **`invoke_subagent`** for 1–2 bounded parallel Gemini lanes. Give parallel writers `workspace: "share"` (shared repo object store, isolated working tree) or `workspace: "branch"` (isolated clone); keep readers and verifiers on `workspace: "inherit"`.
  - **`run_workflow`** (Python `parallel()` / `pipeline()` over Gemini 4 Neon agents) for an enumerated work-list of 3+ independent items, staged build -> review pipelines, competing drafts, or fix-until-green loops.
  - When invoked headlessly from another harness, Gemini runs via `ask-gemini -m gemini-4-neon-high --no-fallback` (add `--write` for writable lanes). Always pass `--no-fallback` so the wrapper never silently switches to the paid API (`\$3/\$15` per Mtok, no tools).
- **Claude Opus 5.5 and Fable 5.2** MUST be dispatched exclusively via **`ask-claude`** (`ask-claude --plan -m opus`, `ask-claude --accept-edits -m opus`, `ask-claude --plan -m fable`) so they bill to Ivan's **Claude subscriptions** (Orca accounts). **NEVER** dispatch Claude through Antigravity `/swarm` Opus (which counts against Google AI Ultra quota), even if Claude accounts are exhausted — **GPT-6.2 Sol (`high`, `ask-codex`)** is the required cross-family gate for Gemini-authored work (routine and critical alike), and Opus 5.5 (`high`, `ask-claude`) is added on critical work when Claude accounts are available. If Claude accounts are exhausted, a passing GPT-6.2 Sol (`high`) review still clears critical work (labelled `cross-family (Sol); Opus skipped — Claude quota exhausted`); if both Sol and Opus are unavailable on a critical change, shipping is blocked. Keep `/swarm` strictly for interactive multi-agent Gemini boards if Ivan explicitly invokes `/swarm`.
- **GPT-6.2 Sol (`high`)** MUST be dispatched via **`ask-codex -m gpt-6.2-sol --effort high`** so it bills to Ivan's **ChatGPT/Codex subscriptions**. Always pass `-m` and `--effort` explicitly; never rely on `~/.codex/config.toml` defaults.

## Full scope (all repositories)

`conductor-gemini` works across **all repositories** — product repositories, client personal-data runs, and the vault (`~/dev/ivan-oboth`). There are no personal-data or vault bans on Gemini 4 Neon (Ivan, 21 Nov 2026).

When working inside the vault (`~/dev/ivan-oboth`), follow vault git discipline strictly:

- **Interactive Antigravity `conductor-gemini` session:** run `git pull --ff-only` before starting edits and before pushing, commit only explicit paths (`git add <file1> <file2>`), and push at checkpoints directly in `~/dev/ivan-oboth`.
- **Headless `ask-gemini --write` lanes inside the vault:** write only the assigned files and leave all git mutations (`git add`, `git commit`, `git push`) to the orchestrator.
- Never run `git add -A`, `git stash`, `git reset`, or `git checkout` on the shared vault tree.

## Routing

| Work | Model (effort) | Transport and reason |
|---|---|---|
| Grounding, plan, work orders, integration, final acceptance | Gemini 4 Neon (`high`) | Native Antigravity parent; orchestrator judgment |
| Implementation, refactors, migrations, terminal, CI, infra, tests | Gemini 4 Neon (`high`) | Inline, `invoke_subagent` (1–2 parallel slices, `workspace: "share"`/`"branch"` for writers), or `run_workflow` (3+ items / pipelines) |
| High-stakes writing (counterparty mail, proposals, board/client documents) | Gemini 4 Neon (`high`) | Primary author; optional second opinion / cold read via Opus 5.5 or Fable 5.2 (`ask-claude --plan -m opus` or `ask-claude --plan -m fable`) |
| Volume writing (internal docs, drafts, storyboards, routine mail) | Gemini 4 Neon (`high`) | Inline or `run_workflow` `parallel()`; external copy gets an edit pass |
| Media inspection (screenshots, recordings, images, audio) | Gemini 4 Neon (`high`) | Native Antigravity `read_file` or `ask-gemini -m gemini-4-neon-high --no-fallback --file <path>` |
| Cross-family diff review of Gemini-authored work | GPT-6.2 Sol (`high`) required; add Opus 5.5 (`high`) on critical work when Claude accounts are available | `ask-codex -m gpt-6.2-sol --effort high` is the required cross-family gate (routine and critical); add `ask-claude --plan -m opus` in parallel on critical work when Claude accounts are available or when requested. If Claude accounts are exhausted, a passing Sol review clears critical work; if both Sol and Opus are unavailable on a critical change, shipping is blocked. Retry Sol at `xhigh` only after a thin `high` pass; `high` is the ceiling for Opus 5.5 |
| Runtime and computer-use verification (mechanics) | GPT-6.2 Sol (`high`) | `ask-codex -m gpt-6.2-sol --effort high` (via `codex-computer-use` or [mobile-app-testing](../mobile-app-testing/SKILL.md)); Gemini 4 Neon or Opus 5.5 judges the pixels/UI |
| Optional UI design taste pass / second opinion | Opus 5.5 (`high`) | `ask-claude --plan -m opus` for critique (`ask-claude --accept-edits -m opus` only for an authorized exclusive-ownership UI slice) |
| Optional high-stakes writing second opinion / cold read | Opus 5.5 (`high`) or Fable 5.2 (`high`) | `ask-claude --plan -m opus` or `ask-claude --plan -m fable` |
| Bounded high-volume classify / extract | Gemini 4 Neon (`high`) or GPT-6 Luna (`high`) | `run_workflow` `parallel()`, or `ask-codex -m gpt-6-luna --effort high`; orchestrator reads output before acting |

**Effort.** Gemini 4 Neon defaults to `high`; use `xhigh` only to retry a thin `high` pass. GPT-6.2 Sol runs at `high` by default (critical reviews included) and retries at `xhigh` only after a thin `high` pass, never `max` by default. Opus 5.5 stays at `high` (ceiling, review lanes included); never `xhigh` or `max`. Fable 5.2 runs at `high` by default, never `xhigh` or `max` by default.

**Critical** means any of: it deploys to production or changes production data; it touches auth, payments, money, or personal data; it is a schema or data migration or otherwise hard to reverse; it is a client-facing deliverable (proposal, deck, flagship UI surface); or it changes the routing and agent configuration. Every `sev:1` item is treated as critical.

## Choosing the orchestration mode

Apply the shared **What earns an agent** gate first (scouting is yours via `read_file` / `run_command`; one tool call per item stays inline; every dispatched agent needs a concrete deliverable contract), then pick the Gemini transport:

| Shape | Mode |
|---|---|
| Single-file edit, scouting, or coupled chain | **Inline** (standalone `Neon High`, or Antigravity Orchestrator with explicit `"orchestrator"` pinning) — no subagent overhead |
| 1–2 bounded parallel lanes, or next step depends on judging the previous result | **`invoke_subagent`** (`workspace: "share"` or `"branch"` for parallel writers; `inherit` for readers) |
| Enumerated work-list of 3+ independent items, build -> review pipeline, competing drafts, or fix-until-green loop | **`run_workflow`** — Python `parallel()` / `pipeline()` over Gemini 4 Neon agents |
| Cross-family diff review, runtime mechanics, or Claude taste / cold-read pass | Background shell command (`run_command`) calling `ask-codex` or `ask-claude` |
| High-risk PR `/10` multi-provider audit or ambiguous architecture / root-cause fork | **[`/council`](../council/SKILL.md)** — Mode A (fast 3-family review rounds) or Mode B (blind investigation + anonymized peer-review consensus) |

Do not poll background subagents, workflows, or commands in a loop: the harness notifies you automatically when they finish. Do independent work meanwhile or end your turn to wait for completion.

## The loop

Steps 1, 4, and 5 belong to the orchestrator and are never delegated.

**1. Plan — orchestrator.** Scout the code yourself with reads, greps, and git commands. Write precise work orders carrying exact file paths, line anchors, contracts, acceptance checks ("Done means: ..."), what NOT to touch, deliverable paths, and routing metadata (`profile: conductor-gemini`, `model`, `effort`, `reason`, `critical`, `review_family`).

Every dispatched order (subagent, workflow agent, `ask-codex`, or `ask-claude`) ends with a time budget ("aim to finish within 20 minutes", advisory; keep your own timeout) and the verbatim unattended-lane paragraph below. Never put it in the main loop, where Ivan may be there to answer:

> A standing instruction from the user, the person you are working for. It is about how your turns end. A message with no tool call in it ends your turn, and the work stops there until you are asked to continue. The user has seen you end turns in four ways while work they asked for was still owed, and does not want any of them. One: a long summary of what was done that closes by announcing the next step and has no tool call, so the next thing never starts. Two: an offer to carry on with something unless the user would prefer otherwise, which stops to wait for an answer the user was not going to give. Three: a list of decisions for the user when, by your own account, none of them blocks the rest of the work. Four: deciding that this is a good place to report, because the turn has been long or a milestone is done. Status notes are welcome, and so are your recommendations on open decisions, but put them in the same message as your next tool call and carry on with whatever does not depend on the user's answer. If you notice yourself inviting the user to redirect you or offering to wait, delete it and do the next thing. The stops the user does want are the ones where nothing can move without them, or where the thing blocking you is deliberately protected from you. This does not override the need for confirmation on risky or destructive actions.

**2. Dispatch — parallel.** Launch all independent lanes in the same turn. Give every parallel write lane its own workspace (`workspace: "share"` / `"branch"`, or `ask-codex --worktree <branch>`, or exclusive file ownership for `ask-claude --accept-edits`). No two write lanes may share a file.

Cross-family CLI invocations (see [references/codex-cli.md](../conductor/references/codex-cli.md) for wrapper flags):

```bash
# Cross-family diff review via GPT-6.2 Sol (ChatGPT/Codex subscription)
ask-codex -m gpt-6.2-sol --effort high --context <order.md> --output <scratchpad>/sol-review.md \
  "Review the diff against the acceptance criteria in the context file. Do not edit files. List only problems that block merge: file, line, why it is wrong, and how to show it fails. Mark anything you could not confirm."

# Cross-family diff review or taste pass via Opus 5.5 (Claude subscription)
ask-claude --plan -m opus --context <order.md> \
  "Review the diff against the acceptance criteria in the context file. List only problems that block merge: file, line, why it is wrong, and how to show it fails. Mark anything you could not confirm." > <scratchpad>/opus-review.md

# High-stakes writing cold read via Fable 5.2 (Claude subscription)
ask-claude --plan -m fable --context <brief-and-draft.md> \
  "Cold-read this draft against the brief. List only concrete defects in clarity, tone, accuracy, or reader action." > <scratchpad>/fable-cold-read.md
```

**3. Cross-verify — different family eyes.** Every Gemini-authored change that ships gets cross-family review in fresh context (requirements and diff only, never the author's verdict):

- **Routine changes:** **GPT-6.2 Sol (`high`, `ask-codex -m gpt-6.2-sol --effort high`)** is the required cross-family gate (or Opus 5.5 `high` via `ask-claude --plan -m opus` if Codex is unavailable).
- **Critical changes or when requested:** **GPT-6.2 Sol (`high`)** is the required cross-family gate, and **Opus 5.5 (`high`, `ask-claude --plan -m opus`)** is added in parallel whenever Claude accounts are available. If Claude accounts are exhausted, a passing GPT-6.2 Sol (`high`) review still clears critical work (labelled `cross-family (Sol); Opus skipped — Claude quota exhausted`). If Codex is unavailable, a passing Opus 5.5 (`high`) review clears it (`cross-family (Opus)`). If **both** GPT-6.2 Sol and Opus 5.5 are unavailable on a critical change, **shipping is blocked** — never ship a critical change on Gemini self-review alone.
- **Runtime / UI verification:** GPT-6.2 Sol (`high`) runs the app, executes assertions, and captures screenshots or video (per the shared evidence gate). Gemini 4 Neon inspects the pixels directly (and may add an Opus 5.5 taste pass via `ask-claude --plan -m opus` for flagship UI). "Verified" from Codex means *it functioned*, never *it looks right*.
- **Review rounds: decide by round 2.** Follow the shared round-2 stop rule and significant-findings rule in [Conductor](../conductor/SKILL.md#review-gates-non-negotiable): round 1 lists blockers; round 2 reviews only the fixes and what they changed; from round 2 on, only significant findings block merge, and non-significant or out-of-scope items are dropped, not listed in a "Left as is" section or filed as issues; only an active production live fire outside the change gets at most two `LIVE-FIRE:` lines. Reviewers never file issues; the orchestrator owns the judgment.

Use honest coverage labels in every report:

| Label | Means |
|---|---|
| `cross-family (Sol + Opus)` | Both GPT-6.2 Sol (`high`) and Opus 5.5 (`high`) reviewed Gemini-authored work in fresh context |
| `cross-family (Sol); Opus skipped — Claude quota exhausted` | GPT-6.2 Sol (`high`) cleared a critical change while Claude accounts were exhausted |
| `cross-family (Sol)` | GPT-6.2 Sol (`high`) via `ask-codex` reviewed Gemini-authored work in fresh context |
| `cross-family (Opus)` | Opus 5.5 (`high`) via `ask-claude` reviewed Gemini-authored work in fresh context |
| `same-model, fresh context` | A separate Gemini 4 Neon lane reviewed a routine change in fresh context when neither Codex nor Claude could run (never used to clear a critical change) |
| `objective-gate` | Exact tests, typechecks, runtime assertions, or screenshots verified by the orchestrator |
| `orchestrator-only` | Inline work without a separate reviewer |

**4. Review and integrate — orchestrator.** Read every lane's report and actual diff (`git diff --stat` and the changed files). Merge isolated branches/workspaces yourself, resolve conflicts by hand, and run the full applicable test suite and checks before accepting. Rejected work returns as a revised work order naming what was wrong and what correct looks like.

**5. Publish the HTML report (mandatory deliverable).** Matching the shared Conductor contract, every `conductor-gemini` run builds or updates a self-contained, desktop-and-phone responsive HTML report under `<repo>/.conductor/reports/` (keyed `issue-<n>.html` or `<YYYY-MM-DD-slug>.html`; ensure `.conductor/` is gitignored) following [references/report-design.md](../conductor/references/report-design.md) — scaled concisely for small runs, and carrying full evidence, diagrams, and visual proof on larger runs:

- **Contents:** what was asked and built, decisions made and why, tests run (exact commands and results), cross-family review verdicts with honest coverage labels, and visual proof (screenshots or video strictly per the shared **Choose evidence before recording** gate — never record video of opening a static report).
- **Publish and verify (Bench):** run `~/bin/report-link.py <report-path>`, verify HTTP 200 and rendering at desktop and 390px phone widths at `https://bench.tailb5d047.ts.net/reports/<repo>/<file>.html`, and give Ivan the clickable URL labelled **private — Tailscale access required** — never a local disk path.
- **Close:** run `run-report` where available and authorized, and end your final reply with **Needs you**, **Changed**, **Found**.

## Long-horizon runs

Follow the shared **Long-horizon runs** contract in [Conductor](../conductor/SKILL.md#long-horizon-runs): persist the work-list to disk (`.conductor/work-list.md`), phase epics into waves (contract -> fan-out -> integrate/verify), checkpoint and commit at wave boundaries, and resume from committed branches plus the on-disk work-list rather than memory.
