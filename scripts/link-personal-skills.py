#!/usr/bin/env python3
"""Install shared skills: Claude/Antigravity symlinks and Codex discovery bootstrap."""
from datetime import datetime, timezone
from pathlib import Path
import errno
import os
import shutil
import tempfile


def _copy_entry(src, dst):
    if src.is_symlink():
        dst.symlink_to(os.readlink(src))
    elif src.is_dir():
        shutil.copytree(src, dst, symlinks=True)
    else:
        shutil.copy2(src, dst)


def _remove_entry(path):
    if path.is_symlink() or not path.is_dir():
        path.unlink()
    else:
        shutil.rmtree(path)


def _restore_entry(saved, target):
    try:
        os.rename(saved, target)
    except OSError as exc:
        if exc.errno != errno.EXDEV:
            raise
        _copy_entry(saved, target)


def main(skill="conductor"):
    source = (Path(__file__).resolve().parents[1] / 'skills' / skill).resolve()
    if not (source / 'SKILL.md').is_file():
        raise SystemExit(f'Missing canonical skill: {source}')
    home = Path.home()
    roots = [('claude', Path(os.environ.get('CLAUDE_CONFIG_DIR', home / '.claude'))),
             ('codex', Path(os.environ.get('CODEX_HOME', home / '.codex'))),
             ('gemini', Path(os.environ.get('GEMINI_CONFIG_DIR', home / '.gemini/config')))]
    if skill == 'conductor-claude':
        # A Claude-family-only profile has no meaning from a Codex or Antigravity parent.
        roots = [r for r in roots if r[0] == 'claude']
    targets = [(name, root / 'skills' / skill) for name, root in roots]
    # Preflight every target before modifying any of them.
    seen_destinations = {}
    for name, target in targets:
        resolved_dest = target.parent.resolve() / target.name
        if resolved_dest in seen_destinations:
            raise SystemExit(
                f'Refusing aliased skill destination: {seen_destinations[resolved_dest]} and {name} both resolve to {resolved_dest}'
            )
        seen_destinations[resolved_dest] = name
    pending = []
    try:
        source_ref = '~/' + str((source / 'SKILL.md').relative_to(home))
    except ValueError:
        source_ref = str(source / 'SKILL.md')
    bootstrap = ('---\nname: conductor\ndescription: Mixed-model orchestration with readable explanatory HTML reports and evidence for tested application changes. Use for conductor, orchestrate this, mixed-model build, or independent review.\n---\n\n# Conductor\n\nRead `' + source_ref + '` now and follow that skill. This file is only a discovery entry point; all orchestration, report design, explanation and evidence policy lives in the referenced plugin source. Reread that source before each report revision.\n')
    titles = {'conductor-gemini': 'Conductor Gemini', 'conductor-core': 'Conductor Core', 'conductor-claude': 'Conductor Claude',
              'mobile-app-testing': 'Mobile app testing', 'verify-skill-create': 'Create a verification skill',
              'verify-skill-maintain': 'Maintain a verification skill', 'feature-map-update': 'Update the feature map',
              'verify-skill-eval': 'Evaluate a guidance change', 'how': 'How',
              'journey-review': 'Review a user journey'}
    if skill in titles:
        description = (source / 'SKILL.md').read_text().split('\ndescription: ', 1)[1].split('\n', 1)[0]
        title = titles[skill]
        bootstrap = ('---\nname: ' + skill + '\ndescription: ' + description +
                     '\n---\n\n# ' + title + '\n\nRead `' + source_ref +
                     '` now and follow that skill. Resolve its references from the canonical source directory. This entry point shares the same instructions with Claude.\n')
    for name, target in targets:
        if name == 'codex' and not target.is_symlink() and (target / 'SKILL.md').is_file() and (target / 'SKILL.md').read_text() == bootstrap:
            print(f'Already current: {target} (Codex discovery entry)')
        elif name in ('claude', 'gemini') and target.is_symlink() and target.resolve() == source:
            print(f'Already linked: {target} -> {source}')
        else:
            if target.exists() and not target.is_dir() and not target.is_symlink():
                raise SystemExit(f'Refusing non-directory skill entry: {target}')
            pending.append((name, target))
    if not pending:
        return
    for _, target in pending:
        target.parent.mkdir(parents=True, exist_ok=True)
    state = home / '.local/state/conductor-link'
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    state.chmod(0o700)
    backup = Path(tempfile.mkdtemp(prefix=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S-'), dir=state))
    changed = []
    try:
        # Phase 1: Stage existing entries atomically on the same filesystem, then install new entries.
        for idx, (name, target) in enumerate(pending):
            saved = backup / name
            staged = None
            if target.exists() or target.is_symlink():
                staged = target.parent / f'.{target.name}.conductor-link-tmp-{os.getpid()}-{idx}-{backup.name}'
                target.rename(staged)
            changed.append([target, staged, saved, 'staged' if staged is not None else 'none'])
            if name == 'codex':
                target.mkdir()
                (target / 'SKILL.md').write_text(bootstrap)
                if (source / 'agents').is_dir():
                    (target / 'agents').symlink_to(source / 'agents', target_is_directory=True)
                print(f'Installed Codex discovery entry: {target} -> {source}')
            else:
                target.symlink_to(source, target_is_directory=True)
                if not (target / 'SKILL.md').samefile(source / 'SKILL.md'):
                    raise RuntimeError(f'Link verification failed: {target}')
                print(f'Linked: {target} -> {source}')
        # Phase 2: Archive staged originals into backup (same-FS rename, or cross-FS copy preserving symlinks).
        cross_fs_staged = []
        for entry in changed:
            target, staged, saved, status = entry
            if staged is None:
                continue
            try:
                os.rename(staged, saved)
                entry[3] = 'moved'
            except OSError as exc:
                if exc.errno != errno.EXDEV:
                    raise
                _copy_entry(staged, saved)
                cross_fs_staged.append(entry)
        # Phase 3: Remove cross-FS staged copies only after every backup copy is complete.
        for entry in cross_fs_staged:
            staged = entry[1]
            entry[3] = 'deleting_staged'
            _remove_entry(staged)
            entry[3] = 'moved'
    except BaseException:
        for target, staged, saved, status in reversed(changed):
            if target.is_symlink():
                target.unlink()
            elif target.is_dir():
                # Only our newly created Codex entry exists here.
                for child in target.iterdir():
                    child.unlink()
                target.rmdir()
            if status == 'staged' and staged is not None and (staged.exists() or staged.is_symlink()):
                staged.rename(target)
            elif status in ('moved', 'deleting_staged') and (saved.exists() or saved.is_symlink()):
                _restore_entry(saved, target)
        raise
    print(f'Previous installs preserved: {backup}')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    SKILLS = ['conductor', 'conductor-gemini', 'conductor-core', 'conductor-claude', 'mobile-app-testing', 'verify-skill-create',
              'verify-skill-maintain', 'feature-map-update', 'verify-skill-eval', 'how', 'journey-review']
    parser.add_argument('--skill', choices=SKILLS)
    args = parser.parse_args()
    for skill in ([args.skill] if args.skill else SKILLS):
        main(skill)
