import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WATCH = ROOT / 'scripts/context-watch.py'
HANDOFF = ROOT / 'bin/conductor-handoff'
INSTALL = ROOT / 'scripts/install-context-hook.py'

FAKE_ORCA = '''#!/usr/bin/env python3
import json, os, sys
open(os.environ['ORCA_LOG'], 'a').write(json.dumps(sys.argv[1:]) + '\\n')
cmd = sys.argv[1:3]
if cmd == ['status', '--json']:
    r = {'runtime': {'state': os.environ.get('ORCA_STATE', 'ready')}}
elif cmd == ['terminal', 'create']:
    if os.environ.get('ORCA_SLOW'):
        import time; time.sleep(1)
    r = {'terminal': {'handle': 'term_new'}}
elif cmd == ['terminal', 'show']:
    if os.environ.get('ORCA_SHOW_FAIL'):
        print(json.dumps({'ok': False, 'error': {'code': 'timeout'}}))
        sys.exit(1)
    r = {'terminal': {'title': '\u25d1 #896 API v1 conductor', 'connected': True}}
elif cmd == ['terminal', 'send']:
    mode = open(os.environ['ORCA_SEND']).read().strip() if os.path.exists(os.environ.get('ORCA_SEND', '')) else 'ok'
    if mode == 'reject':
        print(json.dumps({'ok': True, 'result': {'send': {'accepted': False}}}))
        sys.exit(1)
    if mode == 'lost':
        print(json.dumps({'ok': False, 'error': {'code': 'transport', 'data': {'orchestrationRequestId': 'req-lost'}}}))
        sys.exit(1)
    stages = ['input_accepted'] + (['turn_started'] if mode == 'ok' else [])
    r = {'send': {'accepted': True, 'prompt': {'requestId': 'req1', 'stages': stages}}}
else:
    r = {}
print(json.dumps({'ok': True, 'result': r}))
'''


def assistant(tokens, model='claude-opus-5-5', sidechain=False):
    return {'type': 'assistant', 'isSidechain': sidechain, 'message': {'model': model, 'usage': {
        'input_tokens': 10, 'cache_creation_input_tokens': 0, 'cache_read_input_tokens': tokens - 10}}}


class ContextWatchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.state = self.dir / 'state'
        self.transcript = self.dir / 's1.jsonl'
        self.cwd = self.dir / 'repo'
        self.cwd.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, *rows, skill='conductor'):
        lines = []
        if skill:
            lines.append({'type': 'user', 'message': {'content': [{'type': 'text', 'text':
                          f'Base directory for this skill: /home/x/dev/conductor-plugin/skills/{skill}\n\n# Conductor'}]}})
        lines += rows
        self.transcript.write_text(''.join(json.dumps(r) + '\n' for r in lines))

    def run_hook(self, event='PostToolUse', **extra):
        payload = {'hook_event_name': event, 'session_id': 's1', 'transcript_path': str(self.transcript),
                   'cwd': str(self.cwd), 'permission_mode': 'bypassPermissions', **extra}
        env = dict(os.environ, XDG_STATE_HOME=str(self.state))
        for k in ('CONDUCTOR_CONTEXT_WATCH', 'CONDUCTOR_HANDOFF_PCT', 'CONDUCTOR_CONTEXT_WINDOW'):
            env.pop(k, None)
        p = subprocess.run([sys.executable, str(WATCH)], input=json.dumps(payload), capture_output=True,
                           text=True, env=env)
        self.assertEqual(p.returncode, 0)
        return json.loads(p.stdout) if p.stdout.strip() else None

    def test_below_threshold_is_silent(self):
        self.write(assistant(650_000))
        self.assertIsNone(self.run_hook())

    def test_threshold_injects_once_then_stop_blocks_once(self):
        self.write(assistant(720_000), assistant(990_000, sidechain=True))
        out = self.run_hook()
        ctx = out['hookSpecificOutput']['additionalContext']
        self.assertIn('72%', ctx)
        self.assertIn('conductor-handoff', ctx)
        self.assertIsNone(self.run_hook())
        stop = self.run_hook('Stop', stop_hook_active=False)
        self.assertEqual(stop['decision'], 'block')
        self.assertIsNone(self.run_hook('Stop', stop_hook_active=True))
        self.assertIsNone(self.run_hook('Stop', stop_hook_active=False))

    def test_now_level_says_hand_off_now(self):
        self.write(assistant(720_000))
        self.run_hook()
        self.write(assistant(870_000))
        self.assertIn('Hand off now', self.run_hook()['hookSpecificOutput']['additionalContext'])

    def test_compaction_rearms_the_levels(self):
        self.write(assistant(750_000))
        self.assertIsNotNone(self.run_hook())
        self.write(assistant(120_000))
        self.assertIsNone(self.run_hook())
        self.write(assistant(710_000))
        self.assertIsNotNone(self.run_hook())

    def test_subagent_and_non_conductor_sessions_are_ignored(self):
        self.write(assistant(900_000))
        self.assertIsNone(self.run_hook(agent_id='abc'))
        self.write(assistant(900_000), skill=None)
        self.state = self.dir / 'state2'
        self.assertIsNone(self.run_hook())

    def test_work_list_marks_a_conductor_session(self):
        self.write(assistant(900_000), skill=None)
        (self.cwd / '.conductor').mkdir()
        (self.cwd / '.conductor/work-list.md').write_text('- item\n')
        self.assertIsNotNone(self.run_hook())

    def test_statusline_window_overrides_model_default(self):
        self.write(assistant(150_000, model='claude-fable-5-1'))
        self.assertIsNone(self.run_hook())
        (self.state / 'conductor/context/s1.window').write_text('200000\n')
        self.assertIn('75%', self.run_hook()['hookSpecificOutput']['additionalContext'])

    def test_recorded_handoff_silences_the_watch(self):
        self.write(assistant(900_000))
        self.run_hook()
        (self.state / 'conductor/context/s1.handoff.json').write_text(json.dumps({'status': 'done'}))
        self.assertIsNone(self.run_hook('Stop', stop_hook_active=False))


class HandoffTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.wt = self.dir / 'wt'
        (self.wt / '.conductor/work-orders').mkdir(parents=True)
        subprocess.run(['git', 'init', '-q', str(self.wt)], check=True)
        self.order = self.wt / '.conductor/work-orders/run-continue.md'
        self.order.write_text('# Continue\n' + 'state line\n' * 60)
        self.bin = self.dir / 'bin'
        self.bin.mkdir()
        (self.bin / 'orca').write_text(FAKE_ORCA)
        (self.bin / 'orca').chmod(0o755)
        self.log = self.dir / 'orca.log'
        self.state = self.dir / 'state'
        sd = self.state / 'conductor/context'
        sd.mkdir(parents=True)
        (sd / 's1.json').write_text(json.dumps({'skill': 'conductor-claude', 'model': 'claude-opus-5-5',
                                                'permission_mode': 'bypassPermissions', 'pct': 72}))

    def tearDown(self):
        self.tmp.cleanup()

    def run_handoff(self, *args, **env_extra):
        env = dict(os.environ, PATH=f'{self.bin}:{os.environ["PATH"]}', ORCA_LOG=str(self.log),
                   ORCA_SEND=str(self.dir / 'send-mode'),
                   XDG_STATE_HOME=str(self.state), CLAUDE_CODE_SESSION_ID='s1', CLAUDE_EFFORT='high',
                   ORCA_TERMINAL_HANDLE='term_old', **env_extra)
        return subprocess.run([sys.executable, str(HANDOFF), '--order', str(self.order), *args],
                              capture_output=True, text=True, env=env, cwd=self.wt)

    def calls(self):
        return [json.loads(l) for l in self.log.read_text().splitlines()] if self.log.exists() else []

    def test_hands_off_with_this_sessions_settings(self):
        p = self.run_handoff()
        self.assertEqual(p.returncode, 0, p.stderr)
        calls = self.calls()
        create = next(c for c in calls if c[:2] == ['terminal', 'create'])
        launch = create[create.index('--command') + 1]
        self.assertIn('claude --model opus --effort high --dangerously-skip-permissions', launch)
        self.assertEqual(create[create.index('--title') + 1], '#896 API v1 conductor (cont.)')
        send = next(c for c in calls if c[:2] == ['terminal', 'send'])
        prompt = send[send.index('--text') + 1]
        self.assertTrue(prompt.startswith(f'/conductor-claude Read {self.order.resolve()}'))
        self.assertIn('72% context', prompt)
        rename = next(c for c in calls if c[:2] == ['terminal', 'rename'])
        self.assertEqual(rename[rename.index('--title') + 1], '#896 API v1 conductor (handed off)')
        rows = [json.loads(l) for l in (self.wt / '.conductor/handoffs.jsonl').read_text().splitlines()]
        self.assertEqual([(r['status'], r['to_terminal']) for r in rows], [('created', 'term_new'), ('done', 'term_new')])
        marker = json.loads((self.state / 'conductor/context/s1.handoff.json').read_text())
        self.assertEqual((marker['status'], marker['to_terminal']), ('done', 'term_new'))
        self.assertEqual(self.run_handoff().returncode, 4)  # already handed off

    def test_failed_send_is_not_a_handoff_and_a_rerun_reuses_the_terminal(self):
        (self.dir / 'send-mode').write_text('reject')
        self.assertEqual(self.run_handoff().returncode, 5)
        marker = json.loads((self.state / 'conductor/context/s1.handoff.json').read_text())
        self.assertEqual(marker['status'], 'pending')
        (self.dir / 'send-mode').write_text('noturn')
        self.assertEqual(self.run_handoff().returncode, 5)
        (self.dir / 'send-mode').write_text('ok')
        self.assertEqual(self.run_handoff().returncode, 0)
        calls = self.calls()
        self.assertEqual(sum(c[:2] == ['terminal', 'create'] for c in calls), 1)
        sends = [c for c in calls if c[:2] == ['terminal', 'send']]
        self.assertNotIn('--retry-request', sends[0])
        self.assertEqual(sends[-1][sends[-1].index('--retry-request') + 1], 'req1')

    def test_concurrent_handoffs_start_one_successor(self):
        env = dict(os.environ, PATH=f'{self.bin}:{os.environ["PATH"]}', ORCA_LOG=str(self.log), ORCA_SLOW='1',
                   XDG_STATE_HOME=str(self.state), CLAUDE_CODE_SESSION_ID='s1', ORCA_TERMINAL_HANDLE='term_old')
        procs = [subprocess.Popen([sys.executable, str(HANDOFF), '--order', str(self.order)], env=env, cwd=self.wt,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for _ in range(2)]
        self.assertEqual(sorted(p.wait() for p in procs), [0, 4])
        self.assertEqual(sum(c[:2] == ['terminal', 'create'] for c in self.calls()), 1)

    def test_lost_response_retries_the_same_request_and_prompt(self):
        (self.dir / 'send-mode').write_text('lost')
        self.assertEqual(self.run_handoff().returncode, 5)
        state = self.state / 'conductor/context/s1.json'
        state.write_text(json.dumps(dict(json.loads(state.read_text()), pct=73)))
        (self.dir / 'send-mode').write_text('ok')
        self.assertEqual(self.run_handoff().returncode, 0)
        sends = [c for c in self.calls() if c[:2] == ['terminal', 'send']]
        self.assertEqual(sends[1][sends[1].index('--retry-request') + 1], 'req-lost')
        self.assertEqual(sends[0][sends[0].index('--text') + 1], sends[1][sends[1].index('--text') + 1])

    def test_unconfirmed_pending_terminal_blocks_a_new_one(self):
        (self.dir / 'send-mode').write_text('noturn')
        self.assertEqual(self.run_handoff().returncode, 5)
        self.assertEqual(self.run_handoff(ORCA_SHOW_FAIL='1').returncode, 5)
        self.assertEqual(sum(c[:2] == ['terminal', 'create'] for c in self.calls()), 1)

    def test_every_permission_mode_is_explicit(self):
        for mode, flag in (('manual', '--permission-mode manual'), ('default', '--permission-mode default')):
            p = self.run_handoff('--permission-mode', mode, '--dry-run')
            self.assertIn(flag, json.loads(p.stdout)['launch'])

    def test_short_order_is_refused(self):
        self.order.write_text('todo\n')
        self.assertEqual(self.run_handoff().returncode, 2)
        self.assertEqual(self.calls(), [])

    def test_orca_not_ready_prints_the_manual_command(self):
        p = self.run_handoff(ORCA_STATE='starting')
        self.assertEqual(p.returncode, 3)
        self.assertIn('claude --model opus', p.stderr)
        self.assertFalse(any(c[:2] == ['terminal', 'create'] for c in self.calls()))

    def test_chain_guard(self):
        import time
        rows = [json.dumps({'epoch': int(time.time()) - 60 * i}) for i in range(3)]
        (self.wt / '.conductor/handoffs.jsonl').write_text('\n'.join(rows) + '\n')
        self.assertEqual(self.run_handoff().returncode, 4)
        self.assertEqual(self.run_handoff('--force').returncode, 0)


class InstallTest(unittest.TestCase):
    def test_install_is_idempotent_and_keeps_other_hooks(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / 'claude'
            cfg.mkdir()
            other = {'matcher': '*', 'hooks': [{'type': 'command', 'command': 'orca-hook'},
                                               {'type': 'command', 'command': 'python3 /opt/co/context-watch.py --audit'}]}
            (cfg / 'settings.json').write_text(json.dumps({'model': 'opus', 'hooks': {'PostToolUse': [other]}}))
            env = dict(os.environ, CLAUDE_CONFIG_DIR=str(cfg))
            run = lambda *a: subprocess.run([sys.executable, str(INSTALL), '--bin-dir', str(Path(tmp) / 'bin'), *a],
                                            capture_output=True, text=True, env=env)
            self.assertEqual(run().returncode, 0)
            first = (cfg / 'settings.json').read_text()
            self.assertEqual(run().returncode, 0)
            self.assertEqual(first, (cfg / 'settings.json').read_text())
            s = json.loads(first)
            self.assertEqual(s['hooks']['PostToolUse'][0], other)
            self.assertIn('context-watch.py', s['hooks']['PostToolUse'][1]['hooks'][0]['command'])
            self.assertIn('context-watch.py', s['hooks']['Stop'][0]['hooks'][0]['command'])
            self.assertTrue((Path(tmp) / 'bin/conductor-handoff').is_symlink())
            self.assertEqual(run('--uninstall').returncode, 0)
            s = json.loads((cfg / 'settings.json').read_text())
            self.assertEqual(s['hooks'], {'PostToolUse': [other]})
            self.assertFalse((Path(tmp) / 'bin/conductor-handoff').exists())

    def test_copy_install_hooks_only_the_prefix_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            home, prefix = Path(tmp) / 'home', Path(tmp) / 'claude config'
            (home / '.claude').mkdir(parents=True)
            env = dict(os.environ, HOME=str(home))
            env.pop('CLAUDE_CONFIG_DIR', None)
            subprocess.run(['bash', str(ROOT / 'install.sh'), '--prefix', str(prefix), '--bin', str(Path(tmp) / 'bin')],
                           check=True, capture_output=True, text=True, env=env)
            s = json.loads((prefix / 'settings.json').read_text())
            self.assertIn(str(prefix / 'conductor/context-watch.py'), s['hooks']['Stop'][0]['hooks'][0]['command'])
            self.assertFalse((home / '.claude/settings.json').exists())
            stop = s['hooks']['Stop'][0]['hooks'][0]['command']
            p = subprocess.run(['bash', '-c', stop], input=json.dumps({'hook_event_name': 'Stop'}),
                               capture_output=True, text=True, env=env)
            self.assertEqual((p.returncode, p.stderr), (0, ''))


if __name__ == '__main__':
    unittest.main()
