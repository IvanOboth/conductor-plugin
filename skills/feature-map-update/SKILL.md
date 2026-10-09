---
name: feature-map-update
description: Keep a project's feature map true in the same pull request that changes the app. Runs the map checker against the branch's base, lists the feature files the diff touches and any new route no feature covers, updates those files from the changed code, and re-drives the changed recipe steps live. Use before opening or finishing any PR in a repo with a `.claude/skills/verify-*/features/` map, when the checker flags a touched feature, when a build lane changes a route, label, menu or permission, or for "update the feature map".
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
   It fails when your diff touched a feature's `sources` and you did not change its file, and when
   your branch added a route no feature covers. The repo's CI runs the same check on the PR.

2. **Decide per touched feature.** Read the feature file next to your diff. Ask one question: does
   a user reach, see or do anything differently? A new or renamed route, button, label, tab, menu
   item, dialog, empty state, a persona gaining or losing access, a new sub-feature, a removed one:
   update the file. A refactor, a backend fix with the same UI, a style change: leave it, pass
   `--allow-unchanged <feature-id>` locally, and put the line
   `map unchanged: <feature-id> — <reason>` in the PR description, which CI reads.

3. **Edit the file.** Targeted edits only. Keep the entry contract (front matter, H1, one
   paragraph, the four H2s). Add new route files to `sources`. A new route either joins an
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
update the feature file in the same commit (`feature-map-update`)." A reviewer treats a touched
feature with neither a map change nor a `map unchanged:` line as an incomplete PR.
