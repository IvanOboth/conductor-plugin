#!/usr/bin/env python3
"""
conductor-report — per-run agent telemetry ledger.

Parses the current (or named) Claude Code session transcript + its subagent
sidechains, plus any Codex CLI rollout files in the run's time window, computes
tokens per lane and API-equivalent USD, appends ONE JSONL line to the ledger,
and prints a markdown run report suitable for pasting into an issue/PR comment.

Usage (typical, as the closing step of a conductor run):
  python3 tools/conductor-report.py --run-id 2026-07-12-movit-pitch \
      --repo movit-demo --issue "movit#14" --outcome review \
      --since 2026-07-12T09:00:00Z

Run-start registration (the opening step — writes an in-flight entry so a
run dashboard, if you have one, can show the run as active while it executes):
  python3 tools/conductor-report.py --start --run-id 2026-07-12-movit-pitch \
      --repo movit-demo --issue "movit#14" --title "Movit pitch build"
The closing invocation above removes the entry automatically.

  --session PATH|ID   session transcript; default = newest .jsonl for this cwd's project
  --since ISO         run start (default: first timestamp in the session file)
  --until ISO         run end   (default: now)
  --ledger PATH       default ~/.claude/telemetry/conductor-runs.jsonl
  --dry-run           print only, don't append to the ledger

Data sources (verified 2026-07-11):
  ~/.claude/projects/<proj>/<session>.jsonl      per-message message.usage + model,
                                                 isSidechain flags subagent turns
  ~/.claude/projects/<proj>/<session>/subagents/agent-*.jsonl   per-subagent lanes
  ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl   cumulative token_count events
"""
import argparse
import glob
import json
import os
import sys
from datetime import datetime, timedelta, timezone

HOME = os.path.expanduser("~")
LEDGER_DEFAULT = os.path.join(HOME, ".claude", "telemetry", "conductor-runs.jsonl")
ACTIVE_RUNS = os.path.join(HOME, ".claude", "telemetry", "active-runs.json")


