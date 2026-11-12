"""Opus reviews run at high (Ivan, 12 Nov 2026: "opus reviews at xhigh are unnecessary, high is good enough").

No skill, agent, team-config copy or README may prescribe the Opus 5.5 verify-lane, or any Opus review lane, at
xhigh. GPT-6.1 Sol stays at xhigh for critical reviews; dated notes about 31 Oct to 12 Nov 2026 are history.
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

    def test_the_old_verify_lane_description_is_caught(self):
        old = 'Dispatch it with effort\n  xhigh when the change touches money, auth, personal data'
        self.assertTrue(any(p.search(old) for p in BANNED))
        self.assertFalse(any(p.search('GPT-6.1 Sol `xhigh` and the Opus `verify-lane` at `high`') for p in BANNED))


if __name__ == '__main__':
    unittest.main()
