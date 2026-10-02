---
name: conductor-claude
description: Orchestrate a full Conductor run inside the Claude family only — Opus 5.5 and Fable 5.1 lanes, effort as the dial, context-independent adversarial review in place of the cross-family gate. Use when the Codex/ChatGPT quota is spent, Codex is unreachable, or the work must not leave the Claude family. Use for Conductor Claude, /conductor-claude, "no codex", "codex is out of credit", "Claude-only orchestration", "single-family run".
effort: high
---

# Conductor Claude

Run the full Conductor workflow with no Codex lane. Opus 5.5 and Fable 5.1 carry every role. Opus 5.5 is the default for almost every lane, including design and the routine review of Opus-authored work. Fable 5.1 at `high` reviews and designs **critical** work, writes the high-stakes prose, takes ambiguous architecture and takes over when Opus 5.5 at `high` falls short. Effort is the first setting to change, and `high` is the ceiling for Opus 5.5.

Changed 22 Sep 2026: Opus 5.5 replaced Opus 5 in every row, and no Opus lane runs above `high`.

Changed 27 Sep 2026: Fable 5.1 review and Fable 5.1 design are for critical work only. Routine Opus-authored work is reviewed by a separate Opus 5.5 `high` lane in fresh context, labelled `same-model, fresh context`.

**Critical** means any of: it deploys to production or changes production data; auth, payments, money or personal data; a schema or data migration; anything hard to reverse; a client-facing deliverable (proposal, deck, flagship UI surface); or the routing and agent configuration itself. Everything else is routine. Decide it per order when you write the order, and write it into the order.

**The purpose is unchanged from the mixed profile: finish ambitious work.** A migration across a repository, a feature with design and data and copy strands, an epic that spans sessions, a long document or research build. Losing the Codex lane changes who does the work and how it is checked; it does not change how much work a run should attempt. Do not read this profile as a reason to scale the ambition down — read it as the routing and review policy that lets the same ambition proceed on one family.

This is a routing profile in the Conductor plugin, not a degraded mode. It does lose one real thing — a reviewer from a different training run — and the sections below replace that honestly rather than pretending it is still there.

## Profile and shared authority

Set `profile: conductor-claude` in the run and in every work order. This file owns model routing, fan-out, quota budgeting and review acceptance for the run.

Read the current [shared Conductor source](../conductor/SKILL.md) for **What earns an agent**, **Turn-by-turn or Workflow**, **Sizing the fan-out**, **Orchestrator calibration**, **Installation paths**, **Report design contract** (including **Help Ivan understand**), **Run review HTML**, **Choose evidence before recording**, the **Browser video evidence** contract and **Closing step: run-report**. The dispatch-gate and sizing rules there are unchanged by this profile: scouting is still yours, every lane still needs a deliverable contract, one agent per independent item, and the size guideline is a ceiling rather than a target. Those remain the single source for report structure, explanation, delivery and evidence selection. Where they call for a Codex lane, a cross-family reviewer or `ask-codex`, apply the substitutions in this file instead. Resolve relative references from the canonical source directory. Reread the shared report and evidence sections before authoring or revising a report.

The mixed-model routing tables, the GPT-6.1 Sol lanes and the mandatory other-family gate in the sibling [Conductor](../conductor/SKILL.md) skill do not apply here. The [Conductor Core](../conductor-core/SKILL.md) profile is the mirror image of this one — GPT-6.1 Sol-first with optional Opus — and its policy does not apply here either. A continued run keeps its profile across compaction, checkpoints and handoffs unless Ivan changes it.

**The orchestrator still never delegates three things: the plan, the work orders, the final review.** That holds in every profile.

## Choose this profile deliberately, not after a lane fails

Enter Conductor Claude when one of these is true, and say which in the run header:

- Every Codex account is in cooldown or the ChatGPT quota window is spent.
- Codex is unreachable on this host, or the sandbox/transport is broken.
- The work must stay inside one vendor (data boundary, contractual constraint, or Ivan said so).

Check before you assume. Two Codex failure modes look identical to "out of credit" and are not:

```bash
codex-account list --json     # cooldown_until / cooldown_reason per account; available:true means untested, not proven
codex-account pick            # exit 3 = every account is cooling down
```

