---
name: conductor
description: Coordinate mixed-model work across Claude Code and Codex. Keep the current main agent responsible for grounding, work orders, integration and final acceptance; delegate bounded execution and independent review when worthwhile. Produce readable explanatory HTML reports with evidence chosen for the task. Use for /conductor, $conductor, "conduct this", "orchestrate at high", "mixed-model build", "use opus + codex", "use Claude and Codex", "have codex verify", "have codex write the blocks", "writing lane", "mixed-model ultracode", or a multi-stream build requiring independent implementation and review.
effort: high
---

# Conductor — mixed-model orchestration at `high`

## Profile scope

This entry point selects the default mixed-model profile. For Codex-first orchestration with optional Opus and no Fable dependency, use [Conductor Core](../conductor-core/SKILL.md). For a run with no Codex lane at all — every ChatGPT account in cooldown, Codex unreachable, or the work must stay in one vendor — use [Conductor Claude](../conductor-claude/SKILL.md), which carries every role on Opus 5 and Fable 5.1 and replaces the cross-family gate with context-independent, cross-model review under honest coverage labels. Each profile owns model selection, fan-out and review acceptance while it is active. When `profile: conductor-core` is active, that profile owns model selection, fan-out and review acceptance throughout the run, including supporting skills and bundled-agent defaults. The mixed-model mandates below do not override it. Core shares this file's installation, report design, explanation, delivery and evidence-selection contracts; its own policy replaces Claude-specific reviewer requirements within those sections. Ordinary `$conductor` behavior is unchanged.

**What this is for.** Conductor exists to accomplish work that is too large, too long-running or too multi-stranded for one agent in one pass — a migration across a repository, a feature with design and data and copy strands, an epic that spans sessions, a research or document build that runs for hours. The unit of ambition is the *run*, not the turn. Everything below — the work orders, the lanes, the review gates, the report — is machinery for holding a large piece of work together well enough that it finishes and can be trusted. **Verification is a part of that machinery, not its purpose.** The restraint sections exist so the capacity goes where it produces work, and are not a reason to attempt less.

**The premise.** Ultracode is not a model — it's `xhigh` reasoning plus a standing "workflow everything, cost be damned" instruction. You don't need either to fan out: the `Workflow` and `Agent` tools work at any effort. Conductor gets Ultracode-grade output for a fraction of the cost by keeping the main loop at `high`, invoking fan-out **on-demand**, and spending the expensive/high-judgment tokens only where judgment lives — decomposition, work orders, review, integration.

**The orchestrator never delegates three things: the plan, the work orders, the final review.** Everything else is dispatched. This holds whichever model runs the main loop.

## Model selection contract — 13 September 2026

This contract supersedes historical routing recommendations below. Select a role before launching, and record the model, effort, task-specific reason and acceptance criteria in the work order's `routing.json`.

| Work | Model | Effort |
|---|---|---|
| Bounded routine intake candidate packets | gpt-5.6-luna | medium |
| Well-specified implementation and runtime mechanics | gpt-6-astra | medium |
| Stateful execution, recovery, long execution of an established plan | gpt-6-astra | high |
| Ordinary investigation, design and review | claude-opus-5 | high |
| Ambiguous architecture, sustained reasoning and synthesis | claude-fable-5-1 | high |
| Adversarial review | claude-fable-5-1 | high |
| Cross-family review of Claude work | gpt-6-astra | high |

Long horizon means hours of work or continuity across sessions; duration and file count alone do not select a model. Route by the work's bottleneck. Higher review effort requires observed failure evidence and a separately recorded reason. Match the reviewer family against the author family; Astra reviewing Astra is not independent cross-family review.

Luna intake is advisory: use the constrained packet runner through the Codex ChatGPT login. It cannot dispatch workers, change labels, advance intake state or hold merge authority. Scripts handle empty rounds; ambiguity goes to the capable orchestrator. The runner and live collector/poller integration are tracked in IvanOboth/ivan-oboth#85; a skill edit alone does not change scheduled jobs.

The launcher selects the orchestrator model. Conductor guides that orchestrator's worker selection. Orca supplies worktrees and terminals; the command passed to the terminal determines the worker model. Pass model and effort explicitly, never rely on parent defaults. Use configured agent frontmatter or a CLI when the available Agent tool cannot set effort. Workers receive bounded orders and no recursive fan-out unless explicitly budgeted. Existing lanes retain their launch settings.

## One source and current instructions

This is the shared Conductor skill for Claude Code and Codex. The maintained source is `skills/conductor/SKILL.md` in the Conductor plugin repository. Personal entry points use a directory link or a minimal discovery file that reads that source; edit the resolved source, not separate harness variants. Use `scripts/link-personal-skills.py` from the checkout to establish local links. On every new report or substantial report revision, reread the current Report design contract and evidence gate from disk before authoring and before publication. A previously injected skill, older report or saved template may contain stale instructions; do not use it as the current design authority. This cannot update text already loaded into another running session: that session needs to reread the source.

## Installation paths

For a plugin installation, use `${CLAUDE_PLUGIN_ROOT}` for bundled scripts. For a checkout linked through personal skill entry points, resolve this SKILL.md symlink and use its plugin root (the directory containing `skills/`, `scripts/` and `agents/`); set `CLAUDE_PLUGIN_ROOT` to that resolved directory in shell calls using the examples below. The legacy copy installer rewrites these script paths to its installation directory. Do not infer the plugin root from the working repository.

Bench-specific report commands and metadata below apply only on Ivan’s configured Bench. On other hosts, use the configured report delivery surface, preserve its access boundary and verify the served file; do not require Ivan’s private vault, hostname or report helper.

## Harness-specific tools, shared contract

The current main agent remains the orchestrator, whether it is Claude or Codex. The plan, work orders, report requirements, evidence policy and acceptance gates below are shared. A skill does not change the model running the parent session. Use only the tools available in that harness, within its actual concurrency and permission limits; no table below grants capabilities or authorization.

- **Claude Code parent:** use its available Agent/Workflow tools for Claude lanes and `ask-codex` for Codex execution. Named bundled agents are optional and may be used only when installed. Claude-only APIs, options and background notifications in the examples apply to this path.
- **Codex parent:** use collaboration agents for bounded Codex execution when available, and `ask-claude --plan --model <model> --context <order>` for independent Claude review. Use `ask-claude --accept-edits` only for an authorized writable lane with exclusive file ownership. Specify the model according to the routing policy and the installed bridge contract. Codex does not acquire Claude Agent/Workflow tools by reading this skill. A Codex child is the same model family, not an independent cross-family reviewer.
- **Waiting:** use the actual harness completion mechanism. Claude background jobs may notify automatically; Codex must resume a running tool session with its wait/poll API when required. Do useful independent work while waiting, and keep Ivan informed. Do not assume a shell bridge delivers native agent notifications.
- **Safety and ownership:** preserve dirty user changes and serialize overlapping writes. Respect the user's authorized scope for commits, pushes, PRs, issue comments, messages and deployments; a closing checklist does not grant permission. Never deploy to production without explicit authorization.
- **Independent review:** check the implementing family with the other family. For a Codex-authored change, another Codex review is mechanics-only. For visual quality, use Claude to judge screenshots; inspect the actual artifacts and run objective acceptance checks in the main loop.

## Orca lanes or one session?

Decided 17 Sep 2026, measured on the live bench. Tokens are the same either way — each lane is a fresh context — so the real cost is lifecycle and integration, not spend. An Orca lane leaves a 330–530 MB Claude session plus its MCP children (Playwright, Chrome) running until someone closes it, and it ends at a draft PR nobody integrates once the orchestrator is gone. On 17 Sep the bench carried 235 live Orca terminals, 227 of them silent for 7+ days (28 Claude sessions, 13 Codex, 32 Playwright MCP, 19 Chrome), swap 11 of 15 GB used with 17 GB RAM free, and 152 worktrees against 84 on 14 Sep.

