#!/usr/bin/env python3
"""context-watch — tell a long conductor run when to hand off to a fresh session.

Registered as a Claude Code hook on PostToolUse and Stop (issue #17). Hooks get
no token counts, so the hook reads the session's current context size from the
last main-chain assistant `usage` in the transcript, and the window size from
the statusline's cache (scripts/context-statusline-tap.sh) or a model default.

In a conductor session (the conductor, conductor-claude or conductor-core skill
was loaded, or the working directory holds .conductor/work-list.md) it injects
the handoff instruction when usage crosses CONDUCTOR_HANDOFF_PCT (default 70),
again at CONDUCTOR_HANDOFF_NOW_PCT (default 85) and every 5 points after. The
Stop hook blocks one stop per level, so an idle session over the threshold
still hears it. It goes quiet once conductor-handoff writes <session>.handoff.json.

A session waiting on its own background lanes (Agent, Workflow or Bash run in the background, launched in the
last CONDUCTOR_LANE_MAX_HOURS, default 12, with no task-notification yet) is not stopped: those lanes report
to this session, so the Stop block waits for the first stop after they have all landed.

Never fails the session: any error exits 0 with no output.
CONDUCTOR_CONTEXT_WATCH=off disables it; =all watches every session.
"""
import calendar
import fcntl
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

SKILL_RE = re.compile(
    rb'Base directory for this skill: [^"\\]*/(conductor(?:-claude|-core)?)(?=["\\])'
    rb'|"skill":\s*"(?:conductor:)?(conductor(?:-claude|-core)?)"'
)
TAIL_CHUNKS = (1 << 20, 8 << 20, 32 << 20)
NOTE_RE = re.compile(rb'<task-id>([\w.-]+)</task-id>(?:(?!<task-id>).){0,4000}?<status>(\w+)</status>', re.S)
DONE_STATUSES = {'completed', 'failed', 'killed', 'stopped', 'cancelled', 'canceled', 'error', 'errored',
                 'timeout', 'timed_out'}
HEAD_BYTES = 4096


def state_dir():
    base = os.environ.get('XDG_STATE_HOME') or str(Path.home() / '.local/state')
    return Path(base) / 'conductor/context'


def load_state(sid):
    try:
        return json.loads((state_dir() / f'{sid}.json').read_text())
    except (OSError, ValueError):
        return {}


def save_state(sid, state):
    d = state_dir()
    d.mkdir(parents=True, exist_ok=True)
    tmp = d / f'.{sid}.json.tmp'
    tmp.write_text(json.dumps(state, indent=1))
    tmp.replace(d / f'{sid}.json')


def scan_for_skill(transcript, state):
    """Look for a conductor skill load in the bytes added since the last scan."""
    try:
        size = transcript.stat().st_size
    except OSError:
        return None
    offset = state.get('scanned_offset', 0)
    if size < offset:  # transcript replaced; start again
        offset = 0
    with transcript.open('rb') as fh:
        fh.seek(max(0, offset - 200))  # overlap so a marker split across scans is found
        data = fh.read()
    state['scanned_offset'] = size
    found = None
    for m in SKILL_RE.finditer(data):
        found = (m.group(1) or m.group(2)).decode()
    return found


def launched_id(raw):
    """The background task id a tool result started, or None."""
    try:
        d = json.loads(raw)
    except ValueError:
        return None, None
    r = d.get('toolUseResult')
    if not isinstance(r, dict) or d.get('isSidechain'):
        return None, None
    tid = None
    if r.get('status') == 'async_launched':
        tid = r.get('agentId') or r.get('taskId')
    elif r.get('backgroundTaskId'):
        tid = r.get('backgroundTaskId')
    return (str(tid) if tid else None), d.get('timestamp')


def parse_ts(value):
    try:  # transcript timestamps are UTC
        return calendar.timegm(time.strptime(value[:19], '%Y-%m-%dT%H:%M:%S'))
    except (TypeError, ValueError):
        return time.time()


def notification_text(raw):
    """The text of a main-chain user message (string or text blocks), or '' — never tool inputs or results."""
    try:
        d = json.loads(raw)
    except ValueError:
        return ''
    if d.get('type') != 'user' or d.get('isSidechain'):
        return ''
    c = (d.get('message') or {}).get('content')
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return '\n'.join(b.get('text') or '' for b in c if isinstance(b, dict) and b.get('type') == 'text')
    return ''