A silent `ask-codex` past ~10 minutes with no rollout file is a wrapper or sandbox failure, not a quota failure — read the rollout jsonl before concluding anything. `--readonly` succeeding while a write lane dies is the sandbox, not the account. Quota is per **account**, not per home, and cooldowns are keyed on the account, so one login being dry says nothing about the other two.

If exactly one account still has credit, the right move is usually **not** this profile: run the ordinary mixed-model `conductor` and spend that one account on the single lane where family independence matters most — the review gate on whatever ships (GPT-6.1 Sol `high`, or `xhigh` when it is critical). Reach for Conductor Claude when there is nothing left to spend, or when spending it would cost more than the independence buys.

## What you lose, and what replaces it

You lose exactly one thing: a reviewer drawn from a different training run, with different priors and different blind spots. Everything Codex did *mechanically* — terminal work, sweeps, browser driving, screenshots, refactors — Claude also does; it costs more per task and needs a tighter order, but the capability is there.

The loss matters because author and reviewer now share a monoculture. Concretely, these get past a same-family review far more often than a cross-family one:

- An idiom both models reach for that this repo does not use.
- A library API both models remember the same wrong way.
- A framing error inherited straight from the work order, which the reviewer reads as the requirements.
- "Done but not done" — a fix declared complete with a piece unimplemented, where a reviewer with the same optimism reads the summary and agrees.

### The independence substitutes, ranked

Use them in this order. The first is the largest lever and it is free.

1. **Fresh context, artifact only.** Give the reviewer the requirements and the diff or artifact — never the author's rationale, never the author's verdict, never the author's report. Most of what "independent review" buys is *not having already believed the author's reasoning*. This survives intact in a single-family run and it is the substitute that does the most work.
2. **Different model in-family, on critical work.** Fable 5.1 at `high` reviews critical Opus 5.5 work; Opus 5.5 at `high` reviews all Fable 5.1 work. Different post-training, measurably different failure modes. Not another family, but not nothing. Routine Opus 5.5 work does not get this substitute: its reviewer is a second Opus 5.5 lane at `high` in fresh context, which is substitute 1 alone and is labelled as same-model.
3. **Distinct lenses, not more reviewers.** Three reviewers told "review this diff" return the same review three times. Three reviewers each given one failure mode to hunt — "find the case where this returns stale data", "find the input that makes this throw", "find what the order asked for that is missing" — return three different reviews. In this profile, always split the lens.
4. **Objective gates the orchestrator runs.** Tests, typecheck, a runtime assertion on real state, a screenshot you read yourself. These are model-independent, so they carry more weight here than in a mixed run. Push more of the acceptance burden onto them.
5. **Effort asymmetry.** Opus 5.5 at `high` reviewing Opus 5.5 at `medium`. The weakest substitute — same priors, more of them. Never the only one.

**The gate:** nothing ships on substitute 5 alone. Critical work needs (1) plus (2) plus (4). Routine work needs (1) plus (4), or (1) with the orchestrator reading the diff. Anything that leaves the building is critical by definition.

## Routing

| Work | Model | Effort and reason |
|---|---|---|
| Grounding, plan, work orders, integration, final acceptance | orchestrator (Opus 5.5, or Fable 5.1 if it holds the seat) | high — orchestrator judgment |
| Mechanical edits with exact anchors, one item per lane | opus (`bulk-lane`) | low — established pattern, clear acceptance |
| Well-specified implementation against a clear contract | opus | medium — defined behaviour and scope |
| Terminal, DevOps, infra, CI, migrations, SRE | opus | medium, or high when the lane is hard — state, retries and recovery paths |
| Messy repo-level bug hunt, unknown scope | opus | high; on observed failure, Fable 5.1 at high |
| Long-horizon repo or document work (hours, or across sessions), including documents, sheets and decks from a blank page | opus | medium or high — the order carries the unattended-lane paragraph |
| Ambiguous architecture, deep research, or any lane where Opus 5.5 at high has fallen short | fable | high — the escalation step past the Opus ceiling |
| Design, UI, layout, copy-in-a-UI, API shape | opus (`design-lane`) | high — taste is the acceptance test; the order names the stock patterns to avoid |
| Design of a critical surface (flagship UI, client-facing deliverable) | fable | high — critical design |
| Writing, high stakes (counterparty, proposal, board) | fable (`write-lane` where installed) | high — voice is the deliverable |
| Writing, volume or structured (first drafts, prompt packages, internal docs) | opus | medium — with the write-lane constraints in the order |
| Runtime verification, known steps and a stated assertion | opus | medium — execution mechanics |
| Runtime verification, judgment while driving the screen | opus | high — next action depends on reading the screen |
| Review of routine Opus work | opus, a separate lane in fresh context | high — context-independent, same model; labelled `same-model, fresh context` |
| Adversarial review of critical Opus work | fable (`verify-lane` where its frontmatter pins fable/high) | high — a different model from the author |
| Adversarial review of Fable work | opus | high — a different model from the author |