- **Default: one session.** Epics and the night shift run as a conductor run right here — `Agent`/`Workflow` lanes, `isolation: "worktree"` for writers (auto-cleaned when unchanged), cross-family review, merge behind the gates, one review page. The run ends its lanes when they finish and integrates in the same run.
- **Orca lanes only** when Ivan wants to watch or steer a lane live, or when the lane must outlive the orchestrator (a multi-hour build). Orca's value is visibility and steering, not parallelism.
- **Lifecycle rule for every Orca lane:** the terminal closes when its lane-report is written (`orca terminal close --terminal "$ORCA_TERMINAL_HANDLE" --json` as the lane's last command; the poller does this itself since #94, `POLLER_KEEP_TERMINAL=1` to keep one open); the worktree is removed after its PR merges (`orca worktree rm --worktree path:<path> --run-hooks --json`, never `--force` on a dirty tree); an evidence page is produced (`tools/evidence-page.py`).
- The idle reaper closes what slips through (terminals idle > 24 h) and the dashboard shows the terminal budget. Acceptance: a week after install the terminal count stays flat while the night shift runs, and every lane in the Orca sidebar is live or closed within an hour of its report.

## When to invoke (on-demand, not always)

Reach for conductor's fan-out when the work has **separable lanes** — design vs mechanical vs writing vs verification — or a **work-list to pipeline** over, or a **finding that needs independent verification** before it ships. For a single-file edit, a lookup, or tightly-coupled work where lanes would thrash the same files, skip it and work inline (or use plain all-Claude `Workflow` for tightly-coupled fan-out). Don't force a task to split that doesn't want to.

## What earns an agent (gate this before sizing anything)

Sizing answers *how many*. This answers *whether* — and it runs first. Getting this wrong is more expensive than getting the count wrong, because a wasted agent costs its full run and returns nothing.

**Scouting is your job, not a lane.** Step 1 says scout the code yourself, and it means with `Grep`, `Glob`, `Read`, and `Bash` — not by dispatching agents to go look. Delegated discovery is the single most common waste in a conductor run: the agents burn a full context each, come back with prose you then have to re-verify, and answer worse than the grep you could have run in two seconds. **If a grep, find, `ls`, `git log`, or file read would answer it, run the command.** An orchestrator that doesn't know the codebase yet is not ready to write work orders — and reading it yourself is what makes the work orders precise enough for cheap lanes to succeed.

**Every agent needs a deliverable contract.** Before dispatching, name the artifact that comes back: a file written, a diff applied, a report at a known path, a verdict with citations. An agent told to "investigate X and report findings" has no completion condition — it wanders, then goes idle without delivering. If you can't state what lands when it's done, you don't have a work order yet.

**An agent must be worth more than it costs.** An agent pays a fixed overhead every time: loading context, understanding the order, reporting back. That overhead only earns out when the item needs real reading, reasoning, or writing. **If an item is one tool call — a single mutation, one CLI invocation, a two-second edit — run it inline no matter how many items there are.** Four `npx convex run` calls are four seconds of your own turn; four agents to make those same calls is four agent-lifetimes to save nothing. This is orthogonal to coupling: items can be perfectly independent and still not worth an agent each.

**Work that's already parallel downstream doesn't need agent parallelism.** Async provider jobs (renders, builds, CI, queued API work) run concurrently on their own side. Submitting N of them is N calls; the concurrency lives in the provider. Agents assigned to "wait for" those jobs are idle agents — submit, then read the results when they land.

**Name the real reason when you go inline.** "It's a coupled chain" and "each item is one tool call" are different arguments, and only one of them is usually true. Reaching for *coupled* when the reason is *small* mislabels the case and generalizes badly — 20 independent file edits can be described as "an ordered chain" if you squint, and that's how genuinely parallel work gets serialized. State which it is.

**Fan out over a work-list you already have — never to produce one.** Discovery is one cheap step you run yourself (`grep -rl`, `git diff --name-only`); the fan-out is what happens *to the items it returns*. Spawning agents to find the items inverts that and pays the most for the least.

Three questions before any dispatch:

1. **Could a shell command answer this?** → Run the command.
2. **What artifact does this agent return?** → No answer means no dispatch.
3. **Is this discovery or execution?** → Discovery is yours. Execution and verification fan out.
4. **Is the item bigger than the agent's overhead?** → One tool call per item means inline, however many items there are.

A run whose agents mostly *looked things up* has the shape inverted. The scouting is cheap and yours; the expensive parallelism belongs downstream of it.

## Sizing the fan-out

**Lane count follows the work, not a habit.** The four lane *kinds* (design / mechanical / writing / verification) and the four bundled lane *agents* are a taxonomy and a menu — not a quota. One `design-lane` definition can be dispatched twelve times in one run. If the work-list has 20 independent items, that's 20 agents, not 3.

**The size guideline is a ceiling, not a target.** `large` means *up to* 50, never *aim for* 50. Five items get five agents; twenty get twenty; one coupled change gets one. Derive the count from the work-list you actually scouted, then check it against the ceiling — never the reverse. Both directions are failures, and they cost differently: under-fanning silently drops coverage, over-fanning burns tokens and buys nothing. Splitting five items into twenty agents by inventing sub-tasks, or stacking redundant verifiers on a finding nobody disputes, is the same error as batching twenty files into four agents.

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

**Spend the width where the agents are cheap.** A 30-file mechanical sweep is the *right* place for a wide fan-out — `gpt-6-astra` at `low` via codex, or `opus` at `effort: 'low'`, one agent per file. Cheap per-agent cost is exactly what makes breadth affordable; hedging to 4 agents there buys nothing and leaves 26 files unexamined. Reserve narrowness for expensive lanes (`xhigh`/`max` judgment), not cheap ones.

**Wide also survives interruption better.** On resume, cached results stop at the first agent that didn't finish and everything started after it re-runs — so many small agents preserve far more progress than a few long ones.

**The real limits** (none of which is 3):

| Limit | Value |
|---|---|
| Session size guideline | `small` <5 · `medium` <15 (default) · `large` <50 · `unrestricted`. **Advice, not a cap** — a task that calls for more overrides it. Set via `workflowSizeGuideline` in settings or `/config`. |
| Concurrent agents | up to 16 (fewer on limited cores). Excess **queues** — passing 100 items still completes all 100. |
| Total agents per run | 1,000 |
| Items per `parallel()`/`pipeline()` call | 4,096 (hard error above, never silent truncation) |
| Token budget | A "+500k"-style directive is a hard ceiling; `agent()` throws once spent |

Claude Code flags runs above 25 agents (or ~1.5M projected tokens) as `Large workflow` in the task panel. That warning is advisory — it doesn't pause anything. If the work-list justifies the count, proceed; if you bound coverage for cost (top-N, sampling, no-retry), **`log()` what you dropped** so a partial sweep never reads as a complete one.

The restraint elsewhere in this skill — "don't force a task to split", "don't dispatch what a few tool calls would finish" — is about *unnecessary* splits and orchestrator laziness. It is not a reason to under-serve genuinely parallel work. But it applies with full force to discovery: width is for executing and verifying a known work-list, never for assembling one.

## Long-horizon runs

A run that spans hours or sessions fails for different reasons than a run that fits in one turn. It does not usually fail on reasoning; it fails because state was held only in a context that ended. Three things make a large run survive.

**The work-list is an artifact, not a memory.** Write it to a file — the items, their owners, their status (queued / running / done / blocked), and the deliverable path for each. A run that keeps its plan only in the orchestrator's context loses the plan at compaction, at a usage limit, or when a session ends. When the work-list is on disk, any later session — or you after compaction — resumes by reading it.

**Phase the ambition, don't flatten it.** An epic is waves, not one enormous fan-out. Wave 1 establishes the contract (the schema, the shared component, the interface everything else depends on) and is usually one or two lanes. Wave 2 fans wide over the items that now have a stable contract to write against. Wave 3 integrates and verifies. Dependencies between waves are the reason phases exist; `Workflow`'s `phase()` names them, and `pipeline()` lets an item's later stage start as soon as its earlier stage lands rather than waiting for the slowest sibling.

**Checkpoint at boundaries.** At the end of each wave, persist what exists: commit the lanes that landed, update the work-list, and write what remains. Interrupted work that was committed is recoverable; interrupted work held in a lane's context is gone. This is why long write lanes commit incrementally rather than saving everything for a final message, and why many small lanes beat a few long ones — on resume, cached results stop at the first unfinished lane and everything after it re-runs.

**Resuming.** A `Workflow` resumes with `resumeFromRunId`: completed `agent()` calls with unchanged prompts return cached results instantly and only edited or new calls re-run. Stop the prior run before resuming it. For a run that outlived its session entirely, the work-list file plus the committed branches are the resume point — read them, re-scout what changed, and dispatch only what remains.

**Scope honestly as it grows.** A long run discovers work. New items go on the work-list with a status, not silently into a lane. If the run will not finish within the budget or the window, say so while there is still time to choose what gets dropped, and `log()` what was dropped so a partial result never reads as a complete one.

## Model routing

Rankings, higher = better. **Cost** is cost *per task*, not price per token — a model that finishes in a quarter of the tokens is cheaper at twice the price. **Reasoning** is neutral problem-solving: plans, reviews, judgment calls. **Autonomy** is how far a model gets unsupervised in a terminal, a browser or an ops loop — the axis that decides execution lanes. **Steerability** is whether it does what the work order said, no more and no less — it is what most often decides whether a dispatched lane comes back usable. **Taste** covers UI/UX, code quality, API design, and copy-in-a-UI. **Writing** is prose a human reads and judges the author by — emails, proposals, long documents, scripts, film prompt packages — a separate axis because a model can have taste in code and still write slop.

| model       | cost/task | reasoning | autonomy | steerability | taste | writing |
|-------------|-----------|-----------|----------|--------------|-------|---------|
| gpt-6-astra | 8         | 8.8       | 9.5      | 9.5          | 6     | 7       |
| opus-5      | 5         | 8.5       | 8.2      | 6            | 8.5   | 8       |
| fable-5.1   | 5         | 9.2       | 8.8      | 8.5          | 9     | 9       |

Adjust these to your own plan and pricing — they are directional, not universal. Reviewed against OpenAI's launch table, Artificial Analysis's independent runs, BenchLM, and Codex practitioner reports on 2026-09-05. **Astra's cost is a per-task number.** At API list it is $10/$50, level with Fable 5.1 (cache reads $1 vs Fable's $0.25; Fast mode 2× on the API, 2.5× in Codex; a long-context premium above 272K input) — but on Terminal-Bench 4.0's own leaderboard it resolves 58.2% for $3.3k on 1.5B tokens where Fable 5.1 does 57.9% for $6.2k on 2.7B and Opus 5 51.8% for $6.0k on 6.5B, and OpenAI's cost curves show the same inversion on OSWorld, Agents' Last Exam and BenchCAD. On a ChatGPT plan a codex lane costs quota in a 5-hour window rather than dollars, which only widens the gap. **Reasoning 8.8 vs autonomy 9.5 is the whole Astra story:** the neutral index did not move; the computer-use, terminal and automation boards did. The two agentic measures it does not lead are BenchLM's agentic aggregate (Opus 5 77.4 vs 70.3) and the Coding Agent Index (Fable 5.1 70 vs 67) — repo-shaped work, which is why those lanes stay on Claude.

