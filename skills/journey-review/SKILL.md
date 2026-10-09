---
name: journey-review
description: Walk a persona's real job through a product (a salesperson visiting an outlet, taking an order, adjusting it, collecting payment, giving a receipt; a back-office user settling a truck) using the project's feature map and helper, find where the flow does not match how that person works or is not intuitive, investigate why in the code, design the better workflow, and fix it or file it with the proposal. Use for "/journey-review", "is this flow intuitive", "walk the salesperson's day", "the visit flow feels clunky", "review the UX of <journey>", "make the payment flow easier", or after a feature map exists and a journey matters to clients. Works with verify-skill-* (maps and helpers), build-flow-contract (scored checks), uiux-review (screen polish) and flow-wireframe (proposals).
disable-model-invocation: true
---

# Review a user journey

A feature map says where each screen is. A journey says what a person is trying to get done, across
screens, in the order their work happens. Most UX problems that matter live between screens: a
salesperson at an outlet has to collect cash before the app lets them print, has to leave the sale to
fix a quantity, re-types a customer the visit already knows, or cannot find how to take part payment.
No single screen looks wrong, yet the job is slow and confusing. This skill finds those problems,
finds their cause, designs the better flow and gets it built.

It sits on top of the project's verification skill (`.claude/skills/verify-<app>/`): the helper drives
the app and the feature map says where things are. It does not judge colours, spacing or one screen's
layout; hand that to `uiux-review`.

## 0. Inputs

- The project's verification skill and feature map. None: run `verify-skill-create` first.
- The journey: who (persona and where they are: in an outlet on a phone, at a depot desk), the job
  in their own words, how often they do it, and what is at stake (money, stock, a customer waiting).
- The product's own rules: `AGENTS.md`, any product contract (`docs/product-contract.md` in Mikono),
  domain rules that constrain order (an invoice before a receipt; stock issued before it is sold).

## 1. Write the journey file

`features/journeys/<id>.md` next to the feature map, so the journey is maintained like a feature and
reused by verification and demo videos. Shape: [`references/journey-template.md`](references/journey-template.md).
Front matter `id`, `persona`, `surface`, `features` (the feature ids it crosses), `sources`. Then:

- `Goal and context`: the job, where and how often it happens, the stakes.
- `Steps the user expects`: the sequence as the person thinks of it, from domain knowledge and the
  product's own vocabulary, written before you look at the app. This is the yardstick.
- `Path in the app`: the routes, screens and controls the app makes them use today, in order.
- `Driving it with <harness>`: preconditions and the commands to walk it, stopping before any write
  the feature map does not mark safe.
- `Gotchas`: what invalidates a walk (demo data, persona gating, offline behaviour).

Give the journey an id no feature file uses. Register it in `features/README.md` under a `## Journeys`
heading (`- [Title](./journeys/<id>.md) covers …`), and make sure the project's checker understands
journeys: `python3 <skill>/scripts/feature_map_check.py --version` must report 4 or later; if it is
older, copy the current one from `verify-skill-create/scripts/` in the same pull request, so CI checks
the journey too. Then run the checker; it validates the journey's sections and the features it lists.

Write `Steps the user expects` first. If you write it after walking the app, the app's sequence leaks
into the yardstick and every flow looks intuitive.

## 2. Walk it and keep a step ledger

Walk the journey as the persona, on the surface they use (native app through `mobile-app-testing`
when that is where they work; the web helper otherwise). Record a ledger, one row per user action:
screen, action, input typed, taps or clicks, waits, decisions the user had to make, errors, back
navigation, and whether the step serves the goal (essential) or the app (overhead). Save a screenshot
per screen and, for a journey that will be redesigned, a recording: it is the "before" evidence.

Read the code for each screen as you go (`how` for an unfamiliar subsystem): what the screen requires,
what it defaults, what it validates, what it does on commit. Steps you cannot drive without writing
shared data are walked to the confirm button and completed from source, labelled so.

## 3. Find the friction

Compare the ledger with `Steps the user expects`. Look for, and cite the step and the code for each:

