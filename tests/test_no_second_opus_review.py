"""The second Opus review of critical work is removed (Ivan, 18 Nov 2026: "Remove the second Opus review as well").

Opus-authored critical work, `sev:1` items and production data changes get the GPT-6.2 Sol `high` review alone,
plus the orchestrator's own read of the diff. No skill, agent, team-config copy or README may still run the
Opus 5.5 `verify-lane` beside it. Two cases stay: the `verify-lane` reviews critical work GPT-6.2 Sol wrote, and
a fresh-context Opus 5.5 reviewer takes Sol's place when Codex cannot run.
"""
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
BANNED = [
    re.compile(r'GPT-6\.[12] Sol `?high`? (and|plus|\+) (the |an )?(Opus( 5\.5)? )?`?verify-lane'),
    re.compile(r'plus `verify-lane` `high` review'),
    re.compile(r'always runs beside (it|the GPT-6\.[12] Sol)'),
    re.compile(r'beside the Opus 5\.5 `verify-lane` judgment review for critical'),
    re.compile(r'critical beside the Opus 5\.5 `verify-lane`'),
    re.compile(r'critical work two independent'),
    re.compile(r'two independent (fresh-context )?Opus 5\.5 (reviews|lanes) for critical'),
    re.compile(r'one of the two critical reviews'),
    re.compile(r'GPT-6\.[12] Sol (at )?`high` and an Opus 5\.5 judgment review'),
    re.compile(r'beside an Opus 5\.5 fresh-context judgment review'),
    re.compile(r'both reviews on critical work'),
]


def tracked_text_files():
    names = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '*.md', '*.json'],
                           capture_output=True, text=True, check=True).stdout.split()
    for name in names:
        path = ROOT / name
        if name.startswith('.conductor/') or path.is_symlink() or not path.is_file():
            continue
        yield name, path.read_text(errors='replace')


class NoSecondOpusReviewTests(unittest.TestCase):
    def test_no_active_text_runs_the_verify_lane_beside_sol(self):
        hits = []
        for name, text in tracked_text_files():
            flat = re.sub(r'\s+', ' ', text)
            for pattern in BANNED:
                if pattern.search(flat):
                    hits.append(f'{name}: {pattern.pattern}')
        self.assertEqual(hits, [])

    def test_the_old_clauses_are_caught(self):
        for old in ('A `sev:1` item always gets the critical review (GPT-6.1 Sol `high` and the Opus `verify-lane` at `high`)',
                    'with a copy of the rows first, GPT-6.1 Sol `high` plus `verify-lane` `high` review, and a read-back',
                    'Opus-authored, critical → GPT-6.1 Sol `high` + Opus 5.5 `verify-lane` in fresh context',
                    'Critical work gets GPT-6.1 Sol at `high` and an Opus 5.5 judgment review at `high` in fresh context',
                    'routine work gets one Opus 5.5 `high` reviewer in fresh context, critical work two independent ones'):
            self.assertTrue(any(p.search(old) for p in BANNED), old)

    def test_the_kept_cases_are_stated(self):
        agent = (ROOT / 'agents/verify-lane.md').read_text()
        self.assertIn('critical work that GPT-6.2 Sol wrote', re.sub(r'\s+', ' ', agent))
        self.assertIn("in\n  place of the GPT-6.2 Sol review when Sol cannot run", agent)
        agents_md = (ROOT / 'team-config/AGENTS.md').read_text()
        self.assertIn('GPT-6.2 Sol-authored, critical → the Opus 5.5 `verify-lane` at `high`.', agents_md)
        claude_md = (ROOT / 'team-config/CLAUDE.md').read_text()
        self.assertIn('still reviews critical work that GPT-6.2 Sol wrote', claude_md)
        self.assertIn('its review goes to Opus 5.5 `high` in a fresh context, never to Fable 5.2', claude_md)


if __name__ == '__main__':
    unittest.main()