**Increase Opus effort before changing models, stopping at `high`.** Opus 5.5 uses `low` for mechanical sweeps, `medium` for implementation, execution and investigation, and `high` for the main loop, design, bug hunts and review. `high` is the ceiling: `xhigh` buys about two points for double the cost and `max` scores lower than `xhigh`. Before moving a lane opus → fable, re-run it at the next effort up to `high`; past `high`, change the model instead. Before dropping a lane for cost, drop effort. Opus 5.5 thinks more per effort level than Opus 5 did, so set effort explicitly on every lane and do not carry old `xhigh` settings forward. Fable 5.1 runs at `high`. The standing exception is unchanged: never run Fable at `low` for anything that must look something up — at `low` it answers from memory instead of searching.

**When Fable is unavailable** (its own limit, or a shared allowance already spent), the Fable rows fall back to Opus 5.5 at `high` in fresh context, and the review label drops from `cross-model` to `same-model, fresh context`. Do not raise Opus above `high` to make up for the missing model. Say so in the report. A Fable-specific limit does not establish Opus availability and switching models does not bypass an exhausted shared allowance.

**Never** Haiku for judgment work. **Never** Fast mode on a dispatched lane — same intelligence at twice the price, for faster tokens nobody is watching.

### Mechanics: pinning model and effort

The `Agent` tool takes `model:` but has **no effort parameter** — a subagent dispatched through it inherits the session's effort. Three ways to pin both, in order of preference:

- **A bundled lane agent**, whose frontmatter sets `model:` and `effort:` — `design-lane` (opus/high), `exec-lane` (opus/medium), `bulk-lane` (opus/low), `verify-lane` (fable/high, for critical review). Check what is actually installed before naming one: on the bench `write-lane` is **not** installed, so a high-stakes writing lane is a plain `Agent` with `model: 'fable'` carrying the write-lane rules in its prompt. Read the agent's own frontmatter rather than trusting a routing table's description of it. An older install may still pin `design-lane` to opus/xhigh or `verify-lane` to opus/max; if so, dispatch the lane through a `Workflow` with the model and effort set inline.
- **A `Workflow` script**, where `agent(prompt, {model: 'fable', effort: 'high'})` sets both inline. This is also where fan-out and pipelining live.
- **The `Agent` tool with `model:` alone**, accepting the session's effort. Fine when the session is already at the effort the lane wants, which at `high` it usually is for review lanes.

`model: 'opus'` resolves to Opus 5.5 (`claude-opus-5-5`); `model: 'fable'` resolves to Fable 5.1 (`claude-fable-5-1`).

## Lanes that used to be Codex's

| Was | Now | What the order must add |
|---|---|---|
| Mechanical sweep on the Codex overflow lane (GPT-6.1 Sol `high`), one lane per item | `bulk-lane` (opus/low), still one lane per item | Nothing new — use the default mechanical-sweep lane, one item per order. Keep the fan-out wide; cheap lanes are where width belongs. |
| Terminal / infra / migration; GPT-6.1 Sol `high` when ops-, runbook- or automation-shaped | opus at `medium`, or `high` when the lane is hard | Exact commands, exact paths, what not to touch, and "stop and report if an anchor does not match" instead of improvising. Steerability is Opus 5.5's lowest-rated axis (provisional), and terminal work is where a lane that drifts from the order does the most damage. |
| Patterned multi-file refactor | opus at `medium`, one lane per file or per module | Name the contract precisely and the files exhaustively. Do not let a lane decide which files are in scope. |
| Runtime verification, `codex-computer-use` | an Opus lane driving `agent-browser` with its own `--session <lane>` | Same steps-and-assertion contract. The evidence gate in the shared source still decides screenshots vs video. Native Android/iOS goes to `mobile-app-testing` with a Claude driver. |
| Cross-family diff review, `codex-review` (GPT-6.1 Sol `high`; `xhigh` for critical) | the review rows above, under the substitutes | Fresh context, artifact only, one lens per reviewer. Label it honestly. |
| Volume writing on a Codex lane | opus at `medium` | This is the lane that degrades most. See below. |

