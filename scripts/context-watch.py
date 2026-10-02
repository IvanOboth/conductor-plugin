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
still hears it. It goes quiet once conductor-handoff records a handoff.

Never fails the session: any error exits 0 with no output.
CONDUCTOR_CONTEXT_WATCH=off disables it; =all watches every session.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

SKILL_RE = re.compile(
    rb'Base directory for this skill: [^"\\\s]*/(conductor(?:-claude|-core)?)(?=[/"\\\s])'
    rb'|"skill":\s*"(?:conductor:)?(conductor(?:-claude|-core)?)"'
)
TAIL_CHUNKS = (1 << 20, 8 << 20, 32 << 20)


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


def message(pct, tokens, window, now, stopping):
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
        return

    tokens, model = last_usage(transcript)
    if tokens:
        window = window_size(sid, model, tokens)
        pct = tokens * 100 // window
        if pct + 20 <= state.get('pct', 0):  # compacted: the levels count again
            state['told'], state['stop_blocked'] = [], []
        state.update(tokens=tokens, model=model, window=window, pct=pct, updated=int(time.time()))
    if not tokens or state.get('handoff'):
        save_state(sid, state)
        return

    threshold = int(os.environ.get('CONDUCTOR_HANDOFF_PCT', 70))
    now = int(os.environ.get('CONDUCTOR_HANDOFF_NOW_PCT', 85))
    crossed = [lv for lv in levels(threshold, now) if pct >= lv]
    if not crossed:
        save_state(sid, state)
        return
    level = crossed[-1]
    out = None
    if event == 'PostToolUse' and level not in state.get('told', []):
        state.setdefault('told', []).append(level)
        out = {'hookSpecificOutput': {'hookEventName': 'PostToolUse',
                                      'additionalContext': message(pct, tokens, window, now, False)}}
    elif event == 'Stop' and not data.get('stop_hook_active') and level not in state.get('stop_blocked', []):
        state.setdefault('stop_blocked', []).append(level)
        state.setdefault('told', []).append(level)
        out = {'decision': 'block', 'reason': message(pct, tokens, window, now, True)}
    save_state(sid, state)
    if out:
        print(json.dumps(out))


if __name__ == '__main__':
    try:
        main()
    except Exception:  # a watch must never break the session it watches
        pass
    sys.exit(0)
