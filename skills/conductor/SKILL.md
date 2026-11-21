---
name: conductor
description: Coordinate mixed-model work across Claude Code and Codex. Keep the current main agent responsible for grounding, work orders, integration and final acceptance; delegate bounded execution and independent review when worthwhile. Produce readable explanatory HTML reports with evidence chosen for the task. Use for /conductor, $conductor, "conduct this", "orchestrate at high", "mixed-model build", "use opus + codex", "use Claude and Codex", "have codex verify", "have codex write the blocks", "writing lane", "mixed-model ultracode", or a multi-stream build requiring independent implementation and review.
---

# Conductor — mixed-model orchestration

## Profile scope

This entry point selects the default mixed-model profile. For Gemini-first orchestration in Antigravity with Gemini 4 Neon as orchestrator and builder plus subscription-clean Codex/Claude cross-family checks, use [Conductor Gemini](../conductor-gemini/SKILL.md). For Codex-first orchestration with optional Opus and no Fable dependency, use [Conductor Core](../conductor-core/SKILL.md). For a run with no Codex lane at all — every ChatGPT account in cooldown, Codex unreachable, or the work must stay in one vendor — use [Conductor Claude](../conductor-claude/SKILL.md), which carries every role on Opus 5.5 and Fable 5.2 under honest coverage labels (Gemini 4 Neon may take Sol's review when Codex is merely down; see that skill). The active profile owns model selection, fan-out and review acceptance throughout the run, supporting skills and bundled-agent defaults included; the mixed-model mandates below do not override `profile: conductor-core` or `profile: conductor-gemini`. Peer profiles share this file's installation, report design, explanation, delivery and evidence-selection contracts, with their own routing and review policy. Ordinary `$conductor` behavior is unchanged.

**What this is for.** Conductor accomplishes work too large, too long-running or too multi-stranded for one agent in one pass — a repository migration, a feature with design, data and copy strands, an epic across sessions, a research or document build that runs for hours. The unit of ambition is the *run*, not the turn; the work orders, lanes, review gates and report are machinery for holding a large piece of work together until it finishes and can be trusted. **Verification is part of that machinery, not its purpose**, and the restraint sections direct capacity to where it produces work — they are not a reason to attempt less.

**The premise.** Ultracode is not a model — it is `xhigh` reasoning plus a standing "workflow everything" instruction, and fan-out needs neither: `Workflow` and `Agent` work at any effort. Conductor gets Ultracode-grade output for a fraction of the cost by running the main loop on Opus 5.5 at `high`, fanning out **on demand**, and spending high-judgment tokens only where judgment lives — decomposition, work orders, review, integration.

**The orchestrator never delegates three things: the plan, the work orders, the final review.** Everything else is dispatched. This holds whichever model runs the main loop.

## Model routing and lanes

Current as of 21 Nov 2026: GPT-6.2 Sol replaced GPT-6.1 Sol in every role (20 Nov, bench-factory#1176), and Gemini 4 Neon is an approved builder alongside Opus 5.5, owns high-stakes writing and media reads, and has no personal-data or vault restrictions (Ivan, 21 Nov 2026). This section owns model and effort selection for the default profile and overrides conflicting effort advice in supporting skills; a skill cannot change the effort of an already-running parent or worker. Dated benchmarks, retired models and the reasons behind past changes are in [references/routing-history.md](references/routing-history.md).

**In one line:** Opus 5.5 and Gemini 4 Neon (`gemini-4-neon-high`, `ask-gemini`) build; Gemini 4 Neon also takes high-stakes writing, media reads, shadow reviews, and Sol's review when Codex cannot run; GPT-6.2 Sol (`gpt-6.2-sol`) is the only GPT model for reviewing, exploring and computer use; Fable 5.2 takes gates, critical design, escalation and optional writing cold reads; GPT-6 Luna takes bounded volume and never reviews.

**Before launching**, record the lane's model, effort, task-specific reason, acceptance criteria, severity and critical class in the work order's `routing.json`, and pass model and effort explicitly — never rely on parent defaults (use agent frontmatter or a CLI when the Agent tool cannot set effort). Claude lanes go through `Agent` / Workflow `agent()` with `model: "opus"` or `"fable"` and an `effort`, or a bundled agent; Codex lanes through `ask-codex -m <model> --effort <level>`; Gemini lanes through `ask-gemini -m gemini-4-neon-high --no-fallback`. Workers get bounded orders and no recursive fan-out unless budgeted; existing lanes keep their launch settings.

| Lane | Model (effort) | Send it |
|---|---|---|
| Judgment (orchestrator) | Opus 5.5 (`high`), every epic; Fable 5.2 (`high`) only for a `sev:1` epic while `~/intake-triage/EPIC_FABLE` reads `on` | Plan, work orders, reading every lane's output, integration, the user-facing summary |
| Plan gate, fresh context | Fable 5.2 (`high`) when Opus wrote the plan; Opus 5.5 (`high`) when Fable wrote it; GPT-6.2 Sol (`high`) alone when Opus wrote it and Fable cannot be used | Before wave 1 of a `sev:1`, `sev:2` or critical-class epic (see **Long-horizon runs**) |
| Epic close | Fable 5.2 (`high`) when Opus orchestrated; Opus 5.5 (`high`, fresh context) beside GPT-6.2 Sol (`high`) when Fable orchestrated; GPT-6.2 Sol (`high`) alone when Opus orchestrated and Fable cannot be used | The same epics, with the close checks in **Long-horizon runs** |
| Design | Opus 5.5 (`high`), `design-lane`; Fable 5.2 (`high`) for critical surfaces | Anything where "looks right" is the acceptance test. Never GPT-6.2 Sol |
| Execution | Opus 5.5 (`high`), `exec-lane`; Gemini 4 Neon (`high`, `ask-gemini -m gemini-4-neon-high --no-fallback --write`) | Implementation, refactors, migrations, terminal, CI and infra, tests, long execution of an established plan |
| Mechanical sweep | Opus 5.5 (`low`), `bulk-lane`, one lane per item; GPT-6.2 Sol (`high`) as overflow; Luna (`high`) when it only classifies or extracts | Renames and contract sweeps with exact anchors |
| Bounded high-volume | GPT-6 Luna (`high`) | Intake packets, classifying, extracting, first-pass checks; a stronger model reads the output first |
| Investigation and exploration | GPT-6.2 Sol (`high`) | Tracing behaviour, logs, mapping a subsystem, bug exploration and the cross-family second attempt on a bug hunt; cites file:line. Investigation that must change code goes to Opus 5.5 |
| Ops and Codex overflow | GPT-6.2 Sol (`high`) | Ops, runbook and business-workflow automation, agentic science; well-specified implementation only when Claude quota is tight |
| Long reasoning | Fable 5.2 (`high`) | Ambiguous architecture; the second attempt when Opus 5.5 and GPT-6.2 Sol have both missed |
| Research and synthesis | Fable 5.2 (`medium`) | Deep research, agentic search, many sources into one finding |
| Adviser | Fable 5.2 (`medium` as an `Agent` call; the native adviser's effort is not documented) | One question from a stuck lane or the orchestrator, with its evidence, before escalating the lane. It answers; it does not take over |
| Writing (high stakes) | Gemini 4 Neon (`high`, `ask-gemini -m gemini-4-neon-high --no-fallback`); Fable 5.2 (`write-lane`) or Opus 5.5 (`Agent`) as optional second opinion / cold read | Counterparty mail, proposals, board documents, client-facing deliverables from a blank page |
| Writing (volume) | Opus 5.5 (`medium`) | Prompt packages, storyboards, internal docs, drafts, routine mail; external copy gets an edit pass |
| Diff review (cross-family) | GPT-6.2 Sol (`high`), critical work included, via `codex-review`; `xhigh` only as the retry after a thin `high` pass | Every Claude- or Gemini-authored change that ships, and the review before an unattended merge |
| Review when Sol cannot run | Route by author family: Claude-authored → Gemini 4 Neon (`gemini-4-neon-high`, `cross-family (Gemini)`), then Opus 5.5 (`high`, fresh context, `same-model, fresh context`); Gemini-authored → Opus 5.5 (`high`, fresh context, `cross-family (Opus)`), never Gemini; never Fable 5.2 | Sol's review, routine or critical, while Codex is out of quota or down |
| Shadow review (trial) | Gemini 4 Neon (`gemini-4-neon-high`), in the background | Optional and non-blocking, beside GPT-6.2 Sol on the same diff, for 3–5 days from 20 Nov 2026 |
| Judgment review | Opus 5.5 (`high`), `verify-lane`, fresh context | Critical work GPT-6.2 Sol wrote, and Fable- or GPT-authored work |
| Runtime verification (mechanics) | GPT-6.2 Sol (`high`) via `mobile-app-testing` (native) or `codex-computer-use` (web, other GUI) | Run the app, capture the evidence the gate selects, assert the result independently |
| Runtime verification (judgment while driving) | Opus 5.5 (`high`) driving `agent-browser` (own `--session`); GPT-6.2 Sol when mechanical | The next click depends on what is on screen |
| Media second read | Gemini 4 Neon, `ask-gemini --file <path>` (repeatable) | Screenshots, recordings, images or audio against the order's expectation. You and the taste lane still judge the pixels |

**Effort.** `low`: Opus 5.5 mechanical sweeps with exact anchors. `medium`: Opus 5.5 volume writing; Fable 5.2 research, synthesis and adviser `Agent` calls. `high`: everything else, every review lane and every GPT-6.2 Sol, Luna and Gemini lane included. **`high` is the ceiling for Opus 5.5**, review lanes included (Ivan, 12 Nov 2026); past it, move to Fable 5.2 or a cross-family attempt. GPT-6.2 Sol runs `xhigh` only as the retry when a `high` pass came back thin. Fable 5.2 never runs `xhigh` or `max` by default, nor `low` for anything that must look something up. Never `max` by default. Another effort needs an explicit user request or a task-specific reason in the order; role names and duration do not raise it (route by the work's bottleneck: hours of runtime, file count or document length alone choose neither model nor effort), and old `xhigh` settings are not carried forward. Read `~/.codex/config.toml` rather than assuming the Codex default.

**Review classes.** **Critical** means any of: it deploys to production or changes production data; it touches auth, payments, money or personal data; it is a schema or data migration or otherwise hard to reverse; it is a client-facing deliverable; or it changes the routing and agent configuration. Decide it per work order. **Severity** (10 Nov 2026): every issue and epic carries one label, `sev:1` to `sev:4`, the worse of its impact and its risk, with older labels as a floor (`priority:critical`, `priority:p0`, `urgent` mean at least `sev:1`; `priority:high`, `priority:p1`, `priority:blocking`, `revenue` at least `sev:2`). It sets the queue and which epics get the plan gate and the epic close; the definitions are in the "Severity" paragraph of `~/.claude/CLAUDE.md`. Severity never lowers review depth.

**Who reviews whom.**
- The reviewer is always a different model from the author; cross-family review needs a different family (GPT-6.2 Sol on Luna output is same-family and labelled so).
- Opus-authored work, routine or critical (money, auth, personal data, migrations, production data and every `sev:1` item included): GPT-6.2 Sol at `high`, plus your own read of the diff. No second Opus review runs on critical Opus-authored work (Ivan removed it on 18 Nov 2026).
- When GPT-6.2 Sol cannot run (Codex out of quota or down), route the fallback by the author's model family: for Claude-authored work, Gemini 4 Neon takes the review as a genuine cross-family reviewer (`cross-family (Gemini)`), with Sol's order (a non-zero exit or empty report falls back to Opus 5.5 `high` in fresh context, requirements + diff only, `same-model, fresh context`); for Gemini-authored work, Opus 5.5 `high` in fresh context takes it (`cross-family (Opus)`), never back to Gemini. Never Fable 5.2 (Ivan, 17 Nov 2026).
- GPT-6.2 Sol reviews, explores and verifies; Gemini 4 Neon builds (`ask-gemini --write`), writes high-stakes prose, reviews (Sol's stand-in, the shadow trial) and reads media (or orchestrates under [Conductor Gemini](../conductor-gemini/SKILL.md)). Sol never judges design or writes the plan, except its no-Fable plan gate and epic close. Luna intake is advisory: its packet runner cannot dispatch workers, change labels, advance intake state or hold merge authority, and ambiguity goes to the orchestrator (ivan-oboth#85).
- Every review order asks: "List only problems that block merge: file, line, why it is wrong, and how to show it fails. Mark anything you could not confirm." Higher GPT review effort needs an observed failure and a recorded reason.

**Where Fable 5.2 fits.** When Fable wrote an epic's plan, its plan gate and close go to Opus 5.5 in fresh context; when Opus planned and Fable cannot be used, GPT-6.2 Sol does the whole plan check and close alone (no Opus fallback for these gates; if Sol cannot run either, the gate is reported as not run). For blank-page knowledge work, Opus 5.5 starts routine and internal documents with Fable as the first escalation; high-stakes writing (counterparty mail, proposals, board/client documents) goes to Gemini 4 Neon with Opus 5.5 or Fable 5.2 as optional second opinion / cold read. The **native adviser**, where a host enables it (Claude Code 2.1.321+; `"advisorModel": "fable"`, `claude --advisor fable` or `/advisor fable`; off with `/advisor off` or `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`), is inherited by subagents and consulted before committing to an approach, when an error recurs and before declaring done; an order can ask for it, and its usage counts as Fable usage. Conductor Core never selects Fable: a `sev:1` epic under Core is orchestrated by GPT-6.2 Sol.

**Where GPT-6.2 Sol fits.** It costs \$2/\$10 per Mtok and runs on ChatGPT Pro quota in a 5-hour window, so Codex is also the place for volume when Claude quota is tight. Account homes can default to older models: every Codex lane names `-m` and `--effort` (`ask-codex -m gpt-6.2-sol --effort high`). CLI version and context window: [references/codex-cli.md](references/codex-cli.md).

**Where Gemini 4 Neon fits (21 Nov 2026).** `ask-gemini` runs it headless through the Antigravity CLI on Ivan's Google AI Ultra subscription; repository runs are read-only by default, and `--write` enables edits and commands. Always pass `--no-fallback`: otherwise the wrapper silently switches to the paid API (\$3/\$15 per Mtok), which has no tools and cannot read the repository. Gemini 4 Neon is an approved builder alongside Opus 5.5 (`ask-gemini --write`), the default for high-stakes writing (with Opus 5.5 or Fable 5.2 as optional second opinion / cold read), and the media second read (`--file`). In the **shadow trial**, record both finding lists in the run report for the catch-rate comparison; it never gates a merge, and a finding only Gemini raised is checked against the code like any other before anyone acts on it. It works across all repositories — product repos, client personal-data runs, and the vault (personal records included) — with no personal-data or vault restrictions (Ivan, 21 Nov 2026). For Gemini-led orchestration in Antigravity, use [Conductor Gemini](../conductor-gemini/SKILL.md).

**How to apply.**
- Defaults, not limits: if a lane falls short, ask the adviser its one question, re-run at higher effort up to the ceiling, then change the model, without asking. Judge the output, not the price. When axes conflict on anything that ships: the lane's own axis (reasoning for plans and reviews, autonomy for execution) > steerability > taste > cost per task.
- In the default Claude profile, the orchestrator stays Claude: it needs the 1M window, the harness and the skills, and cross-family review exists only if reviewers are another family; use `conductor-gemini` when running on Antigravity / Gemini 4 Neon.
- Design orders ban Opus 5.5's stock styles unless the design system already uses them: cream or off-white backgrounds, italic accent words in headings, numbered "01 / 02 / 03" labels, monospace labels, pill-shaped buttons. Writing orders state audience, register, length ceiling, the reader's one action, banned phrases and a voice sample; volume writing asks for plain, literal sentences.
- **The signature move:** each lane is checked by the other family through the dedicated skills (`codex-review`, `mobile-app-testing`, `codex-computer-use`). "Verified" from a Codex lane means *it functioned*, never *it looks right*: you judge the pixels.
- **Never dispatch a lane as `general-purpose`:** it inherits the session's model and effort. Use the bundled agents — `design-lane`, `exec-lane` (opus/high), `bulk-lane` (opus/low), `verify-lane` (opus/high), `write-lane` (fable/high) — or pass `model` and `effort` (Claude Code 2.1.292+). Lanes use the 5-minute prompt cache (`subagentPromptCacheTtl: "5m"`, `experimental.cacheTtl: 5m`, `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL=5m` on epic runs), so keep long waits and suites CI already runs out of lanes.
- Cross-family routing is also availability insurance. Never Haiku or Sonnet for judgment work; never Fast mode on a dispatched lane.

## One source, installation paths

This is the shared Conductor skill for Claude Code and Codex; the maintained source is `skills/conductor/SKILL.md` in the Conductor plugin repository, and its cold reference files are in `skills/conductor/references/`. Personal entry points use a directory link or a minimal discovery file that reads that source (`scripts/link-personal-skills.py` sets them up); edit the resolved source, not harness variants. On every new report or substantial report revision, reread [references/report-design.md](references/report-design.md) (the Report design contract) and the **Browser video evidence** block at the end of this file (the evidence gate) from disk before authoring and before publication: an injected skill, older report or saved template may be stale, and a running session keeps the text it loaded until it rereads.

**Installation paths.** In a plugin installation use `${CLAUDE_PLUGIN_ROOT}` for bundled scripts; for a linked checkout, resolve this SKILL.md symlink and set `CLAUDE_PLUGIN_ROOT` to its plugin root (the directory holding `skills/`, `scripts/` and `agents/`), never the working repository. Bench-specific report commands apply only on Ivan's configured Bench; elsewhere use the configured report surface and verify the served file.

## Harness-specific tools, shared contract

The current main agent remains the orchestrator, whether it is Claude or Codex; the plan, work orders, report requirements, evidence policy and acceptance gates are shared. A skill does not change the parent's model, and no table here grants capabilities or authorization: use only the tools the harness has, within its concurrency and permission limits.

- **Claude Code parent:** Agent/Workflow tools for Claude lanes, `ask-codex` for Codex and `ask-gemini` for Gemini. Named bundled agents only when installed.
- **Codex parent:** collaboration agents for bounded Codex execution, and `ask-claude --plan --model <model> --context <order>` for independent Claude review (`--accept-edits` only for an authorized writable lane with exclusive file ownership). A Codex child is the same family, not a cross-family reviewer.
- **Waiting:** use the harness's real completion mechanism (Claude background jobs notify; Codex resumes a running tool session with its wait/poll API). Do independent work meanwhile and keep Ivan informed.
- **Safety and ownership:** preserve dirty user changes and serialize overlapping writes. Commits, pushes, PRs, issue comments, messages and deployments need the user's authorized scope; a checklist grants none. Never deploy to production without explicit authorization.
- **Independent review:** check the implementing family with the other family; another Codex review of a Codex change is mechanics-only. Claude judges screenshots for visual quality; the main loop inspects the artifacts and runs objective checks.

## Orca lanes or one session?

Decided 17 Sep 2026 on bench measurements ([references/routing-history.md](references/routing-history.md#orca-lanes-the-17-sep-2026-measurement)): tokens are the same either way, so the cost is lifecycle and integration — an Orca lane leaves a 330–530 MB Claude session and its MCP children running until closed, and ends at a draft PR nobody integrates once the orchestrator is gone.

- **Default: one session.** Epics run as a conductor run here — `Agent`/`Workflow` lanes, `isolation: "worktree"` for writers, cross-family review, merge behind the gates, one review page — and the run ends its lanes and integrates them itself.
- **Orca lanes only** when Ivan wants to watch or steer a lane live, or the lane must outlive the orchestrator (a multi-hour build): Orca's value is visibility and steering, not parallelism.
- **Lifecycle rule for every Orca lane:** the terminal closes when its lane-report is written (`orca terminal close --terminal "$ORCA_TERMINAL_HANDLE" --json` as its last command; the poller does this itself, `POLLER_KEEP_TERMINAL=1` keeps one open); the worktree is removed after its PR merges (`orca worktree rm --worktree path:<path> --run-hooks --json`, never `--force` on a dirty tree; on the bench `~/bin/bench-worktree-rm <path>`, which refuses unpushed or uncommitted work with exit 2, while its `--force` saves that work first); an evidence page is produced (`tools/evidence-page.py`).
- The idle reaper closes what slips through (terminals idle > 24 h) and the dashboard shows the terminal budget.

## Execution slices on a CI box or boat (Bench only)

On Ivan's Bench an independent execution slice whose order stands alone can run on a CI box or boat sandbox through `conductor-box-lane run`. Before using it, and before any in-process fallback for a slice that went out, read [references/box-lanes.md](references/box-lanes.md) (conditions, exit codes, the one-writer-per-branch rule). Other hosts ignore this.

## When to invoke (on-demand, not always)

Reach for conductor's fan-out when the work has **separable lanes** — design vs mechanical vs writing vs verification — or a **work-list to pipeline** over, or a **finding that needs independent verification** before it ships. For a single-file edit, a lookup, or tightly-coupled work where lanes would thrash the same files, skip it and work inline (or use plain all-Claude `Workflow` for tightly-coupled fan-out). Don't force a task to split that doesn't want to.

## Turn-by-turn or Workflow — pick the orchestration mode

Once lanes are earned, choose who holds the plan. Both modes are legitimate:

- **Turn-by-turn** — you orchestrate. Lanes go out as `Agent` calls or background `Bash` → `ask-codex` / `ask-gemini`; you decide the next step after each result, and each result lands in your context.
- **`Workflow`** — a script orchestrates. `agent()`/`parallel()`/`pipeline()` run in the background, intermediate results stay in script variables, and only the final return reaches you (a phased line in the task panel and `/workflows`).

| Signal | Mode |
|---|---|
| 1–2 lanes, or 3 lanes of different kinds with no shared shape | Turn-by-turn |
| The next order depends on a judgment you make after reading the previous result | Turn-by-turn — a Workflow takes no mid-run input |
| A single Codex lane, or Codex lanes you want to adjust between | Turn-by-turn |
| An enumerated work-list of 3+ independent items | **Workflow** — `pipeline()` one agent per item |
| Findings that must be adversarially verified before they are reported | **Workflow** — review → verify pipeline |
| Competing drafts or approaches judged against each other | **Workflow** — `parallel()` attempts + judges |
| A fix-until-green or find-until-dry loop, or a run long enough that an interruption would hurt | **Workflow** — the loop lives in the script; completed agents resume from cache |

Mixed runs are normal: scout and hold the judgment calls turn by turn, hand the enumerated wave to a Workflow, then review its result turn by turn. Never dispatch a pinned taste or judgment lane (`design-lane`, `verify-lane`) to scout.

## What earns an agent (gate this before sizing anything)

Sizing answers *how many*; this answers *whether*, and runs first. A wasted agent costs its full run and returns nothing.

**Scouting is your job, not a lane.** Scout with `Grep`, `Glob`, `Read` and `Bash`, not by dispatching agents to look: delegated discovery is the most common waste in a conductor run — each agent burns a context and returns prose you must re-verify, answering worse than a two-second grep. **If a grep, find, `ls`, `git log` or file read would answer it, run the command.** Reading the code yourself is what makes the work orders precise enough for cheap lanes to succeed.

**Every agent needs a deliverable contract:** a file written, a diff applied, a report at a known path, a verdict with citations. "Investigate X and report findings" has no completion condition; if you cannot state what lands when it is done, you do not have a work order yet.

**An agent must be worth more than its overhead** (loading context, understanding the order, reporting back). **If an item is one tool call — a single mutation, one CLI invocation, a two-second edit — run it inline however many items there are.** Async provider jobs (renders, builds, CI, queued API work) already run in parallel on the provider: submit them and read the results; an agent that waits on them is idle. When you go inline, name the real reason — "coupled chain" and "one tool call each" are different arguments, and calling small work coupled is how genuinely parallel work gets serialized.

**Fan out over a work-list you already have — never to produce one.** Discovery is one cheap step you run yourself (`grep -rl`, `git diff --name-only`); the fan-out happens to the items it returns.

Four questions before any dispatch:

1. **Could a shell command answer this?** → Run the command.
2. **What artifact does this agent return?** → No answer means no dispatch.
3. **Is this discovery or execution?** → Discovery is yours. Execution and verification fan out.
4. **Is the item bigger than the agent's overhead?** → One tool call per item means inline.

## Sizing the fan-out

**Lane count follows the work, not a habit.** The four lane kinds and the bundled lane agents are a menu, not a quota: one `design-lane` can be dispatched twelve times, and 20 independent items mean 20 agents. **The size guideline is a ceiling, not a target** (`large` means *up to* 50): derive the count from the work-list you scouted, then check it against the ceiling. Under-fanning silently drops coverage; over-fanning (inventing sub-tasks, stacking verifiers on an undisputed finding) burns tokens for nothing.

Match the count to the shape of the work:

| Shape | Sizing |
|---|---|
| Independent items (files, endpoints, findings, sources) — **already enumerated** | **One agent per item.** Don't batch items into a single agent to keep the count down — that's how coverage gets silently dropped. |
| Finding out *what* the items are | **Zero agents.** That's a grep, and it's yours. |
| Adversarial verification of a finding | 3 refuters, or 3 distinct lenses when the finding can fail in more than one way |
| Competing approaches worth weighing | 3-5 independent attempts + judges, not one attempt iterated |
| Open-ended hunting where the *answer set* is unknown (bugs, edge cases, security holes) | Loop until 2 consecutive rounds find nothing new — a fixed count misses the tail. Distinct from scouting: no grep answers "what bugs exist", but a grep does answer "which files exist". |
| One coupled change | 1 agent. Splitting coupled work costs more than it saves. |
| Many items, but each is a single tool call (mutations, CLI invocations, one-line edits) | **0 agents — inline.** Independent ≠ worth an agent. Agent overhead exceeds the work. |
| Jobs that run async on a provider (renders, builds, CI) | **0 agents.** Submit them, then read results. The provider is the parallelism. |

**Spend the width where the agents are cheap.** A 30-file mechanical sweep is the right place for a wide fan-out (`bulk-lane`, Sol overflow, Luna for classify/extract), one agent per file; hedging to 4 agents leaves 26 files unexamined. Keep the expensive lanes (Fable 5.2, `high` judgment) narrow.

**Wide also survives interruption better:** on resume, cached results stop at the first unfinished agent, so many small agents keep more progress than a few long ones.

**The real limits** (none of which is 3): the session size guideline (`small` <5 · `medium` <10, the default · `large` <50 · `unrestricted`; `workflowSizeGuideline` or `/config workflowSizeGuideline=large`) is advice, not a cap — read the value in force from the Workflow tool's description or the `Running in background` line, not a config file. Up to 16 agents run concurrently and the excess **queues** (100 items still all complete); a run allows 1,000 agents; a `parallel()`/`pipeline()` call takes 4,096 items (a hard error above, never silent truncation); a "+500k"-style directive is a hard token ceiling. Runs above 25 agents or ~1.5M projected tokens show an advisory `Large workflow` warning: proceed when the work-list justifies it, and when you bound coverage for cost, **`log()` what you dropped** so a partial sweep never reads as a complete one.

The restraint elsewhere in this skill is about *unnecessary* splits, not a reason to under-serve genuinely parallel work — but it applies with full force to discovery: width is for executing and verifying a known work-list, never for assembling one.

## Long-horizon runs

A run that spans hours or sessions fails for different reasons than a run that fits in one turn. It does not usually fail on reasoning; it fails because state was held only in a context that ended. Three things make a large run survive.

**The work-list is an artifact, not a memory.** Write it to a file — the items, their owners, their status (queued / running / done / blocked), and the deliverable path for each. A run that keeps its plan only in the orchestrator's context loses the plan at compaction, at a usage limit, or when a session ends. When the work-list is on disk, any later session — or you after compaction — resumes by reading it.

**Phase the ambition, don't flatten it.** An epic is waves, not one enormous fan-out: wave 1 establishes the contract (the schema, the shared component, the interface everything depends on) in one or two lanes; wave 2 fans wide over items with a stable contract; wave 3 integrates and verifies. **Plan gate** (`sev:1`, `sev:2` and critical-class epics only): before wave 1, send the plan, the shared contract and the slice list to a fresh-context lane that did not write the plan (models in **Model routing and lanes**); it returns the structural risks, the missing contracts and a corrected slice order, and you still own the plan and write the work orders. **Epic close** (the same epics): after the last wave, one judgment pass by a model other than the orchestrator's reads the integrated diff against the epic's acceptance before the run reports done. Slice-level review is unchanged; other epics get no plan gate and close on your own read. `Workflow`'s `phase()` names wave dependencies, and `pipeline()` starts an item's later stage as soon as its earlier one lands.

**Every epic-close order asks two questions by default** (11–15 Nov 2026 epic runs):
- **Readers left behind.** When the epic moves a rule (how something is computed, aged, counted or labelled), the close order asks: "Readers left behind: search the whole tree for anything that still decides this by itself." Keep time in the plan for one or two more children after it.
- **Completeness claims against the inventory.** When a document, reader table or code comment in the epic claims completeness ("every reader", "all callers"), check that completeness table against the inventory before the close, and attach the inventory where the claim points.

**Checkpoint at boundaries.** At the end of each wave, persist what exists: commit the lanes that landed, update the work-list, and write what remains. Interrupted work that was committed is recoverable; interrupted work held in a lane's context is gone. This is why long write lanes commit incrementally rather than saving everything for a final message, and why many small lanes beat a few long ones — on resume, cached results stop at the first unfinished lane and everything after it re-runs.

**Resuming.** A `Workflow` resumes with `resumeFromRunId`: completed `agent()` calls with unchanged prompts return cached results instantly and only edited or new calls re-run. Stop the prior run before resuming it. For a run that outlived its session entirely, the work-list file plus the committed branches are the resume point — read them, re-scout what changed, and dispatch only what remains.

**Context: compact in place (issue #17; Ivan, 18 Nov 2026).** A long run does not hand over to a fresh session when its context fills: Claude Code compacts the session, re-attaches the skills it had loaded, and the run carries on. The plan lives in the work-list file, so the compaction summary is enough as long as the work-list is current. (A hand-over cost about USD 9 to 10, a compaction USD 1.0 to 3.3; figures in [references/routing-history.md](references/routing-history.md#compact-in-place-why-18-nov-2026).)

The `context-watch` hook (installed with the plugin, or by `scripts/install-context-hook.py`) reads this session's usage after every tool call; its levels and settings are in [references/context-handoff.md](references/context-handoff.md).

1. **Before the compaction: checkpoint.** When the hook says a compaction is near (70%, 85% and every 5 points after by default; 40% and 45% on the bench), bring the work-list file up to date — what is done; what is running, with task ids and output paths; the decisions taken and why; what comes next; which gates and reviews still apply — commit what has landed, and carry on. No continuation order, no `conductor-handoff`, no successor.
2. **After the compaction: re-read.** When the hook's SessionStart entry (source `compact`) — or, without it, the first tool call after a 20-point drop — says the session was compacted, re-read the work-list file and the run's order before any other action, check the lanes in flight by their task ids before starting new ones, and do not redo a step the work-list marks done. The run's gates, reviews and authorisations are unchanged.

**Context handoff: when a hand-over is still right.** Hand over to a fresh session only when the run sets `CONDUCTOR_CONTEXT_MODE=handoff`, or when the run must move to another machine or another model. Then follow [references/context-handoff.md](references/context-handoff.md) (checkpoint, continuation order, `conductor-handoff --order <path>`, stand down); the successor is a new conductor run on the same work-list.

**Scope honestly as it grows.** A long run discovers work. New items go on the work-list with a status, not silently into a lane. If the run will not finish within the budget or the window, say so while there is still time to choose what gets dropped, and `log()` what was dropped so a partial result never reads as a complete one.

## Native mobile verification

For Android/iOS application testing, read the bundled [mobile-app-testing skill](../mobile-app-testing/SKILL.md) and the project's mobile profile before writing the device order; it supplies the device, authentication, recording, recovery and cleanup procedures and the work-order fields. GPT-6.2 Sol at `high` (`-m gpt-6.2-sol --effort high`) owns the device session by default (or runs it directly when it is already the orchestrator), one agent per device and mutable fixture. Claude judges the UI (Gemini 4 Neon may add a `--file` second read, never in its place) and the orchestrator keeps final acceptance. Native execution is a verification lane: a built APK, unit tests or a mobile browser do not replace native results, and missing runtime access is reported as a gap, never a pass. Conductor remains the evidence and report-design authority.

## Orchestrator calibration (read before sizing lanes)

Opus 5.5 behaviours to counter in the orders you write:

- **Unattended lanes can end a turn after a progress update.** Put the unattended-lane paragraph (see **The loop**, step 2) at the end of every dispatched order. Treat a lane's text-only ending as a report, not proof the work is done: check its work-list, and name the open items when you send it back.
- **It thinks more per effort level than Opus 5 did.** Set effort explicitly, never above `high`, and lower effort rather than prompting for less thinking; drop "think carefully" lines — effort is the control.
- **It gets to work quickly.** On tasks spread across mail, documents, sheets or records, tell it to look through the relevant sources before it changes anything.
- **It paces itself to elapsed time.** For a fan-out, put a time budget in each order ("aim to finish within 20 minutes") and set it somewhat above what you want spent. The budget is advisory, so keep your own timeout.
- **Delete self-verification scaffolding.** "Double-check your output" or "spawn a verifier" in an order produces over-verification, not rigour; your cross-family gate (step 3) is the verification that matters.
- **Give it the whole task and the finish line.** One order carries the complete task and a "Done means: …" line naming the observable end state (every endpoint uses the new client, the old client is deleted, the suite passes). Never ask a lane to write its reasoning out in the reply; on Opus 5.5 that can trip the `reasoning_extraction` refusal.
- **Ask for the report you want to read.** Lanes mark anything they could not confirm and say where they looked. An audit or migration fan-out gives each item its own lane, and the orchestrator checks each lane's evidence before accepting it and finishes with one table (item, result, evidence). The orchestrator's own close to the user uses three headings: **Needs you**, **Changed**, **Found**.
- **Cap the fan-out you hand a lane.** If a lane could recurse, say so in the order: *"do this yourself; do not spawn subagents"*, or give an explicit ceiling. The **What earns an agent** gate applies to you as orchestrator too.
- **Scope discipline in the order.** State what NOT to touch, and that the lane should flag a concern in a sentence rather than re-scope the work.

Fable 5.2 orders:

- **Outcome orders.** A Fable 5.2 order states the outcome, the audience, the sources to read and the finish line, not a step list. Slice the work only where the slices are independent.
- **Habits observed on Fable 5.1; not yet checked on 5.2.** It may issue one tool call per turn ("request every independent item in one response"), it rewrites whole files for small edits ("targeted edits only"), and at `low` it answers from memory. Keep both order lines.

## The loop

**1. Plan (orchestrator).** Decompose into work orders. A work order that produces good results from a non-orchestrator model is *precise*: exact file paths and line anchors, the data contracts involved, the acceptance check ("the roster renders 4 rows at 390px with no horizontal scroll"), and what NOT to touch. Vague orders waste the cheap model's run and your review time. Scout the code yourself first — the 10 minutes grounding anchors is what makes the cheap lanes cheap.

- **Look for the same fault first.** Before building a fix for a reported fault, search open and recently merged issues and PRs by the error text and the symptom (`gh pr list --search "<error text>" --state all`, `gh issue list --search ...`), and repeat the search at each merge; the same fault often arrives through two channels.
- **Structural rules up front.** For money, stock, access, limits, shared-state or concurrency work, write the structural rules into the order before the first review (one read budget per query, one resolver per decision, one writer per key), and size each limit finding against production row counts: reviewers otherwise find one narrower case per round until the rule is stated as a decision.

**2. Dispatch (parallel).** Note the run's start time so the closing telemetry window is tight. If the run has a tracking issue, flip its label to in-flight (`gh issue edit <n> -R <owner>/<repo> --add-label status:running`). Optionally register the run so it shows as active on a dashboard — skip silently if you don't run one:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/conductor-report.py" --start \
    --run-id <YYYY-MM-DD-slug> --repo <repo> --issue "<repo>#<n>" --title "<short title>"
```

Every dispatched order ends with a time budget ("aim to finish within 20 minutes", set somewhat above what you want spent; keep your own timeout) and then this unattended-lane paragraph, verbatim. It is Anthropic's wording from the Opus 5.5 prompting guide. It goes in every dispatched lane's order, Claude or Codex, and never in the main loop, where the user may be there to answer:

> A standing instruction from the user, the person you are working for. It is about how your turns end. A message with no tool call in it ends your turn, and the work stops there until you are asked to continue. The user has seen you end turns in four ways while work they asked for was still owed, and does not want any of them. One: a long summary of what was done that closes by announcing the next step and has no tool call, so the next thing never starts. Two: an offer to carry on with something unless the user would prefer otherwise, which stops to wait for an answer the user was not going to give. Three: a list of decisions for the user when, by your own account, none of them blocks the rest of the work. Four: deciding that this is a good place to report, because the turn has been long or a milestone is done. Status notes are welcome, and so are your recommendations on open decisions, but put them in the same message as your next tool call and carry on with whatever does not depend on the user's answer. If you notice yourself inviting the user to redirect you or offering to wait, delete it and do the next thing. The stops the user does want are the ones where nothing can move without them, or where the thing blocking you is deliberately protected from you. This does not override the need for confirmation on risky or destructive actions.

Then launch independent lanes in the same turn:

- Claude lanes via the `Agent` tool (`model` and `effort`, or a bundled agent) or a `Workflow` script (`agent(prompt, {model: 'opus', effort: 'high'})`; `effort: 'medium'` for volume writing), in the mode chosen under **Turn-by-turn or Workflow**.
- Codex lanes via `Bash` with `run_in_background: true`:
  ```bash
  ask-codex -m gpt-6.2-sol --effort high --context work-order.md --output <scratchpad>/codex-N-report.md "Execute this work order. Your final message is the report: files changed, evidence, what you did not do."
  ```
  Launch each `ask-codex` or `ask-gemini` lane as its own Bash call with `run_in_background: true` (no `nohup`, no `&`), so its exit wakes the session. Detach only a lane that must outlive the session or the background-shell limit; then find its real PID (`ps -eo pid,args | grep <output path>`, never `$!` after `setsid`) and arm a background `until [ -s <output> ]` waiter.
  Write the work order to a file first (`--context` carries it), pass `-m` and `--effort` every time — the config default is not the lane's — and take the report from `--output` (stdout is session-log noise). Reviews, critical ones included, run `-m gpt-6.2-sol --effort high`, with `--effort xhigh` only for the retry after a thin `high` pass; bounded high-volume lanes run `-m gpt-6-luna --effort high`. Verification lanes need a permitted write-capable mode (check the wrapper and configuration) because they write the evidence the gate selects; do not pass `--readonly`: on the bench a read-only lane can succeed while reviewing only the prompt. For a volume-writing lane the order is the brief and `--output draft.md` is the deliverable.
- Inside a `Workflow` (whose `model:` accepts only Claude models), run a GPT or Gemini lane through a thin wrapper agent (`model: 'opus'`, `effort: 'low'`) that writes a self-contained prompt, runs `ask-codex -m <model> --effort <level>` or `ask-gemini -m gemini-4-neon-high --no-fallback` via Bash, and returns the report.
- **File collision rule:** no two write-lanes share a file. Give each parallel Codex write lane its own worktree with `ask-codex --worktree <branch>`: the lane commits on that branch, and you merge it and remove the worktree. Without `--worktree`, Codex lanes share the working tree, so serialize them or give the file to one lane and a follow-up order to the other.
- **Isolation:** writers get `isolation: "worktree"`; an Orca worktree is chosen only when the lane must be watched or steered live or must outlive the run, and then its terminal closes at lane-report.

**Background lanes: use completion notifications.** Background agents and background Bash are harness-tracked: you are **re-invoked automatically** when one finishes, so wait loops, sleeps and file checks buy nothing — dispatch, then do independent work or end the turn (Codex tool sessions follow the harness waiting contract above). Poll only state the harness cannot see: CI, a deploy or a remote queue (`Monitor` with an until-condition, sized to how fast it changes). A lane whose process exited and whose report file exists is read, not waited for. A hung lane is stopped and re-dispatched, not polled harder.

**3. Cross-verify (cheap, different eyes).** Each lane's work is checked by the *other* model family.

- **Verify orders.** A verify order against a deployed environment starts with step 0, "confirm the target deployment serves <sha>" (the tested commit or preview SHA, or the merge SHA after a merge: that deployment is ready and is the one the URL serves); local-checkout, static, docs and skill checks have no deployment and skip it. Every verify order tests the issue's acceptance text only; conditions you add produce "not met" verdicts that are not defects. Write expected results from the feature file and the component, not the issue's wording.
- **Walk new paths on a real record.** Before closing work that adds a path, walk it on the test track or a device on a real record, on the build that contains the merge, and again after a base merge restyles the same screen; read the screenshots yourself, including alerts, table cells holding new text and states the change hid. Unit tests and review rounds do not cover these.
- **A FAIL is an observation.** Before filing or accepting a walk or verify lane's FAIL, check it against the code and the issue's Acceptance text (Acceptance wins over Change) and read its screenshot; a wrong expectation in the order is not a defect.
- Claude built UI → `mobile-app-testing` (native) or `codex-computer-use` (other surfaces) runs the type checks and drives `agent-browser` (its own `--session`, never the shared one) or `node_repl` + `@oai/sky`, captures screenshots at the viewports that matter into `<scratchpad>/verify/` and writes a findings report.
- Claude executed a change → GPT-6.2 Sol at `high` via `codex-review` reviews the diff as the cross-family pass, critical changes included; no Opus `verify-lane` review runs beside it. When Sol cannot run, Gemini 4 Neon reviews in its place, then a fresh-context Opus 5.5 lane (see **Who reviews whom**).
- Codex executed a refactor → an Opus 5.5 lane at `high` (or you, if small) reviews it for taste and idiom drift. Codex wrote a draft → you edit it against the brief, and external copy gets a `write-lane` or Opus pass.
- You **Read the screenshots yourself.** GPT-6.2 Sol confirms mechanics; only you and the taste lane judge whether it *looks* right. Never accept "verified" on a visual change without seeing the pixels.

**4. Review + integrate (orchestrator).** Read every lane's report and the actual diffs (`git diff --stat` then the files that matter). Rejected work goes back as a *revised work order* — say what was wrong and what correct looks like, don't re-explain the whole task. You run the final checks applicable to the requested change and authorized by the task. Skill/report edits do not imply application builds, device rental or release publication; source changes use their project gates. Verify actual output rather than accepting a lane summary.

**Landing on a busy base.** Before a land waits on CI, check that `mergeable` is not `CONFLICTING` (a conflicted PR gets no CI, and its watch stalls without failing) and run `gh pr ready` on draft lane PRs; after each merge, re-read every other open PR's `mergeable`, and check it again right before merging. When the base moves every 20–30 minutes, land a wave through one integration PR (merge each reviewed lane head into one branch, carry every `Closes` and `map unchanged:` line in its body, cancel the lanes' queued CI) and put CHANGELOG and session-log entries in a small docs PR afterwards. Resolve code, test and feature-map conflicts by hand, never by union merge, and run one landing chain per PR at a time. When the base changes a rule your open PRs touch, test-merge each with the new base in a scratch worktree, check nothing the PR added or moved bypasses the new rule, and run both sides' tests.

**5. Publish the review HTML (orchestrator).** Create or update the run's HTML review file (see *Run review HTML* below) with what happened / what's proposed, decision diagrams, and the verification screenshots + recordings, then hand it to the user: on a desktop host `open` it; on a headless host (the bench — `~/reports` exists, no display) publish and verify with `~/bin/report-link.py <report-path>` and give the checked **hub URL** `https://bench.tailb5d047.ts.net/reports/<repo>/<file>` — never a disk path, never `xdg-open`.

## Codex and Gemini transport

The transport facts — CLI version and context window, `ask-codex` flags and sandbox modes, headless computer use, `ask-gemini` paths and exit codes, and running under a proxied orchestrator — are in [references/codex-cli.md](references/codex-cli.md). Beyond step 2 of the loop, two rules hold on every run:

- Each parallel Codex write lane gets `ask-codex --worktree <branch>`, never Codex's native `codex exec --worktree`; remove the worktree after you integrate the branch. A Codex lane that dies continues with the `ask-codex --resume <id> ...` command it printed at start; it does not restart.
- If `echo "$ANTHROPIC_BASE_URL"` shows a `127.0.0.1` URL, the main loop is proxied to a non-Claude model: read the reference's proxied-orchestrator section first, because cross-family routing inverts.

## Run review HTML (mandatory deliverable)

Every conductor run produces a refined HTML review file on top of the in-session summary, written for *review*, not as a log: executive, skimmable, easy to understand at a glance. Its explanation, diagrams, screenshots, video, Bench metadata and styling follow [references/report-design.md](references/report-design.md); reread it from disk before authoring.

- **Location + reuse:** `<repo>/.conductor/reports/` (create it; ensure `.conductor/` is gitignored), keyed `issue-<n>.html` when the run has an issue, else `<YYYY-MM-DD-slug>.html`. **Update in place:** if a report already exists for this session or issue, revise it (update proposals, append the new run as a dated section) instead of minting a new one.
- **Content:** what was asked; what happened *or what is proposed*; decisions made and why (options rejected included); per-lane outcomes; evidence; residual risk and next steps. A proposal run's HTML is the proposal document.
- **Video only when the evidence gate selects it** (see **Browser video evidence** below; Ivan, 13 Sep 2026): testing of changed application behaviour. Static reports, research and skill work use screenshots or command evidence; never present stills as if a recording existed.
- **Delivery:** on Ivan's configured Bench, run `~/bin/report-link.py <report-path>`, browser-check the exact served URL and deliver the HTTPS link labelled **private — Tailscale access required** (`domains/career-craft/bench/REPORTS.md`; `open` and local paths do not deliver a report on headless Linux). Elsewhere, verify delivery through the configured artifact surface.

## Review gates (non-negotiable)

- No lane's work is "done" until you've read its diff or its screenshots — reports are claims, not evidence.
- Anything user-facing (copy, layout, empty states) gets a taste-lane (Opus 5.5 at `high`, or Fable 5.2) or orchestrator eye before it ships, whichever lane built it. A change to an existing visual surface is judged on before and after screenshots at the same widths (a new surface or copy-only change: after only), not only the diff: on 19 Oct 2026 a finance home that shrank its headline figures passed two diff reviews and its tests. The design lane captures both when it can render the surface (`agents/design-lane.md`); otherwise the verify lane captures them from the base branch's running surface and the change. Benchmark products never override the project's own design rules. Prose that leaves the building may take an optional Fable 5.2 (`write-lane`) or Opus 5.5 second opinion / cold read.
- Verification lives in *your* gates, not in the work orders. A lane that was told to self-verify has told you nothing you can audit — read the diff or the pixels yourself.
- If a codex lane's diff smells like it fought the codebase (new helpers duplicating existing ones, style drift), stop dispatching that class of work to it and either tighten the work order or move the work to a taste lane. Note what happened for the session summary.
- Completion gates match the task: use relevant project checks and runtime evidence for application changes; source/installer checks and static report verification for skill edits. Push, merge and deployment still require task authorization.
- **Review rounds: decide by round 2 (Ivan, 11 Nov 2026).** A review loop on a pull request is decided at its second round. Round 1 lists what blocks, and the author fixes that. Round 2 goes to the same reviewers; its order names the round, lists the round-1 findings and covers only the fixes and what they changed. From round 2 on, a finding blocks the merge only when it is significant. Significant is at least: a round-1 blocking finding still not fixed; the change not doing what it is for; a wrong amount or figure; data lost or recorded wrongly; a security or access fault; personal data exposed; behaviour the base branch has and the change breaks; a step that is hard to reverse; a red check, or any other merge gate the change fails. The orchestrator may judge another finding significant and writes the reason on the pull request. Every remaining finding goes into the pull request's "Left as is" list and the change merges; a remaining finding becomes an issue only when it is significant (Ivan, 18 Nov 2026: a wrong amount or figure, data lost or recorded wrongly, a security or access fault, personal data exposed, behaviour the base branch has and the change breaks, or something a client sees or asked for). A review whose remaining findings are all listed this way counts as clean, for the merge and for the production rule. A third round runs only for a significant finding and covers only its fix. When the same part draws a significant finding in round 3 and again in round 4, stop patching it: take that part out of the pull request, or switch it off behind a default-off option under which none of it runs (a schema change, a migration, or a new public function or endpoint cannot be switched off and is taken out), and file it as its own issue with the open finding. One more round reviews only the removal or the option; when it is clean, the rest merges. The exception is a change with nothing left to merge without that part (the part is the whole change, or the rest only serves it): the rounds continue on that part alone. A change that also carries standalone work is not an exception. When round 2 returns the same kind of finding as round 1, order one structural rule in place of another patch. This sets when a loop ends, not how deep the review is: the review class and every other merge gate stay, and a significant finding is never deferred. Mail, decks and documents keep their own rules. (Why: on 10–11 Nov 2026 two PRs of one `sev:1` epic went six rounds and stayed open 5.6 and 8.6 hours against a 0.6-hour median.)

## Closing step: run-report

When available and authorized, close through the **`run-report`** skill: post the run report (what/tests/evidence/decisions/cost) as a comment on the run's issue/PR — include the review HTML's path in that comment — flip `status:*` labels, and append the telemetry ledger. A run without a report is invisible work.

Before closing, file what the run learned about the business (a decision, a meeting outcome, a client fact, a price or a date, including each Codex lane's "For the vault" section) with the `vault-note` skill, and name the vault commit in the run report. Repo how-to lessons go to Claude auto-memory instead.

If `run-report` is unavailable, use `${CLAUDE_PLUGIN_ROOT}/scripts/conductor-report.py` (resolve the installation path as described above) for configured telemetry and the same evidence/report contract. Do not send comments or change labels without authorization. If the run has no GitHub issue and no ledger configured, `run-report` degrades to the in-session summary plus the review HTML — that is a valid close, not a failure.

## Worked example (shape, not script)

> Task: "Add CSV export to the admin actions view, and make sure nothing regressed."

1. You scout: the view is `admin/actions/+page.svelte`, data comes from `getOrgActions`, export needs a new query arg or client-side serialization — decide client-side, cap honesty note required.
2. Dispatch: **`exec-lane` (Opus 5.5, `high`)** implements the CSV serialization and download button per a work order with exact anchors; no taste lane (the order names the button grammar to reuse).
3. On completion: **codex-review (`-m gpt-6.2-sol --effort high`)** reviews the diff as the cross-family pass, and a **codex verify lane (`-m gpt-6.2-sol --effort high`, write access)** typechecks, loads the page via agent-browser, exports a CSV, asserts the row count matches the screen and screenshots the button to `verify/`. Evidence: screenshots plus the row-count assertion; video only if a changed interaction needs it.
4. You: Read the screenshot (button grammar right?), read the diff, run the final gates, summarize.
5. You: write/update `.conductor/reports/issue-<n>.html` — decision diagram (client-side vs query-arg export, and why), the diff summary, the button screenshot, and, if the evidence gate selected it, the export-flow video (MP4; retain any WebM source) from the verify lane — then hand it over — `open` on a desktop, the hub URL on the bench: "here's the HTML review: https://bench.tailb5d047.ts.net/reports/mikono/issue-<n>.html"

<!-- browser-evidence:start -->
## Browser video evidence

## Choose evidence before recording

Ivan’s 13 September 2026 instruction: video is for meaningful application evidence, not a mandatory artifact for every Conductor run. Record video only when an application has been changed and the recording demonstrates testing of that change. Name the application change, test steps, expected result and independent assertion evidence in the work order. A report being opened in a browser is not an application change.

Do not record report opening, scrolling, resizing, publication checks, static document/design reviews, research, proposals, skill edits, or CLI-only work. For a static HTML report refresh, use desktop/phone screenshots and DOM/layout assertions; a browser being involved does not make video necessary. Use command output, tests or source evidence for nonvisual work. Static application changes may use screenshots when motion or interaction adds no evidence.

Each verification order states the evidence choice and reason. Only orders requiring video need a recording path. Keep required application-flow recordings and their assertions; do not reduce regression coverage. The recording procedure below applies only after this gate selects video. This scope supersedes blanket recording language in older Conductor examples and browser/verification instructions for Conductor work.

This contract supersedes older WebM conversion mandates elsewhere in this skill; WebM examples remain valid optional formats.

For a flow selected for video by the evidence gate, use agent-browser and specify a named session, initial state, steps, expected observable result, recording path and assertion evidence. Record representative application flows, not every unit test or edit iteration.

Read `agent-browser --version`, `agent-browser record --help`, and `agent-browser skills get agent-browser` for the installed command contract. Verified with 0.37.1: recording preserves the current page, DOM and login state, writes MP4 directly (H.264), and requires system ffmpeg. Older versions differ; do not assume they preserve context or support MP4. Use `agent-browser doctor` after upgrades. Upgrade through the installed package manager; avoid changing the default Node runtime for unrelated tools.

1. Use an owned `--session <lane>` on every command. Establish safe demo data/auth and the intended viewport before recording. Keep auth files outside report roots.
2. Start `agent-browser --session <lane> record start <assets>/<flow>.mp4` before the actions that matter. Omit the optional URL to preserve the current page. To capture navigation itself, start on an initialized page then issue `open <url>` separately. Wait for a visible rendered frame before very short flows; an empty capture is not evidence.
3. Drive real actions with fresh snapshot refs. Assert the result independently: visible state, persisted data, row count, download contents or a test assertion. Video alone is not a pass.
4. Stop with `agent-browser --session <lane> record stop`, including failure paths, and close only the owned session. Check exit status, nonempty output, ffprobe duration/codec, and actual playback. Preserve failed-flow evidence.
5. Embed `<video controls playsinline preload="metadata" src="assets/<run>/<flow>.mp4"></video>` in the run report with steps, environment/build, expected/actual result and assertions. Verify the served report and media. On Bench use `~/bin/report-link.py <report>` and deliver its verified private Tailscale URL. On Mac use the established report push and verify the Bench URL. Keep originals when creating derivatives; run Bench media conversion through `~/bin/bench-media-run -- ffmpeg ...` with bounded threads.

For bugs, capture before/after with matching steps, data and viewport when reproducible; say when the before state is unavailable. Never recreate a harmful production failure just for footage. Separate edited demonstrations from unedited verification evidence. For how-tos/journeys/features, include actor, prerequisites, step labels and successful end state; record only material approved for the intended audience.

Keep existing Playwright regression tests, assertions, traces, console/network evidence and flow-contract scorecards: they provide repeatability and diagnosis beyond video. Reuse an existing Playwright video capture if it covers the same flow; do not duplicate drivers solely for recording. Use native/device capture for native apps. When recording fails, report the actual failure and use captioned screenshots plus assertions as a declared fallback. Screenshots support visual review; the mechanics lane does not self-certify design quality.
<!-- browser-evidence:end -->
