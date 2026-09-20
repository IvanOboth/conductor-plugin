"""Execute the helper launchers against fake CLIs; never call a model."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PANE_KEYS = ('ORCA_PANE_KEY', 'ORCA_TAB_ID', 'ORCA_AGENT_LAUNCH_TOKEN')


class HeadlessOrcaIsolationTests(unittest.TestCase):
    def test_child_does_not_inherit_parent_pane_identity(self):
        launchers = [ROOT / 'bin' / name for name in ('ask-claude', 'ask-codex')]
        installed = os.environ.get('ORCA_TEST_INSTALLED_HELPERS')
        if installed:
            launchers += [Path(installed) / name for name in ('ask-claude', 'ask-codex')]
        with tempfile.TemporaryDirectory(prefix='orca-helper-test-') as directory:
            bindir = Path(directory)
            fake = '''#!/usr/bin/env python3
import json, os
print(json.dumps({'probe': 'orca-isolation', 'pane': {k: os.environ.get(k) for k in ('ORCA_PANE_KEY', 'ORCA_TAB_ID', 'ORCA_AGENT_LAUNCH_TOKEN')}, 'context': os.environ.get('ORCA_ISOLATION_TEST_CONTEXT')}))
'''
            for name in ('claude', 'codex'):
                executable = bindir / name
                executable.write_text(fake)
                executable.chmod(0o755)
            env = {**os.environ, 'PATH': str(bindir) + os.pathsep + os.environ['PATH'],
                   'ORCA_ISOLATION_TEST_CONTEXT': 'preserve-context',
                   **{key: 'parent-only' for key in PANE_KEYS}}
            for launcher in launchers:
                with self.subTest(launcher=str(launcher)):
                    result = subprocess.run(['bash', str(launcher), 'isolation probe'],
                                            env=env, capture_output=True, text=True, timeout=15)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    probes = [json.loads(line) for line in result.stdout.splitlines()
                              if line.startswith('{"probe": "orca-isolation"')]
                    self.assertEqual(len(probes), 1, result.stdout)
                    self.assertEqual(probes[0]['pane'], dict.fromkeys(PANE_KEYS))
                    self.assertEqual(probes[0]['context'], 'preserve-context')
                    print('PASS:', launcher, 'child pane identity absent; other context preserved')


if __name__ == '__main__':
    unittest.main()
