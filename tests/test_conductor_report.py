"""conductor-report counts each Codex rollout in one run only (bench-factory#686).

Before, a rollout was added to every run whose time window overlapped it, so ledger spend was counted
several times. Each test runs the script with HOME set to a temporary folder, so it never reads or
writes the live ledger, the active-runs file or real Codex sessions.
"""
from datetime import datetime, timedelta, timezone
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'conductor-report.py'
spec = importlib.util.spec_from_file_location('conductor_report', SCRIPT)
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


def iso(ts):
    return ts.isoformat().replace('+00:00', 'Z')


class OverlappingRunsTests(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix='conductor-report-test-'))
        self.now = datetime.now(timezone.utc).replace(microsecond=0)
        self.ledger = self.home / '.claude' / 'telemetry' / 'conductor-runs.jsonl'
        self.session = self.home / 'session.jsonl'
        self.session.write_text(json.dumps({
            'timestamp': iso(self.now - timedelta(hours=1)),
            'message': {'model': 'claude-opus-5-5', 'usage': {'input_tokens': 10, 'output_tokens': 5}},
        }) + '\n')
        # One Codex rollout from now-2h to now-1h, inside both runs' windows.
        start, end = self.now - timedelta(hours=2), self.now - timedelta(hours=1)
        day = self.home / '.codex' / 'sessions' / f'{start.year:04d}' / f'{start.month:02d}' / f'{start.day:02d}'
        day.mkdir(parents=True)
        self.rollout = day / 'rollout-2026-11-16T10-00-00-0000000-aaaa-bbbb-cccc.jsonl'
        self.rollout.write_text(
            json.dumps({'timestamp': iso(start), 'type': 'session_meta', 'payload': {}}) + '\n'
            + json.dumps({'timestamp': iso(end), 'payload': {
                'type': 'token_count', 'model': 'gpt-6.1-sol',
                'info': {'total_token_usage': {'input_tokens': 1000, 'output_tokens': 100}}}}) + '\n')
        os.utime(self.rollout, (end.timestamp(), end.timestamp()))
        self.agent = self.rollout.name.replace('.jsonl', '')[:40]

    def close_run(self, run_id, since):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), '--run-id', run_id, '--session', str(self.session),
             '--since', since.isoformat(), '--until', (self.now + timedelta(minutes=5)).isoformat(),
             '--ledger', str(self.ledger)],
            env={**os.environ, 'HOME': str(self.home)}, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def rollout_counts(self):
        rows = [json.loads(line) for line in self.ledger.read_text().splitlines()]
        return {row['run_id']: [lane['agent'] for lane in row['lanes']].count(self.agent) for row in rows}

    def test_two_closed_runs_count_an_overlapping_rollout_once(self):
        self.close_run('run-a', self.now - timedelta(hours=3))
        out_b = self.close_run('run-b', self.now - timedelta(minutes=150))
        self.assertEqual(self.rollout_counts(), {'run-a': 1, 'run-b': 0})
        self.assertIn('counted in another run, left out here: 1', out_b)

    def test_an_active_run_with_the_larger_overlap_owns_the_rollout(self):
        active = self.home / '.claude' / 'telemetry' / 'active-runs.json'
        active.parent.mkdir(parents=True)
        active.write_text(json.dumps({'run-a': {'run_id': 'run-a', 'started': (self.now - timedelta(hours=3)).isoformat()}}))
        # run-b overlaps the rollout for 30 minutes; run-a, still active, for the whole hour.
        self.close_run('run-b', self.now - timedelta(minutes=90))
        self.assertEqual(self.rollout_counts(), {'run-b': 0})
        active.write_text('{}')
        self.close_run('run-a', self.now - timedelta(hours=3))
        self.assertEqual(self.rollout_counts(), {'run-b': 0, 'run-a': 1})

    def test_a_stale_active_entry_does_not_swallow_rollouts(self):
        stale = [{'run_id': 'never-closed', 'start': self.now - timedelta(days=9)}]
        with unittest.mock.patch.object(report, 'load_active', return_value={
                'never-closed': {'started': stale[0]['start'].isoformat()}}):
            claimed, open_runs = report.other_runs(str(self.ledger), 'run-b', self.now)
        self.assertEqual(open_runs, [])
        lane = {'agent': self.agent, '_window': (self.now - timedelta(hours=2), self.now - timedelta(hours=1))}
        kept, elsewhere = report.claim_rollouts([lane], self.now - timedelta(minutes=90), self.now, claimed, open_runs)
        self.assertEqual((len(kept), len(elsewhere)), (1, 0))


if __name__ == '__main__':
    unittest.main()
