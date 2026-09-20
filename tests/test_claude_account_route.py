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

if __name__=='__main__': unittest.main()
