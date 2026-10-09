---
name: verify-skill-maintain
description: Scheduled upkeep pass that keeps a project's verification skill and feature map true to the app — checker first, one source reader per feature file, one live pass that drives every feature, then at most one PR of proven corrections. Product regressions found on the way are reported, never written into the map. Use for /verify-skill-maintain, "audit the verify skill", "is the feature map still right", the daily maintenance timer, or after a large merge wave.
disable-model-invocation: true
---

# Maintain a verification skill

A feature map goes stale as soon as the app changes. `feature-map-update` catches most changes in
the pull request that makes them; this pass catches the rest: renamed buttons, moved menus,
permission changes, merges that skipped the rule, and helper commands that no longer work. The unit
of rigour is the feature: every feature file gets a source read and a live drive, without testing
every sentence.

Adapted from poteto's `maintain-verification-skill` (pstack, MIT), routed for Conductor.

## Outcomes

Report exactly one:

- **clean**: every feature had source and live coverage and nothing needed changing. No branch, no PR.
- **changed**: one PR with proven corrections to the skill's own files.
- **blocked**: coverage could not finish, or a proven fix could not ship. Say exactly what blocked it.

## Edit scope

Only the verification skill's directory: `SKILL.md`, `features/`, the helper and its scripts.
Never product code. When the map describes something the app no longer does, decide which it is:
the map drifted (fix the map) or the product regressed (report it with evidence, leave the map
alone, and file an issue if the run is authorised to).

## Pass

0. **Locate the target.** The project-local skill with a helper and `features/` (for example
   `.claude/skills/verify-mikono/`). Several: ask which (unattended: the one the timer names). None:
   stop and point at `verify-skill-create`.

1. **Checker.** Run the plugin's copy, which carries the tests:
   `python3 <verify-skill-create's directory>/scripts/feature_map_check.py <skill>/features` (on the
   bench `~/.claude/skills/verify-skill-create/`; in a plugin install
   `${CLAUDE_PLUGIN_ROOT}/skills/verify-skill-create/`),
   adding `--base <the base SHA the last pass covered>` on a scheduled pass to list the features whose
   sources changed since. If the repo's vendored copy reports an older `--version`, replace it in
   this pass's PR.
   Fix index hygiene first: missing, extra, duplicate or dead entries; malformed files. List
   uncovered routes; each one either joins a feature's `sources` and gets a section, or goes into
   `route_ignore` with a reason.

2. **Source wave.** One read-only lane per feature file (GPT-6.1 Sol `high` via `ask-codex`, with
   "do not edit files" in the order; Opus 5.5 `medium` when Codex quota is out), at most 6 at once
   on the bench. Prioritise the features the checker
   flagged; a full pass covers all of them. Each lane reads the feature file and the code its
   `sources` name and returns: a one-paragraph summary of how the feature works now, likely drift
   with `file:line` citations (labels, routes, persona gates, new sub-features), and one live
   recipe to confirm it. Lanes never drive the app and never edit files.

3. **Reconcile.** Every feature file has a returned summary. Spot-check cited drift in the source
   yourself; do not re-prove claims of no drift. Merge the recipes into as few sign-ins as practical
   (group by persona).

4. **Live pass.** Required even when the source looks clean. One driver owns the browser (you, or
   one Opus 5.5 lane). Use the helper's own commands. Three invariants for the whole pass:
   - run `doctor` before the first drive and after any failed drive; when doctor cannot see the
     failure (a stuck dialog on a healthy app), reset with `open` on the persona's home or `stop`
     and sign in again, rather than hoping;
   - evidence captured so far survives every cleanup; check its directory, do not assume;
   - nothing a drive started outlives its usefulness; `stop` after failed attempts too.
   A doctor failure caused by skill drift (a changed sign-in screen, a moved route) is drift: fix it
   under edit scope, re-run doctor once, and call the pass `blocked` only if it still fails. Clean
   the residue, not the instance: the backend is shared, so name every row a drive created, remove it
   through the UI where the app allows, and otherwise report it with its identifier. Use `target` on
   the test track; never `launch` a dev server for this pass.
   Drive every feature at least once: its main entry point, plus every recipe step the source wave
   flagged. A feature that cannot be reached is `unreachable` only with the concrete prerequisite
   (persona, permission, seeded data, external service) and the route you tried; if the map omits
   that prerequisite, that is drift. Keep to the map's write policy for shared data.

5. **Triage.** Wrong or missing user-facing description: map drift, fix it. Working behaviour the
   helper cannot drive: helper gap, fix it and re-drive it live. Broken app behaviour: product
   regression, record it for the report and keep it out of the PR.

6. **Ship or stop.** For `changed`: re-run the checker, re-read every changed file, open one PR to
   the project's base with the corrections and the evidence links; follow the project's merge rules
   (Mikono's completion contract authorises merging to `develop` behind the Vercel gate). For
   `clean` or `blocked`: no PR.

## Report

Outcome, features covered (source and live), drift fixed, helper fixes, unreachable features with
their prerequisites, product regressions with evidence, the PR link. On the bench, publish it as a
report page and give the hub URL.

## Cadence

Daily on an active product, and after any merge wave of more than about ten PRs. This skill does not
invoke itself. On the bench a `systemd --user` timer starts a headless `claude -p` session that runs
`/verify-skill-maintain` in a dedicated worktree of the base branch, at a time no verify lane is
driving the same test track. Record the base SHA each pass covered so the next pass starts there.