- **Order mismatch**: the app asks for things in a different order than the work happens.
- **Overhead steps**: steps that serve the system, not the job (choose a list before the only option,
  re-confirm a customer the visit already fixed, a modal that only says "OK").
- **Re-entry**: typing what the app already knows (customer, price, the amount just sold).
- **Dead ends and detours**: no way back without losing work; fixing a quantity means leaving the
  sale; the next action is hidden behind a menu.
- **Mode and surface switches**: jumping between tabs, apps or web and phone to finish one job.
- **Unclear state**: after a commit, the user cannot tell what happened (paid, partly paid, synced,
  printed), or two words name one thing.
- **Field conditions**: one hand, sunlight, slow or no network, a customer waiting; long forms,
  small targets and spinners hurt more here.
- **Error recovery**: a mistake (wrong product, wrong tender) has no simple undo before or after commit.
- **Gating**: the persona can see a step but not complete it, or the reverse.

Rate each finding by impact on the job (blocks, slows every time, slows sometimes, cosmetic) and how
often the journey runs. Count essential versus overhead steps; the ratio is the journey's baseline.

## 4. Find the cause

For the top findings, find why the flow is shaped that way before proposing a change: the data model
forces the order (a payment needs an invoice id), a component is shared with a desktop flow, a
permission check, an offline-sync constraint, or nobody designed it. A redesign that ignores a real
constraint will be rejected in review; a constraint that turns out to be an accident is the cheapest
fix of all.

## 5. Design the better flow

For each journey with material friction, sketch two or three alternative flows (one that keeps the
current screens and only reorders or pre-fills; one that merges or removes steps; one bolder if the
constraint allows it). Judge them against the yardstick, the domain rules and the product contract,
and pick one with the reason. Write the chosen flow as a target ledger: the same columns, fewer
overhead steps. For non-trivial UI, produce a `flow-wireframe` in the project's design language.

Money, stock and anything a client sees is a critical design surface: the design pass runs on
Fable 5.1 at `high`, or Opus 5.5 at `high` with a Fable review.

## 6. Fix or file

Sort the changes:

- **Fix now**: copy, defaults, pre-fills, ordering within a screen, a missing link or back path, a
  confirmation on a destructive action. Implement in the project's normal PR flow, update the feature
  and journey files in the same PR (`feature-map-update`), and re-walk the journey.
- **Propose**: merging or removing screens, changing the order the domain enforces, new components.
  File an issue with the before ledger, the target ledger, the alternatives considered, the wireframe
  and the acceptance checks. Follow the repo's rules on what needs the owner first.
- **Ask**: a product decision only the owner can make (a policy on credit, who may discount). Put
  it to them with your recommendation and what each answer changes.

## 7. Prove it and keep it proved

After a fix, walk the journey again and compare the ledgers: overhead steps removed, time, the
findings closed. Record the after video next to the before. Turn the journey's measurable facts into
a flow contract with `build-flow-contract` (for example: essential steps unchanged, overhead steps at
most N, no re-entry of the customer, a receipt reachable in one action after payment), so
`run-flow-contract` catches a regression later.

## Report

Lead with the job and the verdict for each journey (works, slows the user, blocks), then the
findings ranked by impact with their evidence, the before and target ledgers side by side, the
chosen redesign and why, what was fixed, what was filed and what needs a decision. On the bench,
publish a report page.

## Routing

- Lanes return the ledger and findings in their final message when the harness refuses report-like
  files from subagents; the orchestrator saves them.
- Walking and judging intuitiveness: Opus 5.5 at `high` (taste and judgment); runtime mechanics on a
  device can go to GPT-6.1 Sol at `high` through `mobile-app-testing`, with Claude judging the screens.
- Design of money or client-facing flows: Fable 5.1 at `high`, or Opus 5.5 `high` plus Fable review.
- Implementation: Opus 5.5 at `medium`. Review: GPT-6.1 Sol at `high` for routine flows. A change to
  money, stock or a client-facing flow is critical: GPT-6.1 Sol at `xhigh` and a Fable 5.1 `high`
  judgment review of the implementation itself, not only of the design.
