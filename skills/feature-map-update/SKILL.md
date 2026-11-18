---
name: feature-map-update
description: Keep a project's feature map true in the same pull request that changes the app. Runs the map checker against the branch's base, lists the feature files the diff touches and any new route no feature covers, records each change as a new change-note file (or, on a map without notes, edits the feature file) from the changed code, and re-drives the changed recipe steps live. Use before opening or finishing any PR in a repo with a `.claude/skills/verify-*/features/` map, when the checker flags a touched feature, when a build lane changes a route, label, menu or permission, or for "update the feature map".
---

# Update the feature map with the change

The map is shared memory for every agent on the project. If a PR moves a button and leaves the map
alone, the next verify lane follows a recipe that no longer works, fails, and burns its run finding
out why. The cheapest time to fix the map is in the PR that changed the app, while the author still
knows what changed.

This is the in-PR half of the upkeep loop. The scheduled half is `verify-skill-maintain`.

## When it applies

The repo has a verification skill with a map: `ls .claude/skills/verify-*/features/map.json`. If
not, there is nothing to update; `verify-skill-create` makes one.

## Steps

1. **Run the checker against the base.**
   ```bash
   python3 .claude/skills/verify-<app>/scripts/feature_map_check.py \
     .claude/skills/verify-<app>/features --base origin/<base>
   ```
   It fails when your diff touched the `sources` of a feature or a journey (`features/journeys/`)
   and you neither changed its file nor added a note for it (step 3), and when
   your branch added a route no feature covers. The repo's CI runs the same check on the PR.

2. **Decide per touched feature.** Read the feature file next to your diff, with its pending
   notes (`features/notes/<id>/`) and its `### Change notes`; a pending note wins over the body.
   Ask one question: does a user reach, see or do anything differently? A new or renamed route,
   button, label, tab, menu item, dialog, empty state, a persona gaining or losing access, a new
   sub-feature, a removed one: record it (step 3). A refactor, a backend fix with the same UI, a
   style change: leave it, pass `--allow-unchanged <feature-id>` locally, and put the line
   `map unchanged: <feature-id> — <reason>` in the PR description, which CI reads.

3. **Record the change.** When `features/notes/README.md` exists, the map takes change notes:
   for each touched feature or journey write a NEW file `features/notes/<key>/<issue>-<slug>.md`,
   where `<key>` is the feature id or `journeys/<journey-id>` and the name matches
   `^[a-z0-9][a-z0-9-]*\.md$` (pick another slug if the path exists). One note per key in a PR,
   each saying what changed for that feature:
   ```markdown
   ---
   issue: 6942
   date: 2026-11-18
   about: go-order-prepayment
   ---
   At the stop and on New Sale a bank transfer's "Transfer reference (optional)" may be left blank.
   From source and tests, not driven on a device.
   ```
   `issue` and `date` are required; `about` is optional and is an id (the sub-feature, step or
   gotcha), never free text. The body has no H1 or H2, one sentence per line: what a user now
   reaches, sees or does, and how it was checked. Notes are append-only: never edit or rename one
   that is already on the base; add another. Edit the feature file itself only to correct a line
   the change made wrong (a renamed button, a removed path) or to add a route to `sources`; never
   append a dated change line to it (the checker warns, and the bench poller fails, on `#NNNN`
   plus a date). A daily job folds merged notes into the feature files. Without the marker file,
   edit the feature file in place as below.

   **Edit the file.** Targeted edits only. Keep its contract: a feature file has front matter, an
   H1, one paragraph and four H2s (`Sub-features`, `How to get to it (user POV)`, `Driving it with
   <harness>`, `Gotchas`); a journey file has front matter with `persona` and `features`, an H1 and
   five H2s (`Goal and context`, `Steps the user expects`, `Path in the app`, `Driving it with
   <harness>`, `Gotchas`). Add new route files to `sources`. A new route either joins an
   existing feature or gets its own feature file plus an index line in `features/README.md`.
   Use the accessible names your code renders, not the names you meant.

4. **Re-drive what you changed.** For each recipe step you added or edited, run it with the
   project's helper against your build (`$H launch` for local work, `$H target <preview-url>` for
   a pushed branch) and confirm the observable result. A step you could not drive is marked
   "from source, not driven" with the reason.

5. **Re-run the checker** until it exits 0, and put its summary line in the PR description.

## For orchestrators

The rule lives in the project's `AGENTS.md`, which every lane and developer reads, and in CI, which
fails the PR. Add one line to build-lane work orders as well: "If your change alters a user path,
update the feature map in the same commit (`feature-map-update`): a new note file under
`features/notes/<key>/` when `features/notes/README.md` exists, otherwise the feature file." A
reviewer treats a touched feature with neither a map change (a note counts) nor a `map unchanged:`
line as an incomplete PR.