**Writing is where a single family costs you most.** The Codex lane was the volume writer precisely because it is not Claude and does not reproduce Claude's tics. With it gone, every writing order in this profile — not just the high-stakes one — carries the `write-lane` constraints explicitly: short paragraphs, break every three sentences; no "it's not X, it's Y"; no tricolons; no pre-emptive caveats; no closing flourish or summary line; no em-dash cadence. State audience, register, length ceiling, the one thing the reader must do, the banned phrases and a sample of the voice. Then the orchestrator reads the draft against the voice sample and de-slops it by hand. Assume the tics are there; a same-family reviewer will not see them.

## The loop

The full run, end to end. Steps 1, 4 and 5 are yours and are never delegated. Step 2 is the team. Step 3 is where this profile differs from the mixed one.

**1. Plan — orchestrator.** Scout the code yourself: `Grep`, `Glob`, `Read`, `git log`. Do not dispatch agents to find out what the work is. Then decompose into work orders. A work order that a cheap lane can execute is *precise*: the whole task in one message, exact file paths and line anchors, the data contracts involved, an explicit finish line written as "Done means: …" with the acceptance check stated as an observable ("the roster renders 4 rows at 390px with no horizontal scroll"), what NOT to touch, and the deliverable path. Vague orders waste the lane's run and your review time, and in this profile they waste the same quota pool twice.

Every order also carries its routing — `profile: conductor-claude`, `model`, `effort`, the reason, whether the work is critical or routine, and the review coverage it will get — so the report can be assembled from the orders rather than reconstructed afterwards.

Effort is the control for how hard a lane thinks. Do not write "think carefully" or "think step by step" into an order, and never ask a lane to write its reasoning out in the reply; that can trigger the `reasoning_extraction` refusal. Ask for the result and the evidence. A review order uses this prompt for its findings: "List only problems that block merge: file, line, why it is wrong, and how to show it fails." A design order names the stock patterns to avoid. Opus 5.5's defaults are a cream or off-white background, italic accent words in headings, numbered "01 / 02 / 03" section labels, monospace labels and pill-shaped buttons; ban them in product UI unless the project's design system already uses them, and add whatever else the project chose against.

Every dispatched order ends with the unattended-lane paragraph below, Anthropic's wording from the Opus 5.5 prompting guide. Never put it in the main loop, where Ivan may be there to answer. A fan-out order also carries a time budget ("aim to finish within 20 minutes"), set somewhat above what you want spent; Opus 5.5 paces itself to elapsed time, and the budget is advisory, so keep your own timeout.

> A standing instruction from the user, the person you are working for. It is about how your turns end. A message with no tool call in it ends your turn, and the work stops there until you are asked to continue. The user has seen you end turns in four ways while work they asked for was still owed, and does not want any of them. One: a long summary of what was done that closes by announcing the next step and has no tool call, so the next thing never starts. Two: an offer to carry on with something unless the user would prefer otherwise, which stops to wait for an answer the user was not going to give. Three: a list of decisions for the user when, by your own account, none of them blocks the rest of the work. Four: deciding that this is a good place to report, because the turn has been long or a milestone is done. Status notes are welcome, and so are your recommendations on open decisions, but put them in the same message as your next tool call and carry on with whatever does not depend on the user's answer. If you notice yourself inviting the user to redirect you or offering to wait, delete it and do the next thing. The stops the user does want are the ones where nothing can move without them, or where the thing blocking you is deliberately protected from you. This does not override the need for confirmation on risky or destructive actions.

**2. Dispatch — parallel.** Note the run's start time. If the run has a tracking issue, flip its label (`gh issue edit <n> -R <owner>/<repo> --add-label status:running`). Then launch every independent lane **in the same turn** — independent `Agent` calls in one message run concurrently.