**GPT-6 Astra replaced GPT-5.6 Sol on 2026-09-05** (released 2026-09-03; set `model = "gpt-6-astra"` in `~/.codex/config.toml`). One GPT row now — effort is the dial — and the separate cheap-codex sweep tier is gone (a ChatGPT-login Codex does not list `gpt-5.6-codex`); sweeps are Astra at `low`. What moved, and what did not:

- **Autonomy, computer use, terminal and ops lead the board on the GPT side.** OSWorld 2.0 72.6 vs Opus 5 70.2 (OpenAI's own figure: 47% less wall-clock per task than Sol); ScreenSpot-Pro 92.7; Terminal-Bench 4.0 57.7 vs Fable 5.1 55.8 vs Opus 5 52.3 on OpenAI's table (tbench.ai's own leaderboard run: 58.2 / 57.9 / 51.8); SRE-Bench 88.0 vs 12.5; AutomationBench 41.4 vs Fable 5.1 31.4 vs Opus 5 26.9; Agents' Last Exam 59.3 vs Opus 5 55.5 vs Fable 5.1 48.7; ARC-AGI-3 62.7 on the provider-neutral harness per BenchLM (99.9 is OpenAI's stateful harness — don't quote that one) vs Opus 5 30.2 vs Sol 7.8; FrontierMath Tier 4 97.6 vs 87.8.
- **Neutral reasoning is the one axis that did not jump.** Artificial Analysis Intelligence Index 61 — identical to Sol — vs Fable 5.1 at 66; Coding Agent Index 67, level with Opus 5, vs Fable 5.1 in Claude Code at 70; HLE-with-tools 57.2 vs Fable 5.1 65.0; FrontierCode 1.1 53.3 vs Opus 5 53.4; DeepSWE 74.1 vs Opus 5 73.7; SciCode down 2–3 points. **No SWE-bench Pro figure was published** — Opus 5's 79.2 stands until one lands.
- **Steerability went up.** Mid-task steering keeps the original job where Sol treated a steering message as a new goal; misaligned-outcome rate 3.4% vs Sol's 18.8%; honeypot cheating 0% vs 48.2%; hallucination 51% vs 92% (AA-Omniscience). Two things to counter in a work order: its reasoning is terser and harder to audit (UK AISI found it evades monitoring under adversarial prompting), so the report format — evidence, not claims — matters more; and its Codex window is **272K by default** (`~/.codex/models_cache.json`: `context_window: 272000`, `max_context_window: 872000` under a ChatGPT login — raise it per lane with `-c model_context_window=…`; 1.05M is API-only), so raise it for a long lane or split the order at ~200K.
- **Taste and writing are unmeasured or worse.** No published UI/design head-to-head, and GDPval-AA v2 (professional work products) *dropped* ~80 Elo against Sol. Writing stays at Sol's 7, taste at a provisional 6. Fable 5.1 keeps every taste and high-stakes-writing lane.

**Astra effort is the dial** (`ask-codex --effort LEVEL` → `codex exec -c model_reasoning_effort=LEVEL`): `low` for sweeps with exact anchors; `medium` the default for well-specified implementation — the one published practitioner run put it about 30% cheaper than Astra `high` with comparable output, in a third of Sol's requests; `high` when the work involves retries, ownership, persisted state or recovery paths, and for volume writing; `high` for cross-family review and adversarial verification; `ultra` (Codex only — not an API `reasoning.effort` value) — Astra delegating to its own parallel subagents — only for a self-contained long-horizon lane whose order caps the fan-out and names the worker budget (Codex subagents inherit the parent's model, so they are Astra-priced), never for a lane the orchestrator is already fanning out. Read `~/.codex/config.toml` for the default rather than assuming it, and pass the effort per lane.

**Fable 5.1 replaced Fable 5 on 2026-09-01** (`claude-fable-5-1`; `model: 'fable'` resolves to it). Same list price ($10/$50), cache reads at a quarter of Fable 5's rate ($0.25/Mtok — half of Opus 5's), and the gains concentrate where lanes run long: hours-long agentic coding, documents / spreadsheets / decks from a blank page, multistep research, dense-PDF vision, full-1M-context reasoning, and computer use that recovers from failed steps. Anthropic's own guidance is the routing rule: **start with Opus 5; use Fable 5.1 for demanding reasoning and long-horizon work, or when Opus 5 at higher effort still falls short.** Four 5.1 behaviours to counter in a work order: it may issue one tool call per turn where Fable 5 batched several (say "issue independent reads in one turn"); at `low` effort it answers from memory instead of searching (never dispatch it at `low` for research or verification); it rewrites whole files for small edits (say "targeted edits only"); and its prose runs denser with less formatting (writing orders ask for paragraph breaks explicitly).

