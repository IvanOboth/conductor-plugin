# Helper contract

The helper is `verify-<app>.sh` (or a small Node/Python CLI when the app needs more than shell).
Design it the way poteto recommends for an agent-facing CLI: composable subcommands, descriptive
errors that say what to do next, `--help`/no-argument usage, machine-readable output where an
agent will parse it, and no destructive side effect without saying so.

## State

```
RUN="${VERIFY_RUN_ID:-$(basename "$CHECKOUT")}"
RUN_DIR="${VERIFY_RUN_DIR:-$HOME/verify-<app>/$RUN}"
STATE="$RUN_DIR/state"        # url, pid (process session id), dev-server log, recording path
EVIDENCE="$RUN_DIR/evidence"  # survives stop
session() { echo "verify-<app>-$RUN"; }
ab() { agent-browser --session "$(session)" "$@"; }
```

Key everything on `$VERIFY_RUN_ID` so parallel runs in one checkout never share a browser or an
evidence directory.

## Commands

**target [url].** Record a deployed instance; default to the test track. Refuse the production
host by name. Run doctor.

**launch [port].** Refuse when env files or dependencies are missing and say how to get them.
Choose a free port from a dedicated range (`ss -ltnpH "sport = :$p"`; `lsof` misses some
listeners on the bench). Start the dev server with `setsid nohup … &` and store `$!`: it is the
process-session id that every child inherits, so doctor and stop can tell this run's processes
from everyone else's. Poll an HTTP readiness URL, fail fast on `EADDRINUSE`, run doctor.

**doctor.** Read-only. Print what it checked and end in `OK` or exit non-zero:
- the target answers the readiness URL with 200 and the page title is the app's;
- remote: the backend URL the deployment serves (for Convex apps, `/convex-url.txt`) is the
  expected test backend; the base branch head and its Vercel status (`gh api
  repos/<o>/<r>/commits/<base>/status`), since a pending build means the alias still serves the
  previous one;
- local: the listener's process session is the one launch stored; the checkout revision; the
  backend selector from the env file; other `convex dev` watchers pushing to the same deployment.

**sign-in [persona] [as].** Map short persona keys to test emails. Open the sign-in route, fill
the identifier by label, press Continue, branch on what Clerk shows (code screen, password screen
with "Use another method", Resend countdown), wait until the code field exists, enter `424242`,
wait to leave the sign-in route. For staff accounts with a persona chooser, click the named persona.
Print `whoami`. Each wait is a retried `wait --fn` on a DOM condition, never a fixed sleep alone.

**whoami.** One JSON line: path, organisation, page heading.

**open <path>.** Open the route, wait for a heading, and fail fast with the missing permission
when the page shows the app's access-denied state. That turns "I could not find it" into "this
persona cannot see it".

**shot <name>.** `get url`, `snapshot` (full accessibility tree), `screenshot`, all into
`evidence/<name>.*`.

**record start <name> / record stop.** `ab record start <evidence>/<name>.mp4` with no URL (0.37
keeps the page, DOM and login), reset the viewport, and on stop run `ffprobe -count_frames` and
print codec, frames and duration; fail on an empty file.

**features [query].** No argument: the index lines. With a query: matching feature files and
their titles (`grep -il`).

**stop.** `ab close`; if launch ran, `pkill -s <sid>`, wait, `pkill -9 -s <sid>`. Never
`pkill -f <pattern>`: on the bench that pattern can match the calling shell or another session's
lane. Remove `state/`, keep `evidence/`.

## Bench rules the helper must keep

- Builds, installs and type checks go through `~/bin/bench-heavy-run --`.
- One dev server per worktree; never drive an instance the run did not start or target.
- Never print secrets (bypass tokens, passwords) into commands, URLs, evidence or logs; read them
  from a 0600 file into a variable and send them as a header.
- Production is never a target.
