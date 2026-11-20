"""conductor-report counts each Codex rollout once across runs (bench-factory#686).

Before, a rollout was added to every run whose time window overlapped it, so ledger spend was counted
several times. Now a rollout is known by its full file name, and a closing run counts only what no run in
the ledger has counted for it yet, under a lock on the ledger. Every test points HOME at a temporary
folder, so it never reads or writes the live ledger, the active-runs file or real Codex sessions.
"""
from datetime import datetime, timedelta, timezone
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'conductor-report.py'
spec = importlib.util.spec_from_file_location('conductor_report', SCRIPT)
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)

FIRST = 'rollout-2026-11-16T10-00-00-019a8921-1234-7000-8000-000000000001.jsonl'
SECOND = 'rollout-2026-11-16T10-00-00-019a8921-1234-7000-8000-000000000002.jsonl'


def iso(ts):
    return ts.isoformat().replace('+00:00', 'Z')


class RolloutCountingTests(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix='conductor-report-test-'))
        self.now = datetime.now(timezone.utc).replace(microsecond=0)
        self.until = self.now + timedelta(minutes=5)
        self.ledger = self.home / '.claude' / 'telemetry' / 'conductor-runs.jsonl'
        self.session = self.home / 'session.jsonl'
        self.session.write_text(json.dumps({
            'timestamp': iso(self.now - timedelta(hours=1)),
            'message': {'model': 'claude-opus-5-5', 'usage': {'input_tokens': 10, 'output_tokens': 5}},
        }) + '\n')
        day = self.now - timedelta(hours=2)
        self.day = self.home / '.codex' / 'sessions' / f'{day.year:04d}' / f'{day.month:02d}' / f'{day.day:02d}'
        self.day.mkdir(parents=True)

    def write_rollout(self, name, input_tokens, modified):
        """A rollout whose latest token_count reports input_tokens in total (none at all when None)."""
        lines = [json.dumps({'timestamp': iso(self.now - timedelta(hours=2)), 'type': 'session_meta', 'payload': {}})]
        if input_tokens is not None:
            lines.append(json.dumps({'timestamp': iso(modified), 'payload': {
                'type': 'token_count', 'model': 'gpt-6.2-sol',
                'info': {'total_token_usage': {'input_tokens': input_tokens, 'output_tokens': 0}}}}))
        path = self.day / name
        path.write_text('\n'.join(lines) + '\n')
        os.utime(path, (modified.timestamp(), modified.timestamp()))

    def argv(self, run_id, since):
        return ['--run-id', run_id, '--session', str(self.session), '--since', since.isoformat(),
                '--until', self.until.isoformat(), '--ledger', str(self.ledger)]

    def close_run(self, run_id, since):
        result = subprocess.run([sys.executable, str(SCRIPT), *self.argv(run_id, since)],
                                env={**os.environ, 'HOME': str(self.home)}, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def counted(self):
        """{run_id: {rollout file name: input tokens counted}} from the ledger."""
        rows = [json.loads(line) for line in self.ledger.read_text().splitlines()]
        return {row['run_id']: {lane['rollout']: lane['in'] for lane in row['lanes'] if 'rollout' in lane}
                for row in rows}

    def test_two_closed_runs_count_an_overlapping_rollout_once(self):
        self.write_rollout(FIRST, 1000, self.now - timedelta(hours=1))
        self.close_run('run-a', self.now - timedelta(hours=3))
        out_b = self.close_run('run-b', self.now - timedelta(minutes=150))
        self.assertEqual(self.counted(), {'run-a': {FIRST: 1000}, 'run-b': {}})
        self.assertIn('already counted in full by earlier runs, left out here: 1', out_b)

    def test_a_rollout_filed_under_the_day_before_the_window_is_counted(self):
        # Codex files a rollout under the (local) date it started; a lane that started before
        # midnight, or before the run window, lives in the previous day's folder.
        since = self.now - timedelta(minutes=30)
        before = since - timedelta(days=1)
        self.day = self.home / '.codex' / 'sessions' / f'{before.year:04d}' / f'{before.month:02d}' / f'{before.day:02d}'
        self.day.mkdir(parents=True, exist_ok=True)
        self.write_rollout(FIRST, 1000, self.now - timedelta(minutes=10))
        self.close_run('run-a', since)
        self.assertEqual(self.counted(), {'run-a': {FIRST: 1000}})

    def test_a_rollout_that_grows_between_closes_is_counted_once_in_total(self):
        self.write_rollout(FIRST, 1_000_000, self.now - timedelta(hours=1))
        self.close_run('run-a', self.now - timedelta(hours=3))
        self.write_rollout(FIRST, 3_000_000, self.now - timedelta(minutes=30))
        self.close_run('run-b', self.now - timedelta(minutes=90))
        self.assertEqual(self.counted(), {'run-a': {FIRST: 1_000_000}, 'run-b': {FIRST: 2_000_000}})

    def test_two_concurrent_closes_count_a_rollout_once(self):
        self.write_rollout(FIRST, 1000, self.now - timedelta(hours=1))
        barrier = threading.Barrier(2, timeout=3)
        real = report.counted_rollouts

        def read_side_by_side(path):
            # Without the lock both closes read the empty ledger, then meet here, then both append.
            # With it the second close cannot read until the first has appended (the first waits
            # out the barrier alone, and the second finds it broken).
            counted = real(path)
            try:
                barrier.wait()
            except threading.BrokenBarrierError:
                pass
            return counted

        errors = []

        def close(run_id):
            try:
                report.main(self.argv(run_id, self.now - timedelta(hours=3)))
            except BaseException as exc:  # noqa: BLE001 - surfaced through the assertion below
                errors.append(exc)

        with open(os.devnull, 'w') as quiet, \
                mock.patch.object(report, 'HOME', str(self.home)), \
                mock.patch.object(report, 'ACTIVE_RUNS', str(self.home / 'active-runs.json')), \
                mock.patch.object(report, 'counted_rollouts', read_side_by_side), \
                mock.patch('sys.stdout', new=quiet):
            threads = [threading.Thread(target=close, args=(rid,)) for rid in ('run-a', 'run-b')]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        self.assertEqual(errors, [])
        counts = self.counted()
        self.assertEqual(sorted(counts), ['run-a', 'run-b'])
        self.assertEqual(sum(sum(lanes.values()) for lanes in counts.values()), 1000)

    def test_rollouts_sharing_the_display_prefix_are_counted_separately(self):
        self.assertEqual(FIRST[:40], SECOND[:40])
        self.write_rollout(FIRST, 1000, self.now - timedelta(hours=1))
        self.write_rollout(SECOND, None, self.now - timedelta(hours=1))
        self.close_run('run-a', self.now - timedelta(hours=3))
        self.write_rollout(SECOND, 500, self.now - timedelta(minutes=30))
        self.close_run('run-b', self.now - timedelta(minutes=150))
        self.assertEqual(self.counted(), {'run-a': {FIRST: 1000}, 'run-b': {SECOND: 500}})

    def test_rows_from_before_the_rollout_field_count_by_agent_name(self):
        # The script before this change wrote Codex lanes with only the display name in "agent".
        self.write_rollout(FIRST, 1_000_000, self.now - timedelta(hours=1))
        self.ledger.parent.mkdir(parents=True)
        old_row = {'run_id': 'run-old', 'lanes': [
            {'agent': 'orchestrator', 'family': 'anthropic', 'model': 'claude-opus-5-5',
             'in': 10, 'out': 5, 'cr': 0, 'cw': 0},
            {'agent': FIRST.replace('.jsonl', '')[:40], 'family': 'openai', 'model': 'gpt-6.2-sol',
             'in': 1_000_000, 'out': 0, 'cr': 0, 'cw': 0}]}
        self.ledger.write_text(json.dumps(old_row) + '\n')
        self.close_run('run-b', self.now - timedelta(minutes=150))
        self.write_rollout(FIRST, 3_000_000, self.now - timedelta(minutes=30))
        self.close_run('run-c', self.now - timedelta(minutes=90))
        self.assertEqual(self.counted(), {'run-old': {}, 'run-b': {}, 'run-c': {FIRST: 2_000_000}})

    def test_an_abandoned_active_entry_changes_nothing(self):
        self.write_rollout(FIRST, 1000, self.now - timedelta(hours=1))
        active = self.home / '.claude' / 'telemetry' / 'active-runs.json'
        active.parent.mkdir(parents=True)
        entry = {'never-closed': {'run_id': 'never-closed', 'started': (self.now - timedelta(hours=3)).isoformat()}}
        active.write_text(json.dumps(entry))
        self.close_run('run-b', self.now - timedelta(minutes=90))
        self.assertEqual(self.counted(), {'run-b': {FIRST: 1000}})
        self.assertEqual(json.loads(active.read_text()), entry)


if __name__ == '__main__':
    unittest.main()
