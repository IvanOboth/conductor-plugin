#!/usr/bin/env python3
"""Install the context-watch hook and conductor-handoff for a linked checkout (issue #17).

A plugin install gets the hook from hooks/hooks.json. A checkout linked with
link-personal-skills.py (or copied by install.sh) needs it in the user's
settings.json. This adds a PostToolUse ("*") and a Stop entry that run
scripts/context-watch.py from SCRIPT_DIR, and links bin/conductor-handoff into
~/.local/bin. Idempotent; settings.json is backed up before the first change.

  python3 scripts/install-context-hook.py [--settings FILE] [--script-dir DIR] [--bin-dir DIR] [--no-link] [--uninstall] [--dry-run]
"""
import argparse
import json
import os
import shlex
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = 'context-watch.py'
TAG = '# conductor-context-watch'  # ours; other tools' context-watch.py hooks are left alone


def settings_path():
    base = os.environ.get('CLAUDE_CONFIG_DIR') or str(Path.home() / '.claude')
    return Path(base) / 'settings.json'


def strip(hooks):
    """Remove our entries; drop groups left empty."""
    for event in ('PostToolUse', 'Stop'):
        groups = []
        for g in hooks.get(event, []):
            g = dict(g, hooks=[h for h in g.get('hooks', []) if TAG not in h.get('command', '')])
            if g['hooks']:
                groups.append(g)
        if groups:
            hooks[event] = groups
        else:
            hooks.pop(event, None)
    return hooks


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--settings', help='settings.json to edit (default: $CLAUDE_CONFIG_DIR or ~/.claude)')
    ap.add_argument('--script-dir', default=str(ROOT / 'scripts'))
    ap.add_argument('--bin-dir', default=str(Path.home() / '.local/bin'))
    ap.add_argument('--no-link', action='store_true', help='leave the bin dir alone (install.sh copies the command itself)')
    ap.add_argument('--uninstall', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args(argv)

    path = Path(a.settings).expanduser() if a.settings else settings_path()
    settings = json.loads(path.read_text()) if path.exists() else {}
    before = json.dumps(settings, sort_keys=True)
    hooks = strip(settings.get('hooks', {}))
    if not a.uninstall:
        # `|| true`: a missing script must never exit 2, which would block every Stop.
        cmd = f'python3 {shlex.quote(str(Path(a.script_dir).resolve() / SCRIPT))} || true {TAG}'
        entry = {'type': 'command', 'command': cmd, 'timeout': 10}
        hooks.setdefault('PostToolUse', []).append({'matcher': '*', 'hooks': [entry]})
        hooks.setdefault('Stop', []).append({'hooks': [dict(entry)]})
    settings['hooks'] = hooks
    changed = json.dumps(settings, sort_keys=True) != before

    link = Path(a.bin_dir) / 'conductor-handoff'
    target = ROOT / 'bin/conductor-handoff'
    if a.dry_run:
        print(json.dumps({'settings': str(path), 'changes_settings': changed,
                          'hooks': {k: hooks.get(k) for k in ('PostToolUse', 'Stop')},
                          'link': None if a.uninstall or a.no_link else f'{link} -> {target}'}, indent=1))
        return 0
    if changed:
        if path.exists():
            backup = path.with_name(f'settings.json.bak-context-hook-{time.strftime("%Y%m%d-%H%M%S")}')
            shutil.copy2(path, backup)
            print(f'backup   {backup}')
        tmp = path.with_name('.settings.json.context-hook.tmp')
        tmp.write_text(json.dumps(settings, indent=2) + '\n')
        os.chmod(tmp, path.stat().st_mode & 0o777 if path.exists() else 0o600)
        tmp.replace(path)
        print(f'{"removed" if a.uninstall else "hooked"}   {path}')
    else:
        print(f'unchanged {path}')
    if a.no_link:
        return 0
    if a.uninstall:
        if link.is_symlink() and link.resolve() == target.resolve():
            link.unlink()
            print(f'unlinked {link}')
    elif not (link.is_symlink() and link.resolve() == target.resolve()):
        if link.exists() or link.is_symlink():
            print(f'conductor-handoff: {link} exists and is not ours; left alone', file=sys.stderr)
            return 1
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(target)
        print(f'linked   {link} -> {target}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
