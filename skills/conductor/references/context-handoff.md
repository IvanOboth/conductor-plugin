# Context handoff (handoff mode only)

Cold reference for [Conductor](../SKILL.md), **Long-horizon runs**. By default a long run compacts in place and does not hand over; read this only when the run sets `CONDUCTOR_CONTEXT_MODE=handoff`, or must move to another machine or another model.

## Hook levels (both modes)

The `context-watch` hook warns once per level at 70% (`CONDUCTOR_CHECKPOINT_PCT`, older name `CONDUCTOR_HANDOFF_PCT`), again at 85% (`CONDUCTOR_CHECKPOINT_NOW_PCT` or `CONDUCTOR_HANDOFF_NOW_PCT`) and every 5 points after. The bench sets 40% and 45%, below the point where Claude Code compacts a 1M session there (`autoCompactWindow: 500000`, about 47%); keep the levels below that point wherever you change it. In compact-in-place mode (the default) the hook never blocks a stop, and a confirmed compaction re-arms the levels; its SessionStart entry (source `compact`) tells the session it was compacted, and without that entry the first tool call after the context drops by 20 points carries the same message.

## Handoff mode

In handoff mode the hook works as before: it tells you at each level and blocks one stop per level, except while background lanes launched by this session have not reported back (a lane silent for 12 hours, `CONDUCTOR_LANE_MAX_HOURS`, stops counting). Then:

1. **Checkpoint.** Finish or stop the step in flight and start no new wave. Let background `Agent`/`Workflow` lanes land, or stop them and list them as open; Codex lanes can keep running. Commit what landed, update the work-list, and update the run's status comment to say a successor is taking over. This is the old session's last issue edit.
2. **Write the continuation order** at `.conductor/work-orders/<run>-continue.md`. It tells the successor to load this skill and read the original order, the work-list and any shared contract, then gives the state at hand-over (each item with its PR or branch, head SHA and next action; anything running and where its report lands), the decisions already taken, where status is reported, the resources this run owns, the process rules learned in this run, and what is owed at the end. It ends with the unattended-lane paragraph. The successor knows only what the order says and what is on disk.
3. **Run `conductor-handoff --order <path>`.** It opens an Orca terminal (or a T3 thread inside T3 Code) for the same worktree with this session's model, effort `high` and `--dangerously-skip-permissions`, sends `/<skill> Read <order> …`, records the hand-over in `.conductor/handoffs.jsonl` and silences the watch. Without Orca it exits 3 and prints the command for Ivan to run. It refuses a fourth hand-over in two hours. The successor's tab must land in a worktree Orca lists, so Ivan can see it: for an unlisted worktree it opens in `--terminal-worktree <dir>` or this session's worktree, and refuses with exit 6 when none is listed (`--allow-unlisted` overrides). Create worktrees with `git -C ~/dev/<repo> fetch origin <base> && orca worktree create --name <name> --base-branch origin/<base> --setup skip`, never `git worktree add`.
4. **Stand down.** From the old session: no merges, pushes, deploys, issue or comment edits, or dispatches. Answer the successor's questions, forward any late lane result with `orca terminal send --terminal <new terminal> --text "…" --enter`, and tell Ivan in two lines where the successor is. On the bench the idle reaper closes the old tab after 1 hour idle.

The successor is a new conductor run on the same work-list: it re-scouts what changed, then dispatches only what remains.
