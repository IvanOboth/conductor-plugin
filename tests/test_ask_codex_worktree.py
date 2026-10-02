"""Offline coverage for ask-codex --worktree, --resume and the session id line (#19)."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'bin/ask-codex'
SESSION = '01a0fc4d-31bf-7df0-9335-8530299f95f3'

# Records every call as one JSON line and prints a codex-style session header.
FAKE_CODEX = r'''#!/usr/bin/env python3
import json,os,sys
open(os.environ['CODEX_LOG'],'a').write(json.dumps({'cwd':os.getcwd(),'argv':sys.argv[1:]})+'\n')
print('session id: %s' % os.environ['FAKE_SESSION'],file=sys.stderr)
args=sys.argv[1:]
if '-o' in args: open(args[args.index('-o')+1],'w').write('final\n')
print('pong')
'''


class AskCodexWorktree(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.bin = self.root / 'bin'; self.bin.mkdir()
        codex = self.bin / 'codex'; codex.write_text(FAKE_CODEX); codex.chmod(0o755)
        self.repo = self.root / 'repo'; self.repo.mkdir()
        git = ['git', '-C', str(self.repo), '-c', 'user.name=t', '-c', 'user.email=t@t']
        subprocess.run(['git', 'init', '-q', '-b', 'main', str(self.repo)], check=True)
        (self.repo / 'a.txt').write_text('a\n')
        subprocess.run(git + ['add', 'a.txt'], check=True)
        subprocess.run(git + ['commit', '-qm', 'init'], check=True)
        self.codex_log = self.root / 'codex.jsonl'
        self.wt_root = self.root / 'wt'

    def run_ask(self, *args):
        env = {k: v for k, v in os.environ.items() if k != 'CODEX_HOME'}
        # An explicit CODEX_HOME skips the Orca account lookup.
        env.update(PATH=f'{self.bin}{os.pathsep}{env["PATH"]}', HOME=str(self.root),
                   CODEX_HOME=str(self.root / 'home'), CODEX_LOG=str(self.codex_log),
                   FAKE_SESSION=SESSION, ASK_CODEX_WORKTREE_ROOT=str(self.wt_root))
        return subprocess.run(['bash', str(SCRIPT), *args], cwd=self.repo, env=env, text=True,
                              capture_output=True, stdin=subprocess.DEVNULL, timeout=60)

    def calls(self):
        return [json.loads(line) for line in self.codex_log.read_text().splitlines()]

    def test_worktree_created_on_branch_passed_with_C_and_reused(self):
        result = self.run_ask('--worktree', 'lane/x', 'do the order')
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.wt_root / 'repo' / 'lane-x'
        branch = subprocess.run(['git', '-C', str(path), 'branch', '--show-current'],
                                capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(branch, 'lane/x')
        argv = self.calls()[0]['argv']
        self.assertEqual(argv[:1], ['exec'])
        self.assertEqual(argv[argv.index('-C') + 1], str(path))
        self.assertIn(f'git worktree {path} on branch lane/x', argv[-1])
        self.assertTrue(argv[-1].endswith('do the order'))
        self.assertIn(f'git worktree remove {path}', result.stderr)
        again = self.run_ask('--worktree', 'lane/x', 'continue')
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertIn('reusing worktree', again.stderr)
        second = self.calls()[1]['argv']
        self.assertEqual(second[second.index('-C') + 1], str(path))

    def test_resume_uses_exec_resume_with_sandbox_config_and_no_C(self):
        self.run_ask('--worktree', 'lane/y', 'first run')
        path = self.wt_root / 'repo' / 'lane-y'
        result = self.run_ask('--resume', SESSION, '--worktree', 'lane/y', '-m', 'gpt-6.1-sol',
                              '-o', 'out.md')
        self.assertEqual(result.returncode, 0, result.stderr)
        call = self.calls()[1]
        argv = call['argv']
        self.assertEqual(argv[:2], ['exec', 'resume'])
        self.assertNotIn('-C', argv)
        self.assertNotIn('--sandbox', argv)
        self.assertIn('sandbox_mode="workspace-write"', argv)
        self.assertIn('approval_policy=never', argv)
        self.assertIn('gpt-6.1-sol', argv)
        self.assertEqual(argv[-2], SESSION)
        self.assertIn('Continue the same work order', argv[-1])
        self.assertNotIn('WORKTREE:', argv[-1])
        self.assertNotIn('OUTPUT INSTRUCTION', argv[-1])
        self.assertEqual(Path(call['cwd']).resolve(), path)

    def test_session_id_line_printed_after_plain_run(self):
        result = self.run_ask('plain prompt')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls()[0]['argv'][-1], 'plain prompt')
        self.assertIn(f'ask-codex: session id {SESSION} (continue it with: ask-codex --resume {SESSION})',
                      result.stderr)


if __name__ == '__main__':
    unittest.main()