**Opus 5 has not regressed on capability; its weak axis is steerability.** It leads where work is messy and repo-shaped — SWE-bench Pro 79.2% (no Astra figure published), BenchLM's agentic aggregate 77.4 vs Astra's 70.3 (Fable 5.1 tops it at 78.7) — and is level with Astra on OpenAI's DeepSWE table (73.7 vs 74.1) and on FrontierCode. What separates them in practice is **steerability**: Opus 5 is widely reported to expand scope beyond the ask, declare fixes complete while leaving pieces unimplemented, and delegate to subagents more readily than prior models — which is why the counter-instructions below exist. Route away from Opus when a task is steerability-sensitive, not when it is merely hard.

**Writing is its own routing problem.** Published head-to-heads (Jul–Sep 2026) put Fable ahead of the GPT family on prose — top writing Arena Elo, ~70% blind-test wins, more natural email drafts — and 5.1's prose is rated level with Fable 5's. Nothing published yet puts Astra ahead of Sol on prose, and GDPval-AA went the other way. GPT prose is competent, plain, and carries none of Claude's house tics: the "it's not X, it's Y" reflex, tricolons, the pre-emptive caveat, the em-dash cadence, the closing flourish. That makes Astra the *volume* writer even though Fable is the better *writer*; the split below follows from that.

Effort is a **separate dial from model tier**, and it moves reasoning more than a tier change does. Read Opus 5's reasoning as ~8.5 at `xhigh`/`max` and ~8 at `medium`; read Astra's `medium` as its implementation default and its `high`+ as the autonomy numbers above.