def head_hash(transcript):
    try:
        with transcript.open('rb') as fh:
            return hashlib.sha1(fh.read(HEAD_BYTES)).hexdigest()
    except OSError:
        return None


def track_lanes(transcript, state):
    """Update state['lanes'] {id: launched epoch} from the lines added since the last read; return the live ids."""
    lanes = state.setdefault('lanes', {})
    try:
        size = transcript.stat().st_size
    except OSError:
        return []
    offset = state.get('lanes_offset', 0)
    head = head_hash(transcript)
    if size < offset or (offset >= HEAD_BYTES and head != state.get('lanes_head')):
        offset = 0  # transcript replaced: read it again from the start, keeping lanes already known
    if size > offset:
        with transcript.open('rb') as fh:
            fh.seek(offset)
            data = fh.read(size - offset)
        end = data.rfind(b'\n') + 1  # whole lines only; a partial last line is read next time
        for raw in data[:end].split(b'\n'):
            if b'"toolUseResult"' in raw and (b'async_launched' in raw or b'backgroundTaskId' in raw):
                tid, ts = launched_id(raw)
                if tid:
                    lanes[tid] = parse_ts(ts)
            if b'<task-notification>' in raw:
                for m in NOTE_RE.finditer(notification_text(raw).encode()):
                    if m.group(2).decode().lower() in DONE_STATUSES:
                        lanes.pop(m.group(1).decode(), None)
        state['lanes_offset'] = offset + end
    state['lanes_head'] = head
    try:
        max_age = float(os.environ.get('CONDUCTOR_LANE_MAX_HOURS', 12)) * 3600
    except ValueError:
        max_age = 12 * 3600
    cutoff = time.time() - max_age
    for tid in [t for t, at in lanes.items() if at < cutoff]:
        del lanes[tid]  # a lane that never reported (session restarted, lane lost) stops counting
    return sorted(lanes)


def last_usage(transcript):
    """(tokens, model) from the last main-chain assistant message with usage."""
    try:
        size = transcript.stat().st_size
    except OSError:
        return None, None
    with transcript.open('rb') as fh:
        for chunk in TAIL_CHUNKS:
            start = max(0, size - chunk)
            fh.seek(start)
            lines = fh.read().split(b'\n')
            if start:
                lines = lines[1:]  # first line is partial
            for raw in reversed(lines):
                if b'"usage"' not in raw or b'"assistant"' not in raw:
                    continue
                try:
                    d = json.loads(raw)
                except ValueError:
                    continue
                if d.get('type') != 'assistant' or d.get('isSidechain'):
                    continue
                msg = d.get('message') or {}
                u = msg.get('usage') or {}
                tokens = sum(int(u.get(k) or 0) for k in (
                    'input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens'))
                if tokens:
                    return tokens, msg.get('model')
            if not start:
                break
    return None, None


def window_size(sid, model, tokens):
    env = os.environ.get('CONDUCTOR_CONTEXT_WINDOW')
    if env and env.isdigit():
        return int(env)
    try:  # written by the statusline, which is told the real window size
        cached = int((state_dir() / f'{sid}.window').read_text().strip())
        if cached > 0:
            return cached
    except (OSError, ValueError):
        pass
    m = (model or '').lower()
    size = 1_000_000 if ('[1m]' in m or re.search(r'claude-(opus|fable)-5', m)) else 200_000
    return 1_000_000 if tokens > size else size


def levels(threshold, now):
    out = [threshold] + [p for p in range(now, 100, 5) if p > threshold]
    return sorted(set(out))


