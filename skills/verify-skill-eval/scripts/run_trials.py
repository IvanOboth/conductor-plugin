#!/usr/bin/env python3
"""Run paired agent trials (with and without a change to the agent's guidance) and tabulate them.

    run_trials.py run   <plan.json>      run every (task, arm, rep) not yet finished, then summarise
    run_trials.py table <plan.json>      summarise the finished trials only

plan.json:
    {
      "out": "/home/ivan/runs/<run>/trials",
      "model": "opus", "effort": "medium",
      "reps": 2, "concurrency": 4, "timeout_s": 2400,
      "arms":  {"a": {"cwd": "/path/checkout-a"}, "b": {"cwd": "/path/checkout-b"}},
      "tasks": [{"id": "t1", "prompt": "…what a user would type…"}],
      "probe": ["verify-mikono", "features/"],    # strings to look for in tool inputs: did the agent use the guidance?
      "deny": ["Bash(npx convex:*)", "Bash(git push:*)"]   # permission rules every trial runs under
    }

Each trial is `claude -p <prompt>` in the arm's checkout with stream-json output, stdin closed, its
own process group (killed on timeout), and VERIFY_RUN_ID set to a neutral label so parallel trials
never share a browser session. Results: <out>/<label>.jsonl (the stream), <out>/<label>.meta.json,
<out>/results.json and <out>/summary.md.
"""

from __future__ import annotations

import concurrent.futures as cf
import hashlib
import json
import os
import signal
import statistics
import subprocess
import sys
import time
from pathlib import Path


def label_for(task: str, arm: str, rep: int) -> str:
    """A neutral label: nothing in it tells the trial (or a judge) which arm it belongs to."""
    return "r" + hashlib.sha1(f"{task}|{arm}|{rep}".encode()).hexdigest()[:8]


def trials(plan: dict) -> list[dict]:
    return [
        {"task": t["id"], "prompt": t["prompt"], "arm": arm, "rep": rep, "label": label_for(t["id"], arm, rep)}
        for t in plan["tasks"] for rep in range(1, plan.get("reps", 1) + 1) for arm in sorted(plan["arms"])
    ]


