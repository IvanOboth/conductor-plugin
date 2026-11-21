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
        gemini = self.home / '.gemini/config/skills/conductor'
        self.assertTrue(claude.is_symlink())
        self.assertFalse(codex.is_symlink())
        self.assertTrue(gemini.is_symlink())
        self.assertEqual(gemini.resolve(), claude.resolve())
        self.assertIn(str(claude.resolve() / 'SKILL.md'), (codex / 'SKILL.md').read_text())
        self.assertNotIn('## Report design contract', (codex / 'SKILL.md').read_text())
        before = list((self.home / '.local/state/conductor-link').iterdir())
        linker.main()
        self.assertEqual(before, list((self.home / '.local/state/conductor-link').iterdir()))

    def test_conductor_gemini_and_gemini_config_dir_install(self):
        custom_gemini = self.home / 'custom-antigravity'
        with patch.object(linker.os, 'environ', {'GEMINI_CONFIG_DIR': str(custom_gemini)}):
            linker.main('conductor-gemini')
            source = Path(linker.__file__).resolve().parents[1] / 'skills/conductor-gemini'
            claude = self.home / '.claude/skills/conductor-gemini'
            codex = self.home / '.codex/skills/conductor-gemini'
            gemini = custom_gemini / 'skills/conductor-gemini'
            self.assertTrue(claude.is_symlink())
            self.assertTrue((claude / 'SKILL.md').samefile(source / 'SKILL.md'))
            self.assertFalse(codex.is_symlink())
            bootstrap = (codex / 'SKILL.md').read_text()
            self.assertEqual(bootstrap.splitlines()[1], 'name: conductor-gemini')
            self.assertIn(str(source / 'SKILL.md'), bootstrap)
            self.assertTrue(gemini.is_symlink())
            self.assertTrue((gemini / 'SKILL.md').samefile(source / 'SKILL.md'))
            before = list((self.home / '.local/state/conductor-link').iterdir())
            linker.main('conductor-gemini')
            self.assertEqual(before, list((self.home / '.local/state/conductor-link').iterdir()))
            # conductor-claude stays Claude-only (skips both Codex and Antigravity/Gemini).
            linker.main('conductor-claude')
            self.assertTrue((self.home / '.claude/skills/conductor-claude').is_symlink())
            self.assertFalse((self.home / '.codex/skills/conductor-claude').exists())
            self.assertFalse((custom_gemini / 'skills/conductor-claude').exists())
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

    def test_rejects_aliased_destination_roots_before_any_change(self):
        existing_claude = self.home / '.claude/skills/conductor'
        existing_claude.mkdir(parents=True)
        (existing_claude / 'sentinel.txt').write_text('untouched')
        codex_dir = self.home / '.codex'
        codex_dir.mkdir(parents=True)
        aliased_gemini = self.home / 'gemini-alias'
        aliased_gemini.symlink_to(codex_dir, target_is_directory=True)
        for env in ({'GEMINI_CONFIG_DIR': str(codex_dir)}, {'GEMINI_CONFIG_DIR': str(aliased_gemini)}):
            with patch.object(linker.os, 'environ', env):
                with self.assertRaises(SystemExit) as ctx:
                    linker.main('conductor')
                self.assertIn('aliased skill destination', str(ctx.exception))
        # Preflight failed closed before modifying or backing up anything.
        self.assertFalse(existing_claude.is_symlink())
        self.assertEqual((existing_claude / 'sentinel.txt').read_text(), 'untouched')
        self.assertFalse((self.home / '.local/state/conductor-link').exists())

    def test_cross_filesystem_backup_and_rollback_on_exdev(self):
        import errno
        real_rename = linker.os.rename

        def exdev_cross_fs_rename(src, dst):
            if Path(src).parent != Path(dst).parent:
                raise OSError(errno.EXDEV, 'Invalid cross-device link')
            return real_rename(src, dst)

        custom_gemini = self.home / 'other-fs-gemini'
        orig_dir = custom_gemini / 'skills/conductor'
        orig_dir.mkdir(parents=True)
        (orig_dir / 'keep.txt').write_text('gemini-dir')
        old_target = self.home / 'old-target'
        old_target.mkdir()
        orig_claude = self.home / '.claude/skills/conductor'
        orig_claude.parent.mkdir(parents=True)
        orig_claude.symlink_to(old_target, target_is_directory=True)

        # Backup succeeds across EXDEV for both symlink (claude) and directory (gemini).
        with patch.object(linker.os, 'environ', {'GEMINI_CONFIG_DIR': str(custom_gemini)}):
            with patch.object(linker.os, 'rename', side_effect=exdev_cross_fs_rename):
                linker.main('conductor')
        self.assertTrue((custom_gemini / 'skills/conductor').is_symlink())
        self.assertTrue(orig_claude.is_symlink())
        backups = list((self.home / '.local/state/conductor-link').glob('*/gemini/keep.txt'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), 'gemini-dir')
        claude_backups = list((self.home / '.local/state/conductor-link').glob('*/claude'))
        self.assertEqual(len(claude_backups), 1)
        self.assertTrue(claude_backups[0].is_symlink())
        self.assertEqual(claude_backups[0].resolve(), old_target.resolve())
        # No temporary staged entries left behind.
        self.assertEqual(list((custom_gemini / 'skills').glob('.conductor.conductor-link-tmp-*')), [])

        # Rollback succeeds atomically on same-FS staged copy when cross-FS copy fails midway.
        custom_gemini2 = self.home / 'other-fs-gemini-copy-fail'
        orig_dir2 = custom_gemini2 / 'skills/conductor'
        (orig_dir2 / 'sub').mkdir(parents=True)
        (orig_dir2 / 'keep2.txt').write_text('gemini-copy-fail')
        (orig_dir2 / 'sub/nested.txt').write_text('nested-intact')
        orig_claude.unlink()
        orig_claude.symlink_to(old_target, target_is_directory=True)

        def fail_copytree(src, dst, **kw):
            raise OSError('injected cross-fs copy failure')

        with patch.object(linker.os, 'environ', {'GEMINI_CONFIG_DIR': str(custom_gemini2)}):
            with patch.object(linker.os, 'rename', side_effect=exdev_cross_fs_rename):
                with patch.object(linker.shutil, 'copytree', side_effect=fail_copytree):
                    with self.assertRaises(OSError):
                        linker.main('conductor')
        self.assertFalse(orig_dir2.is_symlink())
        self.assertEqual((orig_dir2 / 'keep2.txt').read_text(), 'gemini-copy-fail')
        self.assertEqual((orig_dir2 / 'sub/nested.txt').read_text(), 'nested-intact')
        self.assertEqual(list((custom_gemini2 / 'skills').glob('.conductor.conductor-link-tmp-*')), [])
        self.assertTrue(orig_claude.is_symlink())
        self.assertEqual(orig_claude.resolve(), old_target.resolve())

        # Rollback also leaves live skill 100% intact if cross-FS staged cleanup fails midway (e.g. read-only subdir).
        custom_gemini3 = self.home / 'other-fs-gemini-cleanup-fail'
        orig_dir3 = custom_gemini3 / 'skills/conductor'
        (orig_dir3 / 'ro').mkdir(parents=True)
        (orig_dir3 / 'keep3.txt').write_text('gemini-cleanup-fail')
        (orig_dir3 / 'ro/inner.txt').write_text('inner-intact')
        orig_claude.unlink()
        orig_claude.symlink_to(old_target, target_is_directory=True)

        def partial_fail_rmtree(path):
            # Simulate partial deletion of staged before failing on a read-only subdir.
            (Path(path) / 'keep3.txt').unlink()
            raise PermissionError('read-only subdir inside staged')

        with patch.object(linker.os, 'environ', {'GEMINI_CONFIG_DIR': str(custom_gemini3)}):
            with patch.object(linker.os, 'rename', side_effect=exdev_cross_fs_rename):
                with patch.object(linker.shutil, 'rmtree', side_effect=partial_fail_rmtree):
                    with self.assertRaises(PermissionError):
                        linker.main('conductor')
        self.assertFalse(orig_dir3.is_symlink())
        self.assertEqual((orig_dir3 / 'keep3.txt').read_text(), 'gemini-cleanup-fail')
        self.assertEqual((orig_dir3 / 'ro/inner.txt').read_text(), 'inner-intact')
        self.assertTrue(orig_claude.is_symlink())
        self.assertEqual(orig_claude.resolve(), old_target.resolve())

if __name__ == '__main__': unittest.main()