def message(pct, tokens, window, now, stopping, lanes=0):
    left = max(0, window - tokens)
    head = (f'Context watch (conductor): this session is at {pct}% of its context window '
            f'({tokens:,} of {window:,} tokens; about {left:,} left).')
    if pct >= now:
        body = ('Hand off now unless the run finishes in the next step or two. Do not dispatch new lanes. '
                'Checkpoint (commit landed work, update the work-list), write the continuation order '
                '(conductor skill, "Context handoff"), run `conductor-handoff --order <path>`, then stand down.')
    else:
        body = ('If work on this run remains beyond the step in flight, plan the handoff instead of running '
                'into compaction: finish or checkpoint the step in flight, start no new wave, write the '
                'continuation order (conductor skill, "Context handoff"), run `conductor-handoff --order <path>`, '
                'then stand down. If the run will finish within the remaining context, carry on.')
    if lanes:
        body += (f' {lanes} background lane(s) still report to this session: let them land before you hand off, '
                 'and dispatch nothing new.')
    if stopping:
        body += (' You are ending your turn: if work remains and nothing is waiting on Ivan, hand off now. '
                 'If the run is complete, or you are waiting on Ivan or on lanes that report to this session, '
                 'say so in one line and stop.')
    return f'{head} {body}'


def main():
    mode = os.environ.get('CONDUCTOR_CONTEXT_WATCH', 'conductor').lower()
    if mode in ('off', '0', 'false'):
        return
    data = json.loads(sys.stdin.read() or '{}')
    event = data.get('hook_event_name')
    if event not in ('PostToolUse', 'Stop') or data.get('agent_id'):
        return  # subagent tool calls carry agent_id; the handoff is the orchestrator's
    sid = data.get('session_id')
    transcript = Path(data.get('transcript_path') or '')
    if not sid or not transcript.is_file():
        return

    d = state_dir()
    d.mkdir(parents=True, exist_ok=True)
    with (d / f'{sid}.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)  # concurrent hooks for one session update state in turn
        out = watch(data, event, sid, transcript, mode)
    if out:
        print(json.dumps(out))


def handed_off(sid):
    try:  # written only by conductor-handoff, never by this hook
        return json.loads((state_dir() / f'{sid}.handoff.json').read_text()).get('status') == 'done'
    except (OSError, ValueError):
        return False


def watch(data, event, sid, transcript, mode):
    state = load_state(sid)
    if not state.get('skill'):
        found = scan_for_skill(transcript, state)
        cwd = Path(data.get('cwd') or '.')
        if found:
            state['skill'] = found
        elif (cwd / '.conductor/work-list.md').is_file():
            state['skill'] = 'conductor'
    state['permission_mode'] = data.get('permission_mode') or state.get('permission_mode')
    state['cwd'] = data.get('cwd') or state.get('cwd')
    watched = bool(state.get('skill')) or mode == 'all'
    if not watched:
        save_state(sid, state)
        return None

    live = track_lanes(transcript, state)
    tokens, model = last_usage(transcript)
    if tokens:
        window = window_size(sid, model, tokens)
        pct = tokens * 100 // window
        if pct + 20 <= state.get('pct', 0):  # compacted: the levels count again
            state['told'], state['stop_blocked'] = [], []
        state.update(tokens=tokens, model=model, window=window, pct=pct, updated=int(time.time()))
    if not tokens or handed_off(sid):
        save_state(sid, state)
        return None

    threshold = int(os.environ.get('CONDUCTOR_HANDOFF_PCT', 70))
    now = int(os.environ.get('CONDUCTOR_HANDOFF_NOW_PCT', 85))
    crossed = [lv for lv in levels(threshold, now) if pct >= lv]
    if not crossed:
        save_state(sid, state)
        return None
    level = crossed[-1]
    out = None
    if event == 'PostToolUse' and level not in state.get('told', []):
        state.setdefault('told', []).append(level)
        out = {'hookSpecificOutput': {'hookEventName': 'PostToolUse',
                                      'additionalContext': message(pct, tokens, window, now, False, len(live))}}
    elif event == 'Stop' and live:
        pass  # waiting on lanes that report here: the block comes at the first stop after they land
    elif event == 'Stop' and not data.get('stop_hook_active') and level not in state.get('stop_blocked', []):
        state.setdefault('stop_blocked', []).append(level)
        state.setdefault('told', []).append(level)
        out = {'decision': 'block', 'reason': message(pct, tokens, window, now, True)}
    save_state(sid, state)
    return out


if __name__ == '__main__':
    try:
        main()
    except Exception:  # a watch must never break the session it watches
        pass
    sys.exit(0)