def identity(plan: dict, trial: dict) -> dict:
    """What makes two runs of a label the same experiment: prompt, model, effort, checkout revision."""
    cwd = plan["arms"][trial["arm"]]["cwd"]
    rev = subprocess.run(["git", "-C", cwd, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    return {"prompt_sha": hashlib.sha1(trial["prompt"].encode()).hexdigest()[:12], "model": plan.get("model", "opus"),
            "effort": plan.get("effort", "medium"), "rev": rev, "deny": plan.get("deny", [])}


def has_result(stream: Path) -> bool:
    return stream.exists() and any('"type":"result"' in line.replace(" ", "") for line in stream.open(errors="replace"))


def run_one(plan: dict, trial: dict) -> dict:
    out = Path(plan["out"])
    stream = out / f"{trial['label']}.jsonl"
    meta_path = out / f"{trial['label']}.meta.json"
    ident = identity(plan, trial)
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        # Reuse only a finished trial of the same experiment; re-run timeouts, crashes and changed setups.
        if has_result(stream) and not meta.get("timed_out") and meta.get("identity", ident) == ident:
            return meta
    arm = plan["arms"][trial["arm"]]
    env = {**os.environ, "VERIFY_RUN_ID": trial["label"], **arm.get("env", {})}
    settings = out / "trial-settings.json"
    settings.write_text(json.dumps({"permissions": {"deny": plan.get("deny", [])}}))
    cmd = ["claude", "-p", trial["prompt"], "--settings", str(settings), "--model", plan.get("model", "opus"),
           "--effort", plan.get("effort", "medium"), "--output-format", "stream-json", "--verbose",
           "--dangerously-skip-permissions", "--no-session-persistence"]
    started = time.time()
    with stream.open("w") as fh, (out / f"{trial['label']}.err").open("w") as err:
        proc = subprocess.Popen(cmd, cwd=arm["cwd"], env=env, stdin=subprocess.DEVNULL, stdout=fh,
                                stderr=err, start_new_session=True)
        try:
            proc.wait(timeout=plan.get("timeout_s", 2400))
        except subprocess.TimeoutExpired:
            timed_out = True
        else:
            timed_out = False
        # Kill the whole process group either way: children (browsers, shells) can outlive the parent.
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try:
                os.killpg(proc.pid, sig)
            except ProcessLookupError:
                break
            time.sleep(5)
        code = proc.wait()
    meta = {**trial, "exit": code, "timed_out": timed_out, "wall_s": round(time.time() - started, 1), "identity": ident}
    meta_path.write_text(json.dumps(meta, indent=1))
    return meta


def parse(plan: dict, meta: dict) -> dict:
    stream = Path(plan["out"]) / f"{meta['label']}.jsonl"
    tools: dict[str, int] = {}
    probe_hits = {p: 0 for p in plan.get("probe", [])}
    result: dict = {}
    for line in stream.read_text(errors="replace").splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant":
            for block in ev.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    tools[block["name"]] = tools.get(block["name"], 0) + 1
                    blob = json.dumps(block.get("input", {}))
                    for p in probe_hits:
                        probe_hits[p] += blob.count(p)
        elif ev.get("type") == "result":
            result = ev
    usage = result.get("usage", {})
    return {
        **meta,
        "finished": bool(result) and not meta["timed_out"],
        "is_error": result.get("is_error"),
        "duration_s": round(result.get("duration_ms", 0) / 1000, 1) if result else meta["wall_s"],
        "turns": result.get("num_turns"),
        "cost_usd": result.get("total_cost_usd"),
        "output_tokens": usage.get("output_tokens"),
        "input_tokens": (usage.get("input_tokens") or 0) + (usage.get("cache_read_input_tokens") or 0)
        + (usage.get("cache_creation_input_tokens") or 0),
        "tool_calls": sum(tools.values()),
        "tools": tools,
        "probe_hits": probe_hits,
        "final_message": (result.get("result") or "")[-4000:],
    }


def summarise(plan: dict) -> None:
    out = Path(plan["out"])
    rows = [parse(plan, json.loads(p.read_text())) for p in sorted(out.glob("*.meta.json"))]
    (out / "results.json").write_text(json.dumps(rows, indent=1))
    lines = ["| task | arm | rep | label | finished | time s | turns | tool calls | cost $ | guidance hits |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["task"], r["arm"], r["rep"])):
        lines.append(f"| {r['task']} | {r['arm']} | {r['rep']} | {r['label']} | {r['finished']} | {r['duration_s']} | "
                     f"{r['turns']} | {r['tool_calls']} | {r['cost_usd'] if r['cost_usd'] is not None else ''} | "
                     f"{sum(r['probe_hits'].values())} |")
    lines += ["", "| arm | trials | finished | median time s | median turns | median tool calls | total cost $ |",
              "|---|---|---|---|---|---|---|"]
    for arm in sorted(plan["arms"]):
        rs = [r for r in rows if r["arm"] == arm]
        if not rs:
            continue
        med = lambda k: statistics.median([r[k] for r in rs if r[k] is not None] or [0])
        cost = sum(r["cost_usd"] or 0 for r in rs)
        lines.append(f"| {arm} | {len(rs)} | {sum(r['finished'] for r in rs)} | {med('duration_s')} | "
                     f"{med('turns')} | {med('tool_calls')} | {cost:.2f} |")
    lines += ["", "Success is judged from the evidence, not from these numbers: read each final message and",
              "its screenshots against the task's acceptance check, blind to the arm (labels are neutral)."]
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    # The judging sheet: neutral labels in label order, the task and the deliverable only. No arm, no
    # guidance hits, no tool counts. Judge from this file before opening summary.md.
    judge = ["# Judging sheet", "", "Score each trial pass / partial / fail against its task's acceptance check.", ""]
    for r in sorted(rows, key=lambda r: r["label"]):
        judge += [f"## {r['label']} · task {r['task']}", "", f"Finished: {r['finished']}", "", "```text",
                  r["final_message"].strip() or "(no final message)", "```", ""]
    (out / "judge.md").write_text("\n".join(judge))
    print("\n".join(lines))


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in {"run", "table"}:
        print(__doc__)
        return 2
    plan = json.loads(Path(sys.argv[2]).read_text())
    Path(plan["out"]).mkdir(parents=True, exist_ok=True)
    if sys.argv[1] == "run":
        todo = trials(plan)
        with cf.ThreadPoolExecutor(max_workers=plan.get("concurrency", 4)) as pool:
            for meta in pool.map(lambda t: run_one(plan, t), todo):
                print(f"{meta['label']} task={meta['task']} exit={meta['exit']} timed_out={meta['timed_out']} "
                      f"wall={meta['wall_s']}s", flush=True)
    summarise(plan)
    return 0


if __name__ == "__main__":
    sys.exit(main())
