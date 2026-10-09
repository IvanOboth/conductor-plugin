import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    'run_trials', Path(__file__).resolve().parents[1] / 'skills/verify-skill-eval/scripts/run_trials.py')
rt = importlib.util.module_from_spec(spec)
sys.modules['run_trials'] = rt
spec.loader.exec_module(rt)

# A stub claude: counts its launches, then emits the result event named by $STUB_MODE.
STUB = """#!/bin/sh
echo run >> "$STUB_LOG"
if [ "$STUB_MODE" = error ]; then
  echo '{"type":"result","subtype":"error_during_execution","is_error":true,"result":"usage limit"}'; exit 1
fi
echo '{"type":"result","subtype":"success","is_error":false,"num_turns":3,"duration_ms":1000,"result":"done"}'
"""


class RunTrialsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / 'bin').mkdir()
        (root / 'bin/claude').write_text(STUB)
        (root / 'bin/claude').chmod(0o755)
        self.arm = root / 'arm'
        self.arm.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.arm)], check=True)
        self.log = root / 'launches'
        self.plan = {'out': str(root / 'out'), 'reps': 1, 'arms': {'a': {'cwd': str(self.arm)}},
                     'tasks': [{'id': 't1', 'prompt': 'check the page'}]}
        Path(self.plan['out']).mkdir()
        self.env = patch.dict(os.environ, {'PATH': f"{root / 'bin'}:{os.environ['PATH']}", 'STUB_LOG': str(self.log)})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def run_all(self, mode):
        os.environ['STUB_MODE'] = mode
        return [rt.run_one(self.plan, t) for t in rt.trials(self.plan)]

    def launches(self):
        return len(self.log.read_text().splitlines())

    def test_error_result_is_a_lost_trial_and_reruns(self):
        meta = self.run_all('error')[0]
        self.assertFalse(rt.parse(self.plan, meta)['finished'])
        self.run_all('ok')
        self.assertEqual(self.launches(), 2)
        self.run_all('ok')
        self.assertEqual(self.launches(), 2)

    def test_changed_prompt_or_uncommitted_guidance_invalidates_the_cache(self):
        self.run_all('ok')
        self.plan['tasks'][0]['prompt'] = 'check the other page'
        self.run_all('ok')
        (self.arm / 'GUIDE.md').write_text('new guidance\n')
        self.run_all('ok')
        self.assertEqual(self.launches(), 3)


if __name__ == '__main__':
    unittest.main()
