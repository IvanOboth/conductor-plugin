# Execution slices on a CI box or boat (Bench only)

Cold reference for [Conductor](../SKILL.md). Read it only on Ivan's Bench, when an execution slice may run off the bench. Other hosts have no such tool and ignore this file.

Added 15 Nov 2026 (bench-factory#651). On Ivan's Bench, an orchestrator can send one execution slice to a CI box or a boat sandbox instead of running it as an in-process lane: `conductor-box-lane run --order <file> --branch <epic-N-slug> --epic <N>` places it through `bench-agent-run`, waits for it and collects its lane report and pushed branch. On 14 Nov 2026 epic and Conductor runs were 64% of the Claude use recorded on the bench, and the bench reached a load of 55 to 69 on 16 cores while the boxes and boat had room. The orchestrator keeps the plan, the work orders, the reviews, the pull requests, the merges and every key on the bench. Other hosts have no such tool and ignore this section.

**A slice goes out only when all of these hold:**
- It is an execution slice (implementation, refactor, tests, a mechanical sweep) that one Opus 5.5 lane can finish and push on one branch.
- It is independent: no other running lane writes its files, and it builds on the default branch as it is on GitHub. A slice that needs unmerged work waits until that work is merged, or continues a pushed branch with `--continue`.
- Its order stands alone. The lane gets a clean checkout and the order text only: no `.conductor/` files, no lane presets, no bench paths outside the repository, no development backend unless `bench-agent-run` sends that repository's env files, no signed-in browser, no device, no production key, no vault, and no `gh` call other than `gh issue view` (`bench-agent-run` keeps such an order off boat, so it could only wait for a CI box).
- It needs no judgment the orchestrator must watch, and no GPT-6.2 Sol or Gemini 4 Neon: neither Codex nor agy runs there.

**A slice stays on the bench** when it fails any of these: design and taste lanes, reviews (`codex-review`, `verify-lane`), runtime and device verification, anything that needs a dev server, a browser session, a phone, a production or client key, or the vault.

**How:**
1. Run `conductor-box-lane list` first in a new or resumed session. A lane that is still `out` belongs to this run: `wait`, `collect` or `stop` it; never start a second lane for its branch (`start` refuses it).
2. Write the order as for an `exec-lane`, ending with the unattended-lane paragraph, and run `conductor-box-lane run ... ` with `run_in_background: true`. The harness wakes the session when it ends; do not poll.
3. Read the exit code and the printed line. **One rule before any in-process fallback: run `conductor-box-lane list`, and no row for that branch may still be `out`.** A row still out is waited for (`wait <id>`), collected (`collect <id>`) or stopped (`stop <id>`, confirmed when `list` no longer shows it out) first; otherwise two writers build one branch.
   - Exit 0 and the last line printed (the collect line) starts with `done`: the branch is on GitHub at the printed head and the report is at the printed path. Read the diff and send it to review as any lane's work. Exit 0 with `blocked` (or no status): read the report; finish the slice in-process.
   - Exit 75 (no room, the switch is off, or the cap is full) or 3 (the lane needs the bench): run the slice in-process as an `exec-lane`.
   - Exit 2 that names a lane: a lane for this branch is still out; deal with it as above. Exit 2 otherwise: the order was refused; run the slice in-process.
   - Exit 1, 4 (the lane passed its `--timeout`, 3 hours by default) or 5 (a usage limit; `wait <id>` asks again for an account): apply the rule above, then finish the slice in-process. On a CI box what the lane pushed is on the branch; on boat nothing is pushed unless it exited 0.
4. Its review, pull request, merge and verification follow the same gates as every other lane.

The way back is the switch file `~/.config/conductor-box-lane/switch`; without it every slice runs in-process. The commands, exit codes and ledger are in bench-factory `domains/career-craft/bench/ci-runner/README.md`, "Conductor slices on a box".