Choose the mode with the shared **Turn-by-turn or Workflow** table; in this profile every lane is Claude, so a Workflow never needs a Codex wrapper.

- **Two or three lanes, no pipelining, or a lane whose order depends on a judgment you make after reading the previous result:** the `Agent` tool, one call per lane, all in one message. Use a bundled lane agent when you need the effort pinned.
- **An enumerated work-list of 3+ items, review stacked on top of build, competing drafts to judge, a fix-until-green loop, or a run long enough that an interruption would hurt:** a `Workflow` script, where `agent(prompt, {model, effort})` sets both per lane and `parallel()` / `pipeline()` express the shape. Pipeline by default so each item's review starts the moment its build finishes instead of waiting for the slowest sibling:

  ```js
  const results = await pipeline(
    ITEMS,
    it => agent(orderFor(it), {label: `build:${it.key}`, phase: 'Build',
                               model: 'opus', effort: 'medium', schema: BUILD}),
    build => agent(reviewOrder(build), {label: `review:${build.key}`, phase: 'Review',
                                        model: build.critical ? 'fable' : 'opus',
                                        effort: 'high', schema: VERDICT}),
  )
  ```

  The review stage is always a fresh agent that sees only the requirements and the diff. On critical items it also flips the model, which wires substitute 2 into the shape of the run; on routine items it stays on Opus 5.5 and the label says `same-model, fresh context`.

- **Writers get isolation.** `isolation: "worktree"` on any lane that edits files, auto-cleaned when unchanged. **No two write lanes share a file.** If two orders must touch the same file, serialize them or give the file to one lane and a follow-up order to the other.
- **Do not poll.** Background agents are harness-tracked: you are re-invoked automatically when one finishes. A wait loop, a sleep, or a repeated file-existence check costs tokens and buys nothing. Dispatch, then do something independent or end the turn. A lane that has gone quiet past its expected span is dead, not slow — read its transcript rather than waiting longer.

**3. Cross-verify — the substitutes, applied.** Every lane's output is checked by something that did not write it. In this profile that means, in order: a reviewer in fresh context, given the requirements and the diff and nothing else — Fable 5.1 for critical Opus work, a separate Opus 5.5 lane for routine Opus work, Opus 5.5 for Fable work; one failure-mode lens per reviewer where a finding can fail in more than one way; and at least one objective gate — typecheck, tests, a runtime assertion on real state, or a screenshot.

You read the screenshots yourself. No lane certifies its own design quality, and in a single-family run no lane certifies another's either — a clean review here is weaker evidence than it would be from the other family, so spend the objective gate as well.

**4. Review and integrate — orchestrator.** Read every lane's report *and* the actual diffs: `git diff --stat`, then the files that matter. Reports are claims. Rejected work goes back as a **revised work order** — what was wrong and what correct looks like — not a re-explanation of the task. Merge the lanes' branches or worktrees yourself, resolve the conflicts yourself, and run the final gates appropriate to what changed. The integration is the orchestrator's job precisely because no lane saw the whole.

**5. Publish — orchestrator.** Write or update the run's review HTML per the shared Report design contract, with the coverage labels from this profile's table visible per lane. On the bench, publish with `~/bin/report-link.py <report-path>`, check the served URL, and hand over the hub link labelled **private — Tailscale access required**. Then close through `run-report` where available and authorized.

## Running the team

A few rules that keep a Claude-only team from thrashing, beyond the shared sizing gate:

- **One owner per mutable thing.** One lane per file, per fixture, per browser session (`--session <lane>`, never the shared one), per device. Overlapping writers get serialized, not merged optimistically.
- **State the lane's boundaries in the order, not in your head.** Every order says what not to touch, says "do this yourself, do not spawn subagents" unless you budgeted recursion, and asks the lane to end its report with three headings: **Needs you**, **Changed**, **Found**. Anything the lane could not confirm is marked as unconfirmed, with where it looked; what it did not do goes under **Needs you** or **Found**.
- **No self-verification scaffolding in orders.** "Double-check your work", "add a verification step", "spawn a verifier" produces over-verification and burned quota, not rigour — these models already self-verify. Verification lives in step 3, which is yours.
- **Lanes checkpoint.** A lane that dies on the session limit leaves no report and no commit. Long write lanes commit incrementally or write their artifact as they go, so an interrupted lane leaves recoverable work rather than nothing.
- **Track the work-list.** Queued, running, done, blocked. When you bound coverage for quota, `log()` what you dropped so a partial sweep never reads as a complete one.