| effort   | send it |
|----------|---------|
| `low`    | mechanical work with exact anchors, where only repo idiom is at stake |
| `medium` | well-specified implementation against a clear contract (Astra's default) |
| `high`   | orchestration, design lanes, writing lanes, ordinary review, Astra lanes with state / retries / recovery paths |
| `xhigh` | Escalation supported by observed failure and a recorded reason; never an automatic review default |
| `max` | Further escalation with observed failure evidence and an explicit budget |
| `ultra`  | Astra only: the lane fans out to its own subagents — a self-contained long-horizon order that caps its own fan-out; never inside a fan-out you are already running |

**Cost per task depends on the lane's shape (2026-09-05).** Opus 5 and Fable 5.1 both sit at 5; the tie splits by token shape. *Read-heavy* lanes (reviews, verification, research over a cached corpus) favour Fable — cache reads at half Opus's price ($0.25 vs $0.50/Mtok) and about half the tokens per task. *Output-heavy* lanes (a design lane emitting long HTML, first drafts of long documents, bulk generation) favour Opus — half the output price, and caching never touches output. So Fable takes the review lane and Opus keeps the design lane at the same headline rating. Fable 5.1 leads Opus 5 on every row of Anthropic's 1 Sep table and on the independent boards (AA Intelligence 66 vs 63, Coding Agent Index 70 vs 67, BenchLM agentic 78.7 vs 77.4); neither has a published SWE-bench Pro figure for 5.1.

**How to apply:**

- These are defaults, not limits. If a cheaper lane's output doesn't meet the bar, re-run with more effort or a smarter model without asking. Judge the output, not the price tag — escalating costs less than shipping mediocre work.
- Cost is a tie-breaker only. When axes conflict for anything that ships: **the axis the lane is about (reasoning for plans and reviews, autonomy for execution) > steerability > taste > cost per task**.
- **Effort, not tier, is the first knob.** Before escalating opus → fable, re-run the same lane at higher effort (reviews are the standing exception — they start on Fable). Before dropping opus → codex for cost, drop effort first. Exception: never run `fable` at `low` for anything that must look something up.
- **Terminal, DevOps, infra, CI, migrations, SRE**: `gpt-6-astra` at `medium` via codex, first choice — Terminal-Bench 4.0 57.7 vs 55.8/52.3, SRE-Bench 88 vs 12.5. Its home turf, more so than Sol's was.
- **Patterned multi-file refactors** (rename everywhere, apply a contract across modules): `gpt-6-astra` at `medium`. Its patch format survives multi-file edits better than raw diffs, at about a third of Sol's tokens.
- **High-volume mechanical sweeps**: `gpt-6-astra` at `low`, one lane per item. On a subscription, watch the 5-hour window — a 20-lane fan-out can exhaust it; the overflow lane is `opus` at `low`.
- **Bulk / mechanical**: `gpt-6-astra` at `low`/`medium` is the default — steerability 9.5 and the cheapest cost per task on every computer-use, terminal and automation board. `opus` at `low`/`medium` (`bulk-lane`) only when the idiom is Claude-family (skills, agent definitions, CLAUDE.md conventions) or as the quota-overflow lane — don't reach for `fable` for bulk.
- **Messy repo-level bug hunts, unknown scope**: `opus` at `high`+ stays the default (SWE-bench Pro 79.2 with no Astra figure; agentic aggregate 77.4 vs 70.3). When Opus at `max` has missed, `gpt-6-astra` at `high` is a legitimate cross-family second attempt, not a downgrade.
- **Long-horizon lanes**: use Astra at `high` for execution of an established plan; Fable 5.1 at `high` for ambiguous architecture, sustained reasoning and synthesis. Hours of runtime, a large repository or a long document do not alone choose the model.
- **User-facing** (UI, copy-in-a-UI, API design) needs taste ≥ 7: `opus` (default) or `fable`. Astra has no published taste data — do not send it design.
- **Writing, high stakes** (a counterparty email, a proposal, an investor or board document, anything that carries the user's name and gets judged): `fable` at `high` — the bundled `write-lane` agent. Opus 5 at `xhigh` is the alternative when the document is long and structured rather than voice-critical — a long document is output-heavy, and Opus's output price is half Fable's.
- **Writing, volume or structured** (film prompt packages and generated-video blocks, storyboards and shot lists, internal docs, first drafts of long documents, routine mail): `gpt-6-astra` at `high` via `ask-codex --effort high --context brief.md --output draft.md`, with the orchestrator holding the brief and editing the draft. A **slop-and-cost bet, not a quality bet**: Astra is the other family, so it does not reproduce Claude's tics; its steerability keeps a 30-block structure intact where Opus drifts; hallucination halved since Sol. GDPval's regression is why it stays a bet. Anything that leaves the building still gets a Fable or Opus edit pass before it ships. Every writing order, either lane, states audience, register, length ceiling, the one thing the reader must do, banned phrases, and a sample of the voice.
- **The plan, the work orders and the final review stay with the orchestrator, and the orchestrator stays Claude.** Astra's steerability would make it a fine seat-holder on obedience alone, but the seat needs the 1M window (272K under a ChatGPT login), the Claude Code harness (`Agent`, `Workflow`, the skills), and the lead on neutral intelligence and the coding-agent index — which is where a plan and a final review live. Cross-family verification also only exists if the lanes are the other family from the seat. Opus's weakness is obedience, which the orchestrator seat is the least sensitive to because that is the seat a human is reading. Fable 5.1 is the best Claude in the orchestrator seat (steerability 8.5, and the seat that re-reads the cached prefix most gains most from its cache price); running it as the main loop changes nothing about the lane routing here. Give Astra more of the dispatched surface, never the baton.
- **Reviews**: Fable 5.1 at `high` for adversarial judgment; Astra at `high` for independent review of Claude-authored work. Higher effort requires observed failure evidence and a recorded reason.
- **Runtime verification (mechanics)**: `gpt-6-astra` at `medium`, by default, on any surface you can hand steps and an assertion — web, CLI, simulator, native GUI. Now its strongest suit, not merely the cheap seat, and still the different family — run it on every run; it costs a fraction of an Opus pass. Its ceiling is taste, not autonomy, which is exactly why the screenshots come back to you.
- **Runtime verification (judgment while driving)** — a flow with no pre-statable step list, where the next click depends on reading the screen: `gpt-6-astra` at `high` (OSWorld 72.6 vs 70.2, ScreenSpot-Pro 92.7, recovers from failed steps). Opus 5 driving `agent-browser` only when what is being judged mid-flow is taste.
- **Never use Haiku** for judgment work.
- **Never pay for Fast mode on a dispatched lane.** Same intelligence at 2× the price (2.5× for Astra in Codex), just faster tokens — it's for interactive work where a human is watching, never for a background agent.

## The lanes

| Lane | Model | Transport | Send it |
|------|-------|-----------|---------|
| Judgment | Orchestrator (main loop, `high`) | main loop | Plan, work orders, reviewing every lane's output, integration, the user-facing summary |
| Design | Opus 5 (default) / Fable 5.1 (escalation) | `Agent` with `model: "opus"` (or the bundled `design-lane` agent), or Workflow `agent(prompt, {model: 'opus', effort: 'xhigh'})` | Components, visual grammar, copy with taste — anything where "looks right" is the acceptance test |
| Execution | GPT-6 Astra (`medium`; `low` for sweeps; `high` with state / retries) | `Bash` → `ask-codex --effort medium` (writes to the working tree) | Well-specified mechanical work: refactors, migrations, test authoring, wiring a defined API, sweeps with clear anchors |
| Long reasoning | Fable 5.1 (`high`) | Explicitly configured Claude lane | Ambiguous architecture, sustained reasoning and synthesis |
| Long execution | GPT-6 Astra (`high`) | `ask-codex -m gpt-6-astra --effort high` | Execute an established plan across modules, tools or sessions |
| Writing (high stakes) | Fable 5.1 | Bundled `write-lane` agent (`fable`/`high`) | Counterparty email, proposal, investor or board document — anything that carries the user's name and gets judged |
| Writing (volume) | GPT-6 Astra (`high`) | `Bash` → `ask-codex --effort high --context brief.md --output draft.md` | Film prompt packages and generated-video blocks, storyboards, shot lists, internal docs, first drafts, routine mail — the orchestrator holds the brief and edits the draft; external copy gets a Claude pass before it ships |
| Judgment review | Fable 5.1 (`high`) — `verify-lane`; second opinions need a specific unresolved question | `Agent` with the bundled `verify-lane` agent | Adversarial review of a diff, a plan or a finding against its acceptance criteria — read-heavy, so Fable's economics win; verdict + ranked findings with file:line |
| Diff review (cross-family) | GPT-6 Astra (`high`) | `codex-review` skill (or `Bash` → `ask-codex -m gpt-6-astra --readonly --effort high`) | Co-equal cross-family review of a diff — run beside the Fable judgment lane on anything that ships |
| Runtime verification (mechanics) | GPT-6 Astra (`medium`; `high` for state/recovery) | `mobile-app-testing` for native Android/iOS; `codex-computer-use` for web/other GUI | Run the app, capture task-selected evidence and independently assert the result. The mobile skill covers physical and virtual devices, project profiles, sign-in, native recording and cleanup. |
| Runtime verification (judgment while driving) | GPT-6 Astra (`high`); Opus 5 only when taste is judged mid-flow | `mobile-app-testing` for native flows or `codex-computer-use` for other surfaces, with the decision rule in the order; `Agent` with `model: "opus"` driving `agent-browser` (own `--session`) for the taste case | Flows with no pre-statable step list, where the next click depends on reading what's on screen |

The signature move: each lane is checked by the **other model family**. The GPT-6 Astra verification lanes have dedicated skills — reach for `codex-review` for diffs, `mobile-app-testing` for native Android/iOS, and `codex-computer-use` for other running surfaces rather than hand-rolling the invocation.

**Codex's runtime reach widened (verified 2026-08-07)** and the routing follows it. The bundled `computer-use` plugin registers a `node_repl` MCP server that `codex exec` loads, so a headless shell-out now reads accessibility trees, clicks, types, and screenshots *arbitrary macOS apps* — native apps, menu-bar flows, Xcode/Simulator GUI steps, Chrome under the real logged-in profile. Surfaces that used to be unverifiable without a human are now codex-lane work; send any runtime check you can state as steps + an assertion there, whatever the surface — and with Astra, the flows that need judgment while driving too. What did **not** move is authority: Astra's taste is an unmeasured 6, so it confirms mechanics and you judge the pixels — and its cost per task is low enough that the verify lane runs on every run, not only the cheap ones. "Verified" from a codex lane means *it functioned*, never *it looks right*.

**Optional bundled agents.** When the Conductor plugin is installed, it supplies four pre-tuned lane agents with `model:` and `effort:` already set — `design-lane` (opus/xhigh), `bulk-lane` (opus/low), `verify-lane` (fable/high — the Claude judgment review; changed 2026-09-05), `write-lane` (fable/high). Use them via the `Agent` tool when you want the effort pinned regardless of session effort; the plain `Agent` tool has no `effort` parameter of its own, so a subagent dispatched without one of these inherits the session's effort.

## Native mobile verification

For Android/iOS application testing, read the bundled [mobile-app-testing skill](../mobile-app-testing/SKILL.md) and the target project's mobile profile before writing the device order. Default runtime execution to **gpt-6-astra**: `medium` for an established mechanical replay, `high` for screen interpretation, authentication, state and recovery. Pass model and effort explicitly. If the orchestrator is already Astra and owns the device, execute the run directly rather than creating a duplicate lane.

Astra owns the device session, scoped tests/fixes, native recordings, independent saved-state assertions and cleanup. Claude provides UI judgment under the current routing contract; the orchestrator reads the artifacts and retains final acceptance. Give one agent exclusive control of each device and mutable fixture. Mobile Next can drive physical or ADB-connected virtual devices; Genymotion supplies a cloud runtime. Inventory existing capability before asking for Mac SSH or adding a provider.

The work order names the artifact/build, backend/tenant, authentication reference, cases and assertions, platforms, ownership, evidence choice, authorized fixes/resources and cleanup. Native execution is a verification lane and is not covered by an implementation lane's instruction to avoid the UI. A built APK, unit tests or a mobile browser do not replace native results. Preserve failed runs and state final-build coverage precisely. Missing runtime access or visual-review quota remains an explicit gap; continue independent authorized work without claiming a pass. The mobile skill supplies device/recovery procedures; Conductor remains the evidence and report-design authority.

## Orchestrator calibration (read before sizing lanes)

- **Write work orders that assume self-verification.** Opus 5 verifies its own work unprompted. "Double-check your output", "add a final verification step", "spawn a verifier" in a work order produces over-verification and burned tokens, not more rigour — **delete that scaffolding**. Your own cross-family gate (§3) is the verification that matters, and it stays.
- **Cap the fan-out you hand a lane.** Opus 5 reaches for subagents readily. If a design lane could recurse, say so explicitly in the order: *"do this yourself; do not spawn subagents"* — or give an explicit ceiling. Same goes for you as orchestrator: don't dispatch what a few tool calls would finish inline.
- **Scope discipline in the order.** Opus 5 can widen a task it judges under-specified. State what NOT to touch *and* that it should flag a concern in a sentence rather than re-scoping the work.

## The loop

**1. Plan (orchestrator).** Decompose into work orders. A work order that produces good results from a non-orchestrator model is *precise*: exact file paths and line anchors, the data contracts involved, the acceptance check ("the roster renders 4 rows at 390px with no horizontal scroll"), and what NOT to touch. Vague orders waste the cheap model's run and your review time. Scout the code yourself first — the 10 minutes grounding anchors is what makes the cheap lanes cheap.

**2. Dispatch (parallel).** Note the run's start time so the closing telemetry window is tight. If the run has a tracking issue, flip its label to in-flight (`gh issue edit <n> -R <owner>/<repo> --add-label status:running`). Optionally register the run so it shows as active on a dashboard — skip silently if you don't run one:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/conductor-report.py" --start \
    --run-id <YYYY-MM-DD-slug> --repo <repo> --issue "<repo>#<n>" --title "<short title>"
```

Then launch independent lanes in the same turn:

- Design, long-horizon and high-stakes writing lanes via the `Agent` tool (`model: "opus"` / `"fable"`, or the bundled `design-lane` / `write-lane` agents) or a `Workflow` script (`agent(prompt, {model: 'opus', effort: 'xhigh'})`). Workflow when there's fan-out/pipelining — it's also where you can set per-lane effort inline; plain `Agent` for 1-2 lanes.
- Codex lanes via `Bash` with `run_in_background: true`:
  ```bash
  ask-codex --effort medium --context work-order.md --output <scratchpad>/codex-N-report.md "Execute this work order. Your final message is the report: files changed, evidence, what you did not do."
  ```
  Write the work order to a file first (`--context` carries it) and pass `--effort` every time — the config default is not the lane's. `--output` makes the CLI save the final message to a known path; stdout is session-log noise, the report file is the deliverable. Verification lanes need a permitted write-capable execution mode (verify the wrapper and active configuration; do not assume a sandbox default) at `--effort medium` — they write the screenshots or recordings selected by the evidence gate; `--readonly` is for lanes that only read (diff review, investigation). For a volume-writing lane the work order is the brief (audience, register, length ceiling, the reader's one action, banned phrases, a voice sample, and the block/section structure to keep) and `--output draft.md` is the deliverable.
- To run GPT-6 Astra *inside* a `Workflow` (the `model:` param only accepts Claude models), spawn a thin wrapper agent (`model: 'opus'`, `effort: 'low'`) whose prompt writes a self-contained codex prompt, runs `ask-codex` via Bash, and returns the result — the wrapper does no thinking of its own, so the cheapest Claude that can run a shell command is the right one.
- **File collision rule:** no two write-lanes share a file. Codex has no worktree isolation — if two write-lanes must touch the same file, serialize them or give the file to one lane and a follow-up order to the other.
- **Isolation:** writers get `isolation: "worktree"`; an Orca worktree is chosen only when the lane must be watched or steered live or must outlive the run, and then its terminal closes at lane-report.

**Claude-native background lanes: use completion notifications.** Background agents and background Bash are harness-tracked — when one finishes you are **re-invoked automatically** with its result. Writing a "bounded wait for lanes" loop, a sleep, or a repeated file-existence check buys you nothing and costs a shell command, tokens, and wall-clock per poll. Dispatch, then either work on something independent or end the turn; the notification is the wake signal.

For Codex tool sessions, follow the harness-specific waiting contract above. Other exceptions are state the harness cannot see:

- External systems with no notification path: a CI run, a deploy, a remote queue. Use `Monitor` with an until-condition, or a wakeup sized to how fast that state actually changes — not a 30-second tick.
- A codex lane whose *report file* is the deliverable and whose process has already exited. Read the file; don't wait for it.

If a lane hangs, that's a lane to stop and re-dispatch, not a lane to poll harder.

**3. Cross-verify (cheap, different eyes).** Each lane's work is checked by the *other* model family.

- Claude built UI → use `mobile-app-testing` for native Android/iOS and `codex-computer-use` for other surfaces: run the type checks, drive `agent-browser` (its own `--session` name — never the shared one) or, for a non-scriptable/native surface, `node_repl` + `@oai/sky`; capture screenshots at the viewports that matter into `<scratchpad>/verify/`, and write a findings report.
- Codex executed a refactor → an Opus 5 / Fable 5.1 lane (or you, if small) reviews the diff for taste and idiom drift; for a heavier independent pass on Codex-authored code, use a Claude-family reviewer; `codex-review` can provide an additional mechanics pass.
- You **Read the screenshots yourself.** GPT-6 Astra confirms mechanics ("page loads, no console errors"); only you and the taste lane judge whether it *looks* right. Never accept "verified" on a visual change without seeing the pixels.
- Codex wrote the draft → you edit it against the brief, and anything external gets a `write-lane` (or Opus `xhigh`) pass before it ships. Astra confirms the structure held; the voice is judged by the Claude side.

**4. Review + integrate (orchestrator).** Read every lane's report and the actual diffs (`git diff --stat` then the files that matter). Rejected work goes back as a *revised work order* — say what was wrong and what correct looks like, don't re-explain the whole task. You run the final checks applicable to the requested change and authorized by the task. Skill/report edits do not imply application builds, device rental or release publication; source changes use their project gates. Verify actual output rather than accepting a lane summary.

**5. Publish the review HTML (orchestrator).** Create or update the run's HTML review file (see *Run review HTML* below) with what happened / what's proposed, decision diagrams, and the verification screenshots + recordings, then hand it to the user: on a desktop host `open` it; on a headless host (the bench — `~/reports` exists, no display) run `~/bin/sync-reports.sh` and give the **hub URL** `https://bench.tailb5d047.ts.net/reports/<repo>/<file>` — never a disk path, never `xdg-open`.

## Codex CLI facts

- Config lives at `~/.codex/config.toml` — `model` and `model_reasoning_effort` are the two keys that matter. **Read it rather than assuming its contents**; effort there is independent of the Claude session's effort. Override per-invocation with `ask-codex -m gpt-6-astra --effort high` (maps to `codex exec -c model_reasoning_effort=high`) or `ask-codex -m MODEL`.
- Two transports, same engine: `ask-codex` (on PATH (resolve with `command -v ask-codex`)) shells out to `codex exec`. The direct equivalents are `codex exec -s <sandbox> "<prompt>"` (execution/verification) and `codex exec review` / `codex review` (diff review — `--uncommitted`, `--base <branch>`, `--commit <sha>` scope it).
- `ask-codex` flags: `--effort LEVEL` (per-lane reasoning effort — pass it every time; the config default is not the lane's), `--context FILE` (attach work order; a missing file is an error), `--readonly` (read-only sandbox — for lanes that only read: diff review, investigation; not for verification lanes, which write screenshots), `--clean` (strip session logs), `--output FILE` (codex writes its answer to a file — prefer this over parsing stdout), `-m MODEL` (override). Sandbox modes on `codex exec`: `read-only`, `workspace-write`, `danger-full-access` (only when permitted and the task must act outside the working tree). Inspect the active wrapper/configuration rather than assuming a default; native device orders follow the mobile skill’s permissions preflight.
- Wrapper quirk: with `--clean`, the answer can print *after* the `--- End Codex Response ---` marker — read the tail of output, or better, use `--output`/report-files and skip stdout parsing entirely.
- Codex CAN run shell commands (tests, `agent-browser` incl. `record start/stop`, `open`, `screencapture`, simulators) inside its sandbox in write mode — the cheap path for **computer-use verification headlessly** (see the `codex-computer-use` skill). It also carries the Playwright MCP headlessly. **On the bench** the same lane runs via `ssh bench codex exec …` with agent-browser + Playwright MCP (Chrome sandboxed under the `agent-chrome` AppArmor profile); `sky`/native GUI and the iOS Simulator stay Mac-only; **For native Android/iOS, use `mobile-app-testing`.** Discover available acceleration and devices; Mobile Next can drive physical phones or ADB-visible virtual devices such as Genymotion. Do not retry software emulation indefinitely on a host without usable acceleration.
- **GUI computer use is reachable headlessly too.** `codex exec` loads the `node_repl` MCP server from the bundled `computer-use` plugin, giving it `@oai/sky` — accessibility tree, clicks, typing, per-app screenshots on any macOS app. `codex exec -s danger-full-access` is the working invocation (full access because the artifacts dir is usually outside the repo, and the CU service hands back `file://` screenshot paths the lane must copy). The Codex **desktop app** (`@Computer` / `@AppName`) is now only the *interactive* front door to the same engine — reserve it for flows a human should watch. Caution: `sky` drives the user's real desktop, so prefer `agent-browser`/Playwright for ordinary web QA and name the off-limits windows in the work order.
- Long runs: launch with `run_in_background: true` and a generous timeout; you get notified on completion. Multiple codex lanes run fine in parallel.
- Parallel *write* lanes need isolation: codex has no worktree isolation of its own, so two codex write-lanes touching the same file collide. Serialize them, or run each via an `Agent`/`Workflow` wrapper with `isolation: 'worktree'`.

## Run review HTML (mandatory deliverable)

Every conductor run produces a refined HTML review file on top of the in-session summary. On other hosts, verify delivery through their configured artifact surface; the following commands apply only on Ivan’s configured Bench. On Bench, run `~/bin/report-link.py <report-path>`, browser-check the exact served URL, and deliver the HTTPS link labelled **private — Tailscale access required**. Follow `domains/career-craft/bench/REPORTS.md`; `open` and local paths do not deliver a report on headless Linux. Written for *review*, not as a log: executive, skimmable, easy to understand at a glance.

- **Location + reuse:** `<repo>/.conductor/reports/` (create it; ensure `.conductor/` is gitignored). Key the file by issue when the run has one — `issue-<n>.html` — else by run-id (`<YYYY-MM-DD-slug>.html`). **Update-in-place rule:** if a report already exists for this session or this issue, update that file (revise proposals, append the new run as a dated section) instead of minting a new one.
- **Content:** what was asked; what happened *or what's being proposed*; decisions made and why (including options rejected); per-lane outcomes; evidence; residual risk and next steps. If the run is a proposal rather than a build, the HTML is the proposal document.
- **Diagrams:** use them wherever they beat prose — decision trees for choices made, before/after architecture, lane/data flow. Inline SVG or styled HTML/CSS preferred; mermaid via CDN script is acceptable (the file is local, no CSP).
- **Screenshots:** embed every verification screenshot that mattered. Base64 data URIs keep the file self-contained; drop large originals in `.conductor/reports/assets/<run-id>/` and reference them. Caption each with viewport + what it proves.
- **Video when warranted (Ivan, 13 Sep 2026):** apply the evidence gate below. Record only testing of changed application behavior; static reports, research and skill work use screenshots or command evidence. For selected flows, use the tool for the surface and the run assets directory:
- Web recording: first apply the evidence gate; when video is warranted, follow the Browser video evidence contract; prefer direct MP4 on verified 0.37.1. Reuse existing Playwright capture where it covers the flow.
  - **Native Android/iOS:** follow `mobile-app-testing` for device selection, durable recorder ownership, fresh UI observations, final-artifact provenance and cleanup. Mobile Next recording APIs or a durable owned ADB recorder are valid; the recorder need not belong to the orchestrator if the device lane owns its lifetime. Use the evidence gate before capture.
  - **iOS Simulator (Mac only):** `xcrun simctl io <device-udid> recordVideo --codec h264 <assets>/<flow>.mp4` in the background, drive, then SIGINT it.
  - **Native macOS app:** `screencapture -v <assets>/<flow>.mp4` (Ctrl-C to stop) — Mac only.
  - Embed with `<video controls preload="metadata" src="assets/<run-id>/<flow>.mp4">` and retain the original when converting from WebM; direct MP4 needs no duplicate. On the bench also drop the files under `~/reports/<repo>/<run>/` so they're viewable from the phone at https://bench.tailb5d047.ts.net/reports/. When recording is genuinely infeasible, a captioned screenshot sequence is the fallback — say so in the report; never present stills as if a recording existed.
- **Discovery metadata (configured Bench only):** the `<head>` carries the `bench:*` block (`bench:type`, `bench:owner`, `bench:action`, `bench:action-url`, `bench:due`, `bench:evidence-date`, `bench:work`) so the hub can catalogue the run — see "Declare what the report needs" in `domains/career-craft/bench/REPORTS.md` for the rules. Set `bench:owner` honestly: `ivan` only when a human decision is genuinely waiting, `agent` for routine agent-owned work. Set `bench:evidence-date` to the date of the newest evidence embedded in the report, not the date you wrote it.
- Styling: follow the Report design contract below; light, readable, editorial, and responsive.

## Report design contract

Use a light editorial document: warm off-white ground, dark ink, restrained sage accent. Lead with the outcome or decision and the next action, then develop the reasoning. Do not invent a decision when none is needed. Use a clear title, short standfirst and descriptive section headings; compact anchor navigation helps long reports.

### Help Ivan understand

A report has two jobs: say what was done and help Ivan understand what is going on. Explain the problem or trigger, how the relevant parts interact, what changed, and why that produces the outcome. For proposals, distinguish the intended effect from observed results. Use plain language, short explanations and concrete examples; introduce technical terms only when needed and explain them on first use. Keep implementation detail available as supporting evidence.

Always consider a visual while outlining the report. Prefer a diagram or flowchart for a multi-step process, decision, dependency, ownership boundary or cause-and-effect relationship; use before/after views to explain a meaningful change. Put it beside the explanation it supports, with a short caption stating the takeaway. A trivial update may be clearer in a sentence; do not add a decorative diagram to meet a quota.

Keep each visual focused on one question, with a clear reading direction, short plain-language labels and labelled arrows where their meaning is not obvious. Show only the parts needed to understand the point; split complex systems into smaller views. Ensure labels remain readable on a phone, and include a brief text explanation so the diagram is not the only way to understand it. Prefer inline SVG or HTML/CSS that works offline.

Before delivery, check: can Ivan explain what happened, why it happened and what it means without reading the raw logs or knowing the codebase? If not, simplify the explanation or add the missing visual.

Keep prose around 65–75 characters wide, body text at least 16px with 1.55–1.75 line height, generous section spacing and a distinct heading hierarchy. System fonts work offline; a restrained serif heading can add character. Use whitespace and thin rules for structure. Avoid repeated rounded cards, giant boxed flow steps, dashboard badges, decorative metrics and dense full-width prose. Reserve panels for content that benefits from grouping.

Use tables only for genuine comparisons. At phone widths, provide labelled stacked rows or a deliberate scrollable table with readable column widths; never squeeze labels and paths into one-word or one-character columns. Prefer compact numbered sequences for simple process explanations. Diagrams must communicate a relationship more clearly than prose.

Keep the conclusion, decisions, material failures and risks visible. Put raw logs, long reviewer transcripts and secondary file anchors in labelled native details/summary disclosures. Evidence should support a specific claim; do not fill the report with redundant screenshots or recordings of the report itself. Preserve provenance and uncertainty when restyling an existing report.

Use semantic headings, visible keyboard focus, adequate contrast and meaningful link labels. Keep HTML/CSS self-contained and offline-capable; avoid required remote fonts or rendering libraries. Check the served page at desktop and 390px phone widths, including open disclosures, long paths, navigation and overflow. Use screenshots for visual review; DOM checks alone do not establish readability. Route design/taste to the Claude lane and verify mechanics independently.

## Review gates (non-negotiable)

- No lane's work is "done" until you've read its diff or its screenshots — reports are claims, not evidence.
- Anything user-facing (copy, layout, empty states) gets a taste-lane (Opus 5 at `xhigh`, or Fable 5.1) or orchestrator eye before it ships, regardless of which lane built it. Prose that leaves the building gets a `write-lane` or Opus edit pass regardless of which lane drafted it.
- Verification lives in *your* gates, not in the work orders. A lane that was told to self-verify has told you nothing you can audit — read the diff or the pixels yourself.
- If a codex lane's diff smells like it fought the codebase (new helpers duplicating existing ones, style drift), stop dispatching that class of work to it and either tighten the work order or move the work to a taste lane. Note what happened for the session summary.
- Completion gates match the task: use relevant project checks and runtime evidence for application changes; source/installer checks and static report verification for skill edits. Push, merge and deployment still require task authorization.

## Closing step: run-report

When available and authorized, close through the **`run-report`** skill: post the run report (what/tests/evidence/decisions/cost) as a comment on the run's issue/PR — include the review HTML's path in that comment — flip `status:*` labels, and append the telemetry ledger. A run without a report is invisible work.

If `run-report` is unavailable, use `${CLAUDE_PLUGIN_ROOT}/scripts/conductor-report.py` (resolve the installation path as described above) for configured telemetry and the same evidence/report contract. Do not send comments or change labels without authorization. If the run has no GitHub issue and no ledger configured, `run-report` degrades to the in-session summary plus the review HTML — that is a valid close, not a failure.

## Worked example (shape, not script)

> Task: "Add CSV export to the admin actions view, and make sure nothing regressed."

1. You scout: the view is `admin/actions/+page.svelte`, data comes from `getOrgActions`, export needs a new query arg or client-side serialization — decide client-side, cap honesty note required.
2. Dispatch in one turn: **codex (write)** — implement the CSV serialization + download button per work order with exact anchor lines; **taste lane** — n/a this time (no design surface beyond a button — the work order specifies the exact button grammar to reuse).
3. On completion: **codex (workspace-write, `--effort medium`)** — verify: typecheck, load the page via agent-browser, export a CSV, assert row count matches the on-screen count, screenshot the button placement to `verify/`. Evidence choice: screenshots plus download row-count assertion, because the downloaded data establishes correctness; add video only if a changed interaction needs demonstration.
4. You: Read the screenshot (button grammar right?), read the diff, run the final gates, summarize.
5. You: write/update `.conductor/reports/issue-<n>.html` — decision diagram (client-side vs query-arg export, and why), the diff summary, the button screenshot, and, if the evidence gate selected it, the export-flow video (MP4; retain any WebM source) from the verify lane — then hand it over — `open` on a desktop, the hub URL on the bench: "here's the HTML review: https://bench.tailb5d047.ts.net/reports/mikono/issue-<n>.html"

## Appendix — running under a proxied orchestrator (optional)

Skip this section unless you route Claude Code's main loop through a local proxy to a non-Claude model (e.g. CLIProxyAPI serving GPT-6 Astra). **Detect it:** run `echo "$ANTHROPIC_BASE_URL"` — a `127.0.0.1` URL means proxied mode. This inverts the usual arrangement: the proxied model holds the judgment lanes and does most execution itself; Claude becomes the dispatched taste / second-family lane.

- **The `Agent`/`Workflow` `model:` param cannot reach Claude models** through such a proxy — it has only the proxy's auth, so `model: "opus"` silently remaps and `model: "fable"` errors. Never dispatch a taste lane via `Agent`/`Workflow` in this mode; it would be the same model reviewing itself.
- **Taste/design/judgment lanes go via an env-stripped shell-out to real Claude**, which uses your own Claude login directly (never add Claude auth to the proxy):
  ```bash
  env -u ANTHROPIC_BASE_URL -u ANTHROPIC_AUTH_TOKEN -u ANTHROPIC_MODEL \
      -u ANTHROPIC_DEFAULT_OPUS_MODEL -u ANTHROPIC_DEFAULT_SONNET_MODEL \
      -u ANTHROPIC_DEFAULT_HAIKU_MODEL -u ANTHROPIC_SMALL_FAST_MODEL \
      -u CLAUDE_CODE_SUBAGENT_MODEL \
    claude --model opus --dangerously-skip-permissions \
      -p "$(cat work-order.md)

Write your report to <scratchpad>/claude-N-report.md when done." \
      --output-format text < /dev/null
  ```
  `--model opus` for taste/design lanes; `--model claude-fable-5-1` when the lane needs top-shelf judgment or is a high-stakes writing lane. Write the work order to a file first; launch long lanes with `run_in_background: true` and a generous timeout — the report file is the deliverable. Same file-collision rule as codex lanes: these shell-outs write to the shared working tree with no isolation.
- **Codex lanes are unchanged** but become *same-family* with the orchestrator. Cross-family verification therefore routes the other way: send diff-taste review and anything user-facing to a Claude shell-out lane, and treat `codex-review` as a mechanics-only second pass, not the independent perspective.
- Everything else holds: the orchestrator still never delegates the plan, work orders, or final review; still Reads screenshots itself; still runs the end gates and closes with `run-report`.

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
5. Embed `<video controls playsinline preload="metadata" src="assets/<run>/<flow>.mp4"></video>` in the run report with steps, environment/build, expected/actual result and assertions. Verify the served report and media. On Bench use `~/bin/report-link.py <report>` and deliver its verified private Tailscale URL. On Mac use the established report push and verify the Bench URL. Keep originals when creating derivatives; run Bench media conversion through `~/bin/bench-heavy-run -- ffmpeg ...` with bounded threads.

For bugs, capture before/after with matching steps, data and viewport when reproducible; say when the before state is unavailable. Never recreate a harmful production failure just for footage. Separate edited demonstrations from unedited verification evidence. For how-tos/journeys/features, include actor, prerequisites, step labels and successful end state; record only material approved for the intended audience.

Keep existing Playwright regression tests, assertions, traces, console/network evidence and flow-contract scorecards: they provide repeatability and diagnosis beyond video. Reuse an existing Playwright video capture if it covers the same flow; do not duplicate drivers solely for recording. Use native/device capture for native apps. When recording fails, report the actual failure and use captioned screenshots plus assertions as a declared fallback. Screenshots support visual review; the mechanics lane does not self-certify design quality.
<!-- browser-evidence:end -->
