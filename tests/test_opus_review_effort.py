"""Opus reviews run at high (Ivan, 12 Nov 2026: "opus reviews at xhigh are unnecessary, high is good enough").

No skill, agent, team-config copy or README may prescribe the Opus 5.5 verify-lane, or any Opus review lane, at
xhigh. Dated notes about 31 Oct to 12 Nov 2026 are history.

GPT-6.1 Sol reviews run at high too, critical work and Conductor Core's fresh-context Sol review included (Ivan,
17 Nov 2026: Sol at xhigh showed no benefit over high: 2 of 139 vs 2 of 203 final-round blocks, at about 40% more
tokens per review). xhigh stays only as the retry after a thin or failed high pass.
"""
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
BANNED = [
    re.compile(r'verify-lane[^\n]{0,90}effort: "xhigh"'),
    re.compile(r'verify-lane`?,? `?xhigh`? (on|for) money'),
    re.compile(r'verify-lane`? at `?xhigh'),
    re.compile(r'verify-lane`? `xhigh`'),
    re.compile(r'review lanes?, which may run at `xhigh`'),
    re.compile(r'except (on )?review lanes'),
    re.compile(r'review lane may run (Opus )?at `xhigh`'),
    re.compile(r'Dispatch it with effort\s+xhigh'),
    re.compile(r'dispatch at `xhigh` for money'),
    re.compile(r'\(`xhigh` for a review lane\)'),
]
HISTORY = re.compile(r'from 31 Oct to 12 Nov 2026')
# Clauses that ran GPT-6.1 Sol at xhigh by default, for critical work or a review class, before 17 Nov 2026.
SOL_BANNED = [
    re.compile(r'GPT-6\.1 Sol,? (at )?`?xhigh`?(?! showed)'),
    re.compile(r'Sol `xhigh` (on|for|plus|\+)'),
    re.compile(r'`?xhigh`? (when|for) (every |the )?(critical|change is critical)'),
    re.compile(r'(fresh-context|separate) (GPT-6\.1 )?Sol (reviewer )?(review )?(at )?`xhigh`'),
    re.compile(r'--effort xhigh`? (for|when) (a )?critical'),
    re.compile(r'at xhigh for critical'),
    re.compile(r'you at\s+`xhigh`|beside your `xhigh` review'),
    re.compile(r'\| gpt-6\.1-sol[^|\n]*\| xhigh —'),
]


class OpusReviewEffortTests(unittest.TestCase):
    def test_no_active_text_dispatches_an_opus_review_at_xhigh(self):
        names = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '*.md', '*.json'],
                               capture_output=True, text=True, check=True).stdout.split()
        hits = []
        for name in names:
            path = ROOT / name
            if path.is_symlink() or not path.is_file():
                continue
            text = path.read_text(errors='replace')
            lines = text.splitlines()
            for pattern in BANNED:
                for match in pattern.finditer(text):
                    line = text.count('\n', 0, match.start()) + 1
                    if not HISTORY.search(lines[line - 1]):
                        hits.append(f'{name}:{line}: {pattern.pattern}')
        self.assertEqual(hits, [])

    def test_no_active_text_runs_sol_at_xhigh_by_default(self):
        names = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '*.md', '*.json', 'bin/*'],
                               capture_output=True, text=True, check=True).stdout.split()
        hits = []
        for name in names:
            path = ROOT / name
            if name.startswith('.conductor/') or path.is_symlink() or not path.is_file():
                continue
            for number, line in enumerate(path.read_text(errors='replace').splitlines(), 1):
                for pattern in SOL_BANNED:
                    if pattern.search(line):
                        hits.append(f'{name}:{number}: {pattern.pattern}')
        self.assertEqual(hits, [])

    def test_the_old_sol_clauses_are_caught_and_the_retry_is_kept(self):
        for old in ('Critical work gets GPT-6.1 Sol `xhigh` + Opus 5.5 `verify-lane`',
                    '| GPT-6.1 Sol `high` via `codex-review`; `xhigh` when the change is critical or a `high` pass came back thin |',
                    '| Diff review of GPT-6.1 Sol-authored work | gpt-6.1-sol, separate fresh-context reviewer | xhigh — labelled',
                    '`-m gpt-6.1-sol --effort high` by default, `-m gpt-6.1-sol --effort xhigh` for critical changes)',
                    'computer use, exploration and overflow, at xhigh for critical review; Luna'):
            self.assertTrue(any(p.search(old) for p in SOL_BANNED), old)
        for kept in ('a `high` review that came back thin is retried at `xhigh`',
                     '| Retry when a GPT-6.1 Sol `high` review pass came back thin | gpt-6.1-sol | xhigh |'):
            self.assertFalse(any(p.search(kept) for p in SOL_BANNED), kept)

    def test_the_old_verify_lane_description_is_caught(self):
        old = 'Dispatch it with effort\n  xhigh when the change touches money, auth, personal data'
        self.assertTrue(any(p.search(old) for p in BANNED))
        self.assertFalse(any(p.search('GPT-6.1 Sol `high` and the Opus `verify-lane` at `high`') for p in BANNED))


if __name__ == '__main__':
    unittest.main()