## Long-horizon runs

The shared **Long-horizon runs** section governs: the work-list is a file rather than a memory, ambition is phased into waves rather than flattened into one fan-out, lanes checkpoint at wave boundaries, and a `Workflow` resumes with `resumeFromRunId`. Read it there. Its **Context handoff** rules apply unchanged: at 70% context the `context-watch` hook prompts you, and `conductor-handoff` starts the successor with `/conductor-claude`, because it reuses the skill this session loaded.

Two things are sharper in this profile, and both argue for *more* structure on a long run, not less ambition:

- **The interruption you should plan for is the usage limit**, and it arrives without an error — a lane simply stops, with no report and no commit. On a multi-hour run this is the single most likely failure. Wave boundaries, committed lanes and an on-disk work-list are what turn that from a lost run into a resumed one.
- **The whole run draws on one pool**, so the phase plan is also the budget plan. Decide before wave 1 roughly what each wave costs in lanes × effort, and put the expensive judgment (Opus 5.5 or Fable 5.1 at `high`) in the narrow waves — contract design, integration review — while the wide waves stay at `low`/`medium`. A run that spends its window on wave 1 has not been ambitious; it has been unplanned.


## Fan-out and the quota budget

The shared **What earns an agent** and **Sizing the fan-out** sections still govern *whether* and *how many*. Scouting is still yours — a grep, not a lane. One agent per independent item. The size guideline is a ceiling, not a target.

What changes is that every lane now draws on one pool. Budget before dispatching, not after:

- **Count lanes × effort before the first dispatch.** A twelve-lane `high` fan-out and a twelve-lane `low` fan-out are not the same run. If the work-list will not fit, cut coverage deliberately at the top — take the top-N items, drop retries, sample — and `log()` what you dropped so a partial sweep never reads as a complete one. Discovering the ceiling half-way through leaves a run nobody can finish or trust.
- **Default to Opus 5.5 on price.** Opus 5.5 costs $4/$20 per Mtok with cache reads at $0.20; Fable 5.1 costs $10/$50 with cache reads at $0.25. Opus 5.5 is cheaper on input, output and cache reads, so spend Fable only on the rows the routing table gives it: review and design of critical work, high-stakes writing, ambiguous architecture and the escalation past `high`. Without Codex, effort and the Opus/Fable split are the cost levers you have left.
- **Wide and cheap beats few and long.** On resume, cached results stop at the first unfinished lane and everything after it re-runs. Many small lanes preserve more progress. That matters more here, because the thing most likely to interrupt a run is the limit itself.
- **Tighter orders are cheaper than bigger models.** The ten minutes of grounding that makes a `low` lane succeed is the cheapest token you will spend all run.

## Failure modes specific to this profile

- **A Claude lane dies silently on the session limit.** No report, no commit, no error you will see — only the lane's own transcript says so. A lane that has gone quiet past its expected span is dead, not slow: read its transcript rather than waiting. Counter it in the order: have write lanes commit or write their artifact incrementally rather than holding everything for a final message.
- **Opus 5.5's behaviours.** Unattended lanes can end a turn after a progress update, so every order carries the unattended-lane paragraph, and a lane's text-only ending is a report, not proof the work is done: check its work-list and name the open items when you send it back. It thinks more per effort level than Opus 5 did, so set effort explicitly, never above `high`, and lower effort rather than prompting for less thinking; the order-writing rules in step 1 cover the rest. It gets to work quickly, so on tasks spread across mail, documents, sheets or records, tell it to look through the relevant sources before it changes anything. On design with no direction it falls back on the stock patterns listed in step 1. With no other-family reviewer, and with routine work reviewed by the same model, your diff read is the gate that catches a lane that stopped early. Read the diff, not the summary.
- **Fable's four behaviours.** Say "issue independent reads in one turn" (it batches less than Fable 5 did); say "targeted edits only" (it rewrites whole files for small changes); never dispatch it at `low` for research or verification; ask for paragraph breaks explicitly in writing orders.
- **Reviewer agreement is not evidence.** In a single family, two lanes agreeing is weaker evidence than it feels. When a review comes back clean on something that ships, spend one objective gate on it anyway — a test, an assertion, a screenshot you read.
- **Label drift.** The word `cross-family` must not appear in a Conductor Claude report. Different effort levels are not different families; different Claude models are not different families.

