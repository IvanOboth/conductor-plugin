"""Account routing regression checks using a fake CLI, without credentials."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class AccountRouteTests(unittest.TestCase):
    def test_routes(self):
        launchers = [ROOT / 'bin/ask-claude']
        installed = os.environ.get('ORCA_TEST_INSTALLED_HELPERS')
        if installed:
            launchers.append(Path(installed) / 'ask-claude')
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / 'orca'
            root.mkdir()
            binary = base / 'claude'
            binary.write_text('#!/usr/bin/env python3\nimport os\nprint(os.environ.get("CLAUDE_CONFIG_DIR", "HOST_DEFAULT"))\n')
            binary.chmod(0o755)
            env = {k:v for k,v in os.environ.items() if k != 'CLAUDE_CONFIG_DIR'}
            env.update(XDG_CONFIG_HOME=tmp, PATH=tmp+os.pathsep+env['PATH'])
            def check(expected, code=0, override=None, args=()):
                for launcher in launchers:
                    e = dict(env)
                    if override: e['CLAUDE_CONFIG_DIR'] = override
                    p = subprocess.run(['bash',str(launcher),*args,'probe'],env=e,text=True,capture_output=True)
                    self.assertEqual(p.returncode,code,p.stderr)
                    self.assertIn(expected,p.stdout if code==0 else p.stderr)
            check('HOST_DEFAULT')
            (root/'orca-profile-index.json').write_text(json.dumps({'activeProfileId':'test'}))
            profile=root/'profiles/test'; profile.mkdir(parents=True)
            def select(account):
                (profile/'orca-data.json').write_text(json.dumps({'settings':{'activeClaudeManagedAccountIdsByRuntime':{'host':account},'claudeManagedAccounts':[{'id':a,'managedAuthRuntime':'host','managedAuthPath':str(root/'claude-accounts'/a/'auth')} for a in ('first','second')]}}))
            for account in ('first','second'):
                home=root/'claude-accounts'/account/'auth'; home.mkdir(parents=True)
                (home/'.credentials.json').write_text('{}')
                select(account); check(str(home))
            check('HOST_DEFAULT', args=('--keep-env',))
            select('first')
            (root/'claude-accounts/first/auth/.credentials.json').unlink()
            check('has no credentials',2)
            select('missing'); check('not a registered host account',2)
            check('/explicit/home',override='/explicit/home')
            select(None); check('HOST_DEFAULT')
            select('../escape'); check('invalid selected account',2)
            (root/'orca-profile-index.json').write_text('broken')
            check('cannot resolve Orca account',2)
            print('PASS: requested launchers; no Orca, selected account, switch, explicit override, host default, missing auth, invalid account, corrupt profile')

    def test_orca_1_4_225_selected_host_pointer_and_profile_home(self):
        launchers = [ROOT / 'bin/ask-claude']
        installed = os.environ.get('ORCA_TEST_INSTALLED_HELPERS')
        if installed:
            launchers.append(Path(installed) / 'ask-claude')
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / 'orca'
            profiles = root / 'claude-profiles'
            profiles.mkdir(parents=True)
            binary = base / 'claude'
            binary.write_text('#!/usr/bin/env python3\nimport os\nprint(os.environ.get("CLAUDE_CONFIG_DIR", "HOST_DEFAULT"))\n')
            binary.chmod(0o755)
            env = {k: v for k, v in os.environ.items() if k != 'CLAUDE_CONFIG_DIR'}
            env.update(XDG_CONFIG_HOME=tmp, PATH=tmp + os.pathsep + env['PATH'])

            def check(expected, code=0, override=None, args=()):
                for launcher in launchers:
                    e = dict(env)
                    if override:
                        e['CLAUDE_CONFIG_DIR'] = override
                    p = subprocess.run(['bash', str(launcher), *args, 'probe'], env=e, text=True, capture_output=True)
                    self.assertEqual(p.returncode, code, p.stderr)
                    self.assertIn(expected, p.stdout if code == 0 else p.stderr)

            # 1. Live Orca 1.4.225+ claude-profiles/selected-host pointer
            pointer = profiles / 'selected-host'
            first_home = profiles / 'acct-first' / 'home'
            second_home = profiles / 'acct-second' / 'home'
            for h in (first_home, second_home):
                h.mkdir(parents=True)
                (h / '.credentials.json').write_text('{}')

            pointer.write_text(f'{first_home}\n')
            check(str(first_home.resolve()))

            pointer.write_text(str(second_home))
            check(str(second_home.resolve()))

            # Override and --keep-env still bypass pointer
            check('/explicit/home', override='/explicit/home')
            check('HOST_DEFAULT', args=('--keep-env',))

            # Empty pointer means system default
            pointer.write_text('   \n')
            check('HOST_DEFAULT')

            # 2. Traversal / escape / malformed pointers rejected (exit 2)
            outside = base / 'outside' / 'home'
            outside.mkdir(parents=True)
            (outside / '.credentials.json').write_text('{}')

            pointer.write_text('../escape')
            check('cannot resolve Orca account', 2)

            pointer.write_text(str(outside))
            check('escapes Orca claude-profiles', 2)

            pointer.write_text(f'{profiles}/acct-first/../acct-second/home')
            check('invalid selected-host pointer', 2)

            pointer.write_text(f'{profiles}/acct-first/auth')
            check('claude-profiles/<id>/home', 2)

            dot_home = profiles / '.hidden' / 'home'
            dot_home.mkdir(parents=True)
            (dot_home / '.credentials.json').write_text('{}')
            pointer.write_text(str(dot_home))
            check('invalid selected account', 2)

            symlink_home = profiles / 'symlinked' / 'home'
            symlink_home.parent.mkdir(parents=True)
            symlink_home.symlink_to(outside)
            pointer.write_text(str(symlink_home))
            check('escapes Orca claude-profiles', 2)

            # 3. Missing .credentials.json in pointed home rejected (exit 2)
            (first_home / '.credentials.json').unlink()
            pointer.write_text(str(first_home))
            check('has no credentials', 2)

            # 4. Fallback to orca-data.json resolves claude-profiles/<id>/home even without legacy claude-accounts auth
            pointer.unlink()
            (root / 'orca-profile-index.json').write_text(json.dumps({'activeProfileId': 'test'}))
            profile = root / 'profiles' / 'test'
            profile.mkdir(parents=True)
            (profile / 'orca-data.json').write_text(json.dumps({
                'settings': {
                    'activeClaudeManagedAccountIdsByRuntime': {'host': 'acct-second'},
                    'claudeManagedAccounts': [
                        {
                            'id': 'acct-second',
                            'managedAuthRuntime': 'host',
                            'managedAuthPath': str(root / 'claude-accounts' / 'acct-second' / 'auth'),
                        },
                        {
                            'id': 'acct-first',
                            'managedAuthRuntime': 'host',
                            'managedAuthPath': str(root / 'claude-accounts' / 'acct-first' / 'auth'),
                        },
                    ],
                }
            }))
            # Legacy claude-accounts/acct-second/auth does NOT exist, but claude-profiles/acct-second/home/.credentials.json does
            check(str(second_home))

            # If neither profile home nor legacy auth has .credentials.json, exit 2
            (profile / 'orca-data.json').write_text(json.dumps({
                'settings': {
                    'activeClaudeManagedAccountIdsByRuntime': {'host': 'acct-first'},
                    'claudeManagedAccounts': [
                        {
                            'id': 'acct-first',
                            'managedAuthRuntime': 'host',
                            'managedAuthPath': str(root / 'claude-accounts' / 'acct-first' / 'auth'),
                        },
                    ],
                }
            }))
            check('has no credentials', 2)

if __name__=='__main__': unittest.main()