def load_active():
    try:
        with open(ACTIVE_RUNS, "r", encoding="utf-8") as fh:
            d = json.load(fh)
            return d if isinstance(d, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_active(d):
    os.makedirs(os.path.dirname(ACTIVE_RUNS), exist_ok=True)
    with open(ACTIVE_RUNS, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=1)

# USD per 1M tokens: (input, output, cache_read, cache_write). Jul 2026.
# cache_read ≈ 10% of input; cache_write ≈ 1.25x input (5m tier; 1h tier is 2x —
# we use 1.25x, so treat cache-write cost as a floor estimate).
PRICES = {
    "claude-opus-4-8":  (5.00, 25.00, 0.50, 6.25),
    "claude-opus-4":    (15.00, 75.00, 1.50, 18.75),
    "claude-sonnet-5":  (2.00, 10.00, 0.20, 2.50),
    "claude-sonnet-4":  (3.00, 15.00, 0.30, 3.75),
    "claude-haiku-4-5": (1.00, 5.00, 0.10, 1.25),
    "claude-fable-5":   (10.00, 50.00, 1.00, 12.50),
    "gpt-5.6-sol":      (5.00, 30.00, 0.50, 0.0),
    "gpt-5.6":          (5.00, 30.00, 0.50, 0.0),
    "gpt-5.5":          (5.00, 30.00, 0.50, 0.0),
}
DEFAULT_CLAUDE_PRICE = (5.00, 25.00, 0.50, 6.25)
DEFAULT_OPENAI_PRICE = (5.00, 30.00, 0.50, 0.0)


def price_for(model, family):
    m = (model or "").lower()
    for key, p in PRICES.items():
        if m.startswith(key):
            return p
    return DEFAULT_OPENAI_PRICE if family == "openai" else DEFAULT_CLAUDE_PRICE


def usd(tokens_in, tokens_out, cache_read, cache_write, price):
    pi, po, pcr, pcw = price
    return round(
        tokens_in / 1e6 * pi + tokens_out / 1e6 * po
        + cache_read / 1e6 * pcr + cache_write / 1e6 * pcw, 4)


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def project_dir_for_cwd():
    slug = "-" + os.getcwd().replace("/", "-").lstrip("-")
    d = os.path.join(HOME, ".claude", "projects", slug)
    return d if os.path.isdir(d) else None


def newest_session(proj_dir):
    files = sorted(glob.glob(os.path.join(proj_dir, "*.jsonl")),
                   key=os.path.getmtime, reverse=True)
    return files[0] if files else None


def sum_claude_file(path, since, until):
    """Sum message.usage in one transcript. Returns {model: {in,out,cr,cw}}, first_ts, last_ts."""
    lanes, first_ts, last_ts = {}, None, None
    try:
        fh = open(path, "r", encoding="utf-8", errors="replace")
    except OSError:
        return lanes, first_ts, last_ts
    with fh:
        for line in fh:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = parse_ts(d.get("timestamp"))
            if ts:
                first_ts = first_ts or ts
                last_ts = ts
                if (since and ts < since) or (until and ts > until):
                    continue
            msg = d.get("message") or {}
            u = msg.get("usage")
            if not u:
                continue
            model = msg.get("model") or "unknown"
            key = ("sidechain:" if d.get("isSidechain") else "") + model
            lane = lanes.setdefault(key, {"in": 0, "out": 0, "cr": 0, "cw": 0})
            lane["in"] += u.get("input_tokens", 0) or 0
            lane["out"] += u.get("output_tokens", 0) or 0
            lane["cr"] += u.get("cache_read_input_tokens", 0) or 0
            lane["cw"] += u.get("cache_creation_input_tokens", 0) or 0
    return lanes, first_ts, last_ts


def codex_lanes(since, until):
    """Find codex rollouts overlapping the window; last token_count event = cumulative totals."""
    out = []
    days, d = [], since.date()
    while d <= until.date():
        days.append(d)
        d += timedelta(days=1)
    for day in days:
        pat = os.path.join(HOME, ".codex", "sessions",
                           f"{day.year:04d}", f"{day.month:02d}", f"{day.day:02d}", "*.jsonl")
        for path in glob.glob(pat):
            mt = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
            if mt < since or datetime.fromtimestamp(os.path.getctime(path), tz=timezone.utc) > until:
                continue
            totals, model = None, None
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        if '"token_count"' not in line and '"model"' not in line:
                            continue
                        try:
                            d2 = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        payload = d2.get("payload") or {}
                        if payload.get("type") == "token_count":
                            info = payload.get("info") or {}
                            totals = info.get("total_token_usage") or totals
                        model = model or payload.get("model") or (d2.get("payload") or {}).get("model")
            except OSError:
                continue
            if totals:
                out.append({
                    "agent": os.path.basename(path).replace(".jsonl", "")[:40],
                    "family": "openai", "model": model or "gpt-5.6-sol",
                    "in": totals.get("input_tokens", 0),
                    "out": totals.get("output_tokens", 0) + totals.get("reasoning_output_tokens", 0),
                    "cr": totals.get("cached_input_tokens", 0), "cw": 0,
                })
    return out


def pane_ref():
    for var, kind in (("TMUX_PANE", "tmux"), ("WEZTERM_PANE", "wezterm"),
                      ("ITERM_SESSION_ID", "iterm2")):
        v = os.environ.get(var)
        if v:
            return f"{kind}:{v}"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--session")
    ap.add_argument("--repo", default="")
    ap.add_argument("--issue", default="")
    ap.add_argument("--skill", default="conductor")
    ap.add_argument("--outcome", default="review")
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--ledger", default=LEDGER_DEFAULT)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--start", action="store_true",
                    help="register the run as active (opening step) and exit")
    ap.add_argument("--title", default="", help="short human title for --start")
    a = ap.parse_args()

    if a.start:
        active = load_active()
        active[a.run_id] = {
            "run_id": a.run_id, "repo": a.repo, "issue": a.issue,
            "title": a.title,
            "started": datetime.now(timezone.utc).isoformat(),
            "pane": pane_ref(),
        }
        save_active(active)
        print(f"Registered active run {a.run_id} ({a.repo or 'no repo'}"
              f"{' · ' + a.issue if a.issue else ''}) → {ACTIVE_RUNS}")
        return

    sess = a.session
    if sess and not os.path.exists(sess):
        proj = project_dir_for_cwd()
        cand = proj and os.path.join(proj, sess + ".jsonl")
        sess = cand if cand and os.path.exists(cand) else None
    if not sess:
        proj = project_dir_for_cwd()
        sess = proj and newest_session(proj)
    if not sess:
        sys.exit("No session transcript found; pass --session PATH")

    until = parse_ts(a.until) or datetime.now(timezone.utc)
    since = parse_ts(a.since)
    main_lanes, first_ts, last_ts = sum_claude_file(sess, since, until)
    since = since or first_ts or (until - timedelta(hours=2))

    lanes = []
    for key, t in sorted(main_lanes.items()):
        side = key.startswith("sidechain:")
        model = key.split(":", 1)[1] if side else key
        lanes.append({"agent": "subagents(inline)" if side else "orchestrator",
                      "family": "claude", "model": model, **t})

    subdir = os.path.join(os.path.dirname(sess),
                          os.path.basename(sess).replace(".jsonl", ""), "subagents")
    for f in sorted(glob.glob(os.path.join(subdir, "agent-*.jsonl"))):
        sub, _, _ = sum_claude_file(f, since, until)
        for key, t in sub.items():
            model = key.split(":", 1)[1] if key.startswith("sidechain:") else key
            lanes.append({"agent": os.path.basename(f).replace(".jsonl", ""),
                          "family": "claude", "model": model, **t})

    lanes += codex_lanes(since, until)

    for lane in lanes:
        lane["usd_api_equiv"] = usd(lane["in"], lane["out"], lane["cr"], lane["cw"],
                                    price_for(lane["model"], lane["family"]))
    totals = {k: sum(l[k] for l in lanes) for k in ("in", "out", "cr", "cw")}
    totals["usd_api_equiv"] = round(sum(l["usd_api_equiv"] for l in lanes), 2)

    record = {
        "run_id": a.run_id, "skill": a.skill, "repo": a.repo, "issue": a.issue,
        "started": since.isoformat(), "ended": until.isoformat(),
        "duration_s": int((until - since).total_seconds()),
        "lanes": lanes, "totals": totals,
        "outcome": a.outcome, "pane": pane_ref(), "session": os.path.basename(sess),
    }

    if not a.dry_run:
        os.makedirs(os.path.dirname(a.ledger), exist_ok=True)
        with open(a.ledger, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
        active = load_active()
        if a.run_id in active:
            del active[a.run_id]
            save_active(active)

    mins = record["duration_s"] // 60
    print(f"## Run report — `{a.run_id}`")
    print(f"**Duration:** {mins} min · **Lanes:** {len(lanes)} · "
          f"**API-equivalent cost:** ${totals['usd_api_equiv']}")
    print()
    print("| lane | model | in | out | cache-read | ~$ |")
    print("|---|---|---:|---:|---:|---:|")
    for l in lanes:
        print(f"| {l['agent']} | {l['model']} | {l['in']:,} | {l['out']:,} "
              f"| {l['cr']:,} | {l['usd_api_equiv']} |")
    print(f"\n_Ledger: {'(dry-run, not written)' if a.dry_run else a.ledger}_")


if __name__ == "__main__":
    main()
