import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('linker', Path(__file__).resolve().parents[1] / 'scripts/link-personal-skills.py')
linker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(linker)

class SkillInstallTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.home_patch = patch.object(Path, 'home', return_value=self.home)
        self.env_patch = patch.object(linker.os, 'environ', {})
        self.home_patch.start(); self.env_patch.start()
    def tearDown(self):
        self.env_patch.stop(); self.home_patch.stop(); self.tmp.cleanup()
    def test_install_and_idempotence(self):
        linker.main()
        claude = self.home / '.claude/skills/conductor'
        codex = self.home / '.codex/skills/conductor'
        self.assertTrue(claude.is_symlink())
        self.assertFalse(codex.is_symlink())
        self.assertIn(str(claude.resolve() / 'SKILL.md'), (codex / 'SKILL.md').read_text())
        self.assertNotIn('## Report design contract', (codex / 'SKILL.md').read_text())
        before = list((self.home / '.local/state/conductor-link').iterdir())
        linker.main()
        self.assertEqual(before, list((self.home / '.local/state/conductor-link').iterdir()))
    def test_mobile_install_shares_canonical_references(self):
        linker.main('mobile-app-testing')
        claude = self.home / '.claude/skills/mobile-app-testing'
        codex = self.home / '.codex/skills/mobile-app-testing'
        source = Path(linker.__file__).resolve().parents[1] / 'skills/mobile-app-testing'
        self.assertTrue((claude / 'references/device-operations.md').samefile(source / 'references/device-operations.md'))
        self.assertIn(str(source / 'SKILL.md'), (codex / 'SKILL.md').read_text())
        self.assertTrue((codex / 'agents/openai.yaml').samefile(source / 'agents/openai.yaml'))
        before = list((self.home / '.local/state/conductor-link').iterdir())
        linker.main('mobile-app-testing')
        self.assertEqual(before, list((self.home / '.local/state/conductor-link').iterdir()))

    def test_copy_installer_includes_mobile_references(self):
        import subprocess
        root = Path(linker.__file__).resolve().parents[1]
        prefix, bindir = self.home / 'copy', self.home / 'bin'
        subprocess.run(['bash', str(root / 'install.sh'), '--prefix', str(prefix), '--bin', str(bindir)], check=True, capture_output=True, text=True)
        self.assertTrue((prefix / 'skills/mobile-app-testing/references/evidence.md').is_file())
        self.assertTrue((prefix / 'skills/conductor/../mobile-app-testing/SKILL.md').is_file())

    def test_core_install_identity_references_and_idempotence(self):
        linker.main('conductor-core')
        source = Path(linker.__file__).resolve().parents[1] / 'skills/conductor-core'
        claude = self.home / '.claude/skills/conductor-core'
        codex = self.home / '.codex/skills/conductor-core'
        self.assertTrue((claude / 'SKILL.md').samefile(source / 'SKILL.md'))
        self.assertFalse(codex.is_symlink())
        bootstrap = (codex / 'SKILL.md').read_text()
        self.assertEqual(bootstrap.splitlines()[1], 'name: conductor-core')
        self.assertIn(str(source / 'SKILL.md'), bootstrap)
        self.assertTrue((codex / 'agents/openai.yaml').samefile(source / 'agents/openai.yaml'))
        # The bootstrap resolves references from source, not its personal entry directory.
        self.assertTrue((source / '../conductor/SKILL.md').is_file())
        before = list((self.home / '.local/state/conductor-link').iterdir())
        linker.main('conductor-core')
        self.assertEqual(before, list((self.home / '.local/state/conductor-link').iterdir()))

    def test_copy_installer_core_shared_contract_survives_relocation(self):
        import re
        import subprocess
        root = Path(linker.__file__).resolve().parents[1]
        prefix, bindir = self.home / 'copy', self.home / 'bin'
        subprocess.run(['bash', str(root / 'install.sh'), '--prefix', str(prefix), '--bin', str(bindir)], check=True, capture_output=True, text=True)
        core = prefix / 'skills/conductor-core/SKILL.md'
        self.assertTrue(core.is_file())
        self.assertTrue((core.parent / 'agents/openai.yaml').is_file())
        links = re.findall(r'\]\((\.\./[^)]+)\)', core.read_text())
        self.assertTrue(links)
        for link in links:
            self.assertTrue((core.parent / link).is_file(), link)
        shared = core.parent / '../conductor/SKILL.md'
        self.assertIn(str(prefix / 'conductor/conductor-report.py'), shared.read_text())
        self.assertNotIn('${CLAUDE_PLUGIN_ROOT}/scripts', shared.read_text())

    def test_preserves_existing_install(self):
        original = self.home / '.codex/skills/conductor'
        original.mkdir(parents=True)
        (original / 'unique.txt').write_text('keep me')
        linker.main()
        backups = list((self.home / '.local/state/conductor-link').glob('*/codex/unique.txt'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), 'keep me')
        self.assertEqual((backups[0].parents[1].stat().st_mode & 0o777), 0o700)
    def test_rolls_back_both_entries_on_failure(self):
        for family in ['.claude', '.codex']:
            p = self.home / family / 'skills/conductor'
            p.mkdir(parents=True); (p / 'original').write_text(family)
        original = Path.symlink_to
        def fail_agents(p, *a, **kw):
            if p.name == 'agents':
                raise OSError('injected second-target failure')
            return original(p, *a, **kw)
        with patch.object(Path, 'symlink_to', fail_agents):
            with self.assertRaises(OSError): linker.main()
        for family in ['.claude', '.codex']:
            p = self.home / family / 'skills/conductor'
            self.assertFalse(p.is_symlink())
            self.assertEqual((p / 'original').read_text(), family)

if __name__ == '__main__': unittest.main()
