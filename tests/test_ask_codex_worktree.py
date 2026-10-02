"""Offline coverage for ask-codex --worktree, --resume and the session id line (#19)."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'bin/ask-codex'
SESSION = '01a0fc4d-31bf-7df0-9335-8530299f95f3'

# Records every call as one JSON line and prints a codex-style session header.
FAKE_CODEX = r'''#!/usr/bin/env python3
import json,os,sys
args=sys.argv[1:]
c_dir=os.path.realpath(args[args.index('-C')+1]) if '-C' in args else None
open(os.environ['CODEX_LOG'],'a').write(json.dumps({'cwd':os.getcwd(),'c_dir':c_dir,'argv':args})+'\n')
print('session id: %s' % os.environ['FAKE_SESSION'],file=sys.stderr,flush=True)
if os.environ.get('FAKE_SLEEP'):
    import time; time.sleep(float(os.environ['FAKE_SLEEP']))
if '-o' in args: open(args[args.index('-o')+1],'w').write('final\n')
print('pong')
'''


def slug(branch):
    return branch.replace('/', '-') + '-' + hashlib.sha1(branch.encode()).hexdigest()[:8]


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

    def env(self, **extra):
        env = {k: v for k, v in os.environ.items() if k != 'CODEX_HOME'}
        # An explicit CODEX_HOME skips the Orca account lookup.
        env.update(PATH=f'{self.bin}{os.pathsep}{env["PATH"]}', HOME=str(self.root),
                   CODEX_HOME=str(self.root / 'home'), CODEX_LOG=str(self.codex_log),
                   FAKE_SESSION=SESSION, ASK_CODEX_WORKTREE_ROOT=str(self.wt_root),
                   ASK_CODEX_POLL_SECONDS='0.1')
        env.update(extra)
        return env

    def run_ask(self, *args, **extra):
        return subprocess.run(['bash', str(SCRIPT), *args], cwd=self.repo, env=self.env(**extra),
                              text=True, capture_output=True, stdin=subprocess.DEVNULL, timeout=60)

    def calls(self):
        return [json.loads(line) for line in self.codex_log.read_text().splitlines()]

    def test_worktree_created_on_branch_passed_with_C_and_reused(self):
        result = self.run_ask('--worktree', 'lane/x', 'do the order')
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.wt_root / 'repo' / slug('lane/x')
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
        path = self.wt_root / 'repo' / slug('lane/y')
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

    def test_resume_hint_is_complete_and_resume_uses_saved_cwd(self):
        result = self.run_ask('--worktree', 'lane/z', '--readonly', '-m', 'gpt-6.1-sol',
                              '--effort', 'xhigh', 'review it')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'(continue it with: ask-codex --resume {SESSION} --worktree lane/z --readonly'
                      ' -m gpt-6.1-sol --effort xhigh)', result.stderr)
        # Same shape as a codex 0.160 rollout: first line is session_meta with payload.cwd.
        saved = self.root / 'saved'; saved.mkdir()
        day = self.root / 'home' / 'sessions' / '2026' / '10' / '02'; day.mkdir(parents=True)
        (day / f'rollout-2026-10-02T07-30-23-{SESSION}.jsonl').write_text(
            json.dumps({'type': 'session_meta', 'payload': {'id': SESSION, 'cwd': str(saved)}}) + '\n')
        resumed = self.run_ask('--resume', SESSION)
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertEqual(Path(self.calls()[-1]['cwd']).resolve(), saved)
        self.assertIn(f'in its saved directory {saved}', resumed.stderr)
        missing = self.run_ask('--resume', '22222222-0000-0000-0000-000000000000')
        self.assertEqual(missing.returncode, 0, missing.stderr)
        self.assertEqual(Path(self.calls()[-1]['cwd']).resolve(), self.repo)
        self.assertIn('the current directory decides where the lane works', missing.stderr)

    def test_resume_hint_repeats_clean(self):
        result = self.run_ask('--clean', 'summarise')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'(continue it with: ask-codex --resume {SESSION} --clean)', result.stderr)

    def test_worktree_folder_is_collision_resistant(self):
        first = self.run_ask('--worktree', 'lane/x', 'one')
        self.assertEqual(first.returncode, 0, first.stderr)
        second = self.run_ask('--worktree', 'lane-x', 'two')
        self.assertEqual(second.returncode, 0, second.stderr)
        a, b = self.wt_root / 'repo' / slug('lane/x'), self.wt_root / 'repo' / slug('lane-x')
        self.assertNotEqual(a, b)
        self.assertTrue(a.name.startswith('lane-x-') and b.name.startswith('lane-x-'))
        for path, branch in ((a, 'lane/x'), (b, 'lane-x')):
            current = subprocess.run(['git', '-C', str(path), 'branch', '--show-current'],
                                     capture_output=True, text=True, check=True).stdout.strip()
            self.assertEqual(current, branch)

    def test_worktree_works_without_gnu_realpath(self):
        # BSD realpath has no -m; the launcher must not depend on it.
        fake = self.bin / 'realpath'
        fake.write_text('#!/bin/sh\nfor a in "$@"; do [ "$a" = -m ] && { echo "realpath: illegal option -- m" >&2; exit 64; }; done\necho "$1"\n')
        fake.chmod(0o755)
        result = self.run_ask('--worktree', 'lane/bsd', 'go')
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.wt_root / 'repo' / slug('lane/bsd')
        self.assertTrue((path / 'a.txt').is_file())
        self.assertEqual(self.calls()[0]['c_dir'], str(path))

    def test_relative_worktree_root_is_made_absolute(self):
        result = self.run_ask('--worktree', 'lane/rel', 'go', ASK_CODEX_WORKTREE_ROOT='relative-root')
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.repo / 'relative-root' / 'repo' / slug('lane/rel')
        call = self.calls()[0]
        self.assertTrue(call['argv'][call['argv'].index('-C') + 1].startswith('/'))
        self.assertEqual(call['c_dir'], str(path))
        self.assertEqual(Path(call['cwd']).resolve(), path)

    def test_hint_printed_before_a_killed_lane_exits(self):
        err = self.root / 'err.txt'
        with open(err, 'w') as handle:
            proc = subprocess.Popen(['bash', str(SCRIPT), 'long order'], cwd=self.repo,
                                    env=self.env(FAKE_SLEEP='30'), stdin=subprocess.DEVNULL,
                                    stdout=subprocess.DEVNULL, stderr=handle, start_new_session=True)
            deadline = time.time() + 10
            while time.time() < deadline and 'continue it with' not in err.read_text():
                time.sleep(0.1)
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=10)
        self.assertIn(f'ask-codex: session id {SESSION} (continue it with: ask-codex --resume {SESSION})',
                      err.read_text())

    def test_resume_never_reads_an_open_stdin(self):
        proc = subprocess.Popen(['bash', str(SCRIPT), '--resume', SESSION], cwd=self.repo,
                                env=self.env(), stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        try:
            self.assertEqual(proc.wait(timeout=20), 0)
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.stdin.close()
        self.assertEqual(self.calls()[0]['argv'][:2], ['exec', 'resume'])


if __name__ == '__main__':
    unittest.main()


STDIN_CODEX = r'''#!/usr/bin/env python3
import os,sys
open(os.environ['STDIN_LOG'],'w').write(sys.stdin.read())
print('session id: %s' % os.environ['FAKE_SESSION'],file=sys.stderr,flush=True)
print('pong')
'''

# Its SIGINT handler stands in for codex stopping the tools it started: it
# writes a marker before exiting, which must happen before the launcher returns.
INT_CODEX = r'''#!/usr/bin/env python3
import os,signal,sys,time
def stop(*_):
    time.sleep(0.5)
    open(os.environ['CLEANUP_LOG'],'w').write('cleaned\n')
    sys.exit(130)
signal.signal(signal.SIGINT, stop)
print('session id: %s' % os.environ['FAKE_SESSION'],file=sys.stderr,flush=True)
time.sleep(30)
'''


class AskCodexLaunchContract(unittest.TestCase):
    setUp = AskCodexWorktree.setUp
    env = AskCodexWorktree.env

    def test_fresh_run_passes_the_callers_stdin_to_codex(self):
        (self.bin / 'codex').write_text(STDIN_CODEX)
        log = self.root / 'stdin.txt'
        result = subprocess.run(['bash', str(SCRIPT), '-'], cwd=self.repo,
                                env=self.env(STDIN_LOG=str(log)), text=True, input='work order\n',
                                capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(log.read_text(), 'work order\n')

    def test_interrupt_waits_for_codex_cleanup(self):
        (self.bin / 'codex').write_text(INT_CODEX)
        marker = self.root / 'cleanup.txt'
        proc = subprocess.Popen(['bash', str(SCRIPT), 'long order'], cwd=self.repo,
                                env=self.env(CLEANUP_LOG=str(marker)), text=True,
                                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, start_new_session=True)
        time.sleep(2)  # past codex's session header and into its sleep
        os.killpg(proc.pid, signal.SIGINT)
        proc.wait(timeout=20)
        self.assertEqual(proc.returncode, 130)
        self.assertTrue(marker.exists(), 'launcher returned before codex finished its cleanup')