## Review, acceptance and honest labels

The implementing lane's self-report is a claim. The orchestrator reads the diff, the artifacts and the actual verification output before acceptance. Rejected work goes back as a *revised* work order — what was wrong and what correct looks like — not a re-explanation of the task.

Use exactly these coverage labels in the report:

| Label | Means |
|---|---|
| `cross-model, fresh context` | Fable 5.1 reviewed critical Opus 5.5 work, or Opus 5.5 reviewed Fable 5.1 work, from requirements + artifact only |
| `same-model, fresh context` | A separate Opus 5.5 lane at `high` reviewed Opus 5.5 work from requirements + artifact only, without the author's rationale. The standard review for routine work, and the fallback for critical work when Fable was unavailable (say which) |
| `objective-gate` | Tests, typecheck, runtime assertion or a screenshot the orchestrator read |
| `orchestrator-only` | Inline work with no separate reviewer |

Name what each covered. A design critique does not make an implementation reviewed. Unresolved acceptance failures stay failures regardless of what was unavailable — report what was exercised, what was not, and the residual risk, without claiming a pass by substitution. Existing authorization to commit, push, merge, send or deploy is unchanged; this profile does not broaden it.

## Returning to mixed-model

When a Codex account comes back (`codex-account pick` exits 0), decide deliberately rather than drifting:

- Work already shipped stays shipped. Do not re-review it for the label.
- Work not yet shipped, that is user-facing or carries Ivan's name, gets one cross-family review pass before it goes — `codex-review` with `-m gpt-6.1-sol --effort high`, or `-m gpt-6.1-sol --effort xhigh` when it is critical — and the report label is upgraded to `cross-family` only for what that pass actually covered.
- The run's report says which parts were single-family reviewed and which were not. That sentence is the deliverable of this whole profile.

## Worked example (shape, not script)

> Task: "Six API routes need the new tenant-scoping middleware, and the settings page needs a tenant switcher. Ship it."

1. **Scout, yourself.** `grep -rl "withAuth(" src/routes` returns the six files. `Read` the middleware and one route. That is the work-list — no agent produced it, and it cost two commands.
2. **Plan.** Six mechanical route edits (identical contract, exact anchors) plus one design surface (the switcher). Seven orders. Each names its files, the contract, "Done means: …", what not to touch, and whether it is critical. Tenant scoping is auth, so the route edits are critical; the switcher is a settings control, not a flagship surface, so its design is routine.
3. **Dispatch, one turn.** Six `bulk-lane` agents (opus/low), one per route, `isolation: "worktree"` — not two agents with three files each, which would silently drop coverage. Plus one `design-lane` (opus/high) for the switcher. Seven lanes, not three; they are cheap and genuinely independent.
4. **Verify.** The routes are critical, so the combined six-route diff gets a Fable review in fresh context with the lens "find the route where one tenant can read another tenant's rows", plus typecheck and the existing route tests, run by you. The switcher is routine, so a separate Opus 5.5 lane at `high` reviews it in fresh context — the requirements and the diff, not the design lane's rationale — with the lens "find what the order asked for that is missing", plus a screenshot at 390px that **you** read. Coverage: `cross-model, fresh context` + `objective-gate` for the routes, `same-model, fresh context` + `objective-gate` for the switcher.
5. **Integrate.** You merge the seven worktrees, resolve the one real conflict in the shared middleware import, run the full gates, and read the combined diff. No lane saw all seven changes; you do.
6. **Publish.** Update `.conductor/reports/issue-<n>.html`: what was asked, the seven lanes and their outcomes, the per-lane coverage labels, the switcher screenshot, and one line of residual risk — the switcher was reviewed by the same model that built it, which is a deliberate trade and is stated as one. Hub URL, labelled private.


## Closing

Close through the shared contract: the run review HTML at `<repo>/.conductor/reports/` (light editorial, per the Report design contract), delivered on the bench as a verified hub URL via `~/bin/report-link.py` and labelled **private — Tailscale access required**, then the **`run-report`** skill where available and authorized. A run without a report is invisible work.
