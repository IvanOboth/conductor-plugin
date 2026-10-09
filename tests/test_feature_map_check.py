import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    'fmc', Path(__file__).resolve().parents[1] / 'skills/verify-skill-create/scripts/feature_map_check.py')
fmc = importlib.util.module_from_spec(spec)
sys.modules['fmc'] = fmc
spec.loader.exec_module(fmc)

FEATURE = """---
id: {id}
sources:
  - app/**/{area}/**   # trailing comments are ignored
---

# {id}

What the user does.

## Sub-features

- `x` does x.

## How to get to it (user POV)

- Sidebar.

## Driving it with verify-demo

Preconditions:

- Signed in.

## Gotchas

- None.
"""


def git(repo, *args):
    subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True,
                   env={'GIT_AUTHOR_NAME': 't', 'GIT_AUTHOR_EMAIL': 't@t', 'GIT_COMMITTER_NAME': 't',
                        'GIT_COMMITTER_EMAIL': 't@t', 'PATH': '/usr/bin:/bin'})


class FeatureMapCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, 'init', '-q', '-b', 'main')
        for route in ['app/(g)/sales/page.tsx', 'app/(g)/sales/[id]/page.tsx', 'app/stock/page.tsx',
                      'app/test-page/page.tsx']:
            p = self.repo / route
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('export default 1\n')
        self.map = self.repo / 'skill/features'
        self.map.mkdir(parents=True)
        (self.map / 'map.json').write_text(json.dumps({
            'repo_root': '../..', 'harness': 'verify-demo',
            'route_globs': ['app/**/page.tsx'], 'route_ignore': ['app/test-*/**']}))
        (self.map / 'sales.md').write_text(FEATURE.format(id='sales', area='sales'))
        (self.map / 'stock.md').write_text(FEATURE.format(id='stock', area='stock'))
        (self.map / 'README.md').write_text('- [Sales](./sales.md)\n- [Stock](./stock.md)\n')
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-qm', 'base')

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_map_covers_routes_and_skips_ignored(self):
        result = fmc.check(self.map, None)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['summary'], {'version': fmc.VERSION, 'features': 2, 'journeys': 0, 'routes': 3, 'covered_routes': 3})

    def test_glob_brackets_are_literal_and_double_star_skips_groups(self):
        rx = fmc.glob_to_regex('app/**/sales/[id]/*.tsx')
        self.assertTrue(rx.match('app/(g)/sales/[id]/page.tsx'))
        self.assertFalse(rx.match('app/(g)/sales/7/page.tsx'))

    def test_index_and_contract_errors(self):
        (self.map / 'orphan.md').write_text(FEATURE.format(id='wrong', area='x').replace('## Gotchas', '## Notes'))
        errors = fmc.check(self.map, None)['errors']
        self.assertIn('orphan.md is not listed in README.md', errors)
        self.assertTrue(any("front matter id is 'wrong'" in e for e in errors))
        self.assertTrue(any('H2 sections are' in e for e in errors))

    def test_diff_flags_touched_feature_and_fails_new_uncovered_route(self):
        (self.repo / 'app/(g)/sales/page.tsx').write_text('export default 2\n')
        new = self.repo / 'app/reports/page.tsx'
        new.parent.mkdir(parents=True)
        new.write_text('export default 3\n')
        result = fmc.check(self.map, 'main')
        self.assertEqual([t['feature'] for t in result['touched_features']], ['sales.md'])
        self.assertEqual(result['new_uncovered_routes'], ['app/reports/page.tsx'])
        self.assertEqual(fmc.main([str(self.map), '--base', 'main']), 1)

    def test_updating_the_feature_file_clears_the_touched_warning(self):
        (self.repo / 'app/(g)/sales/page.tsx').write_text('export default 2\n')
        (self.map / 'sales.md').write_text(FEATURE.format(id='sales', area='sales') + '- New gotcha.\n')
        result = fmc.check(self.map, 'main')
        self.assertEqual(result['touched_features'], [])
        self.assertEqual(fmc.main([str(self.map), '--base', 'main']), 0)


    def test_touched_feature_fails_until_updated_or_acknowledged(self):
        (self.repo / 'app/(g)/sales/page.tsx').write_text('export default 2\n')
        self.assertEqual(fmc.main([str(self.map), '--base', 'main']), 1)
        self.assertEqual(fmc.main([str(self.map), '--base', 'main', '--allow-unchanged', 'sales']), 0)
        body = self.repo / 'pr.md'
        body.write_text('Refactor only.\n\nmap unchanged: `sales` — same screens and labels\n')
        self.assertEqual(fmc.main([str(self.map), '--base', 'main', '--allow-unchanged-from', str(body)]), 0)


    def test_rename_between_features_touches_both(self):
        (self.repo / 'app/(g)/sales/stock').mkdir()
        git(self.repo, 'mv', 'app/stock/page.tsx', 'app/(g)/sales/stock/page.tsx')
        (self.map / 'sales.md').write_text(FEATURE.format(id='sales', area='sales') + '- Stock moved here.\n')
        result = fmc.check(self.map, 'main')
        self.assertEqual([t['feature'] for t in result['touched_features']], ['stock.md'])

    def test_non_ascii_route_is_seen(self):
        p = self.repo / 'app/報告/page.tsx'
        p.parent.mkdir(parents=True)
        p.write_text('export default 4\n')
        self.assertEqual(fmc.check(self.map, 'main')['new_uncovered_routes'], ['app/報告/page.tsx'])


    def journey(self, features='[sales, stock]'):
        return (f"---\nid: sell-and-restock\npersona: Rep\nsurface: web\nfeatures: {features}\nsources:\n  - app/**/sales/**\n---\n\n"
                "# Sell and restock\n\nJob.\n\n## Goal and context\n\nx\n\n## Steps the user expects\n\n1. x\n\n"
                "## Path in the app\n\n1. x\n\n## Driving it with verify-demo\n\nPreconditions: x\n\n## Gotchas\n\n- x\n")

    def test_journeys_are_validated_indexed_and_follow_their_sources(self):
        (self.map / 'journeys').mkdir()
        (self.map / 'journeys/sell-and-restock.md').write_text(self.journey('[sales, nowhere]'))
        errors = fmc.check(self.map, None)['errors']
        self.assertIn('journeys/sell-and-restock.md is not listed in README.md', errors)
        self.assertTrue(any("lists feature 'nowhere'" in e for e in errors))
        (self.map / 'journeys/sell-and-restock.md').write_text(self.journey())
        with (self.map / 'README.md').open('a') as fh:
            fh.write('- [Sell and restock](./journeys/sell-and-restock.md)\n')
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-qm', 'journey')
        self.assertEqual(fmc.check(self.map, None)['errors'], [])
        (self.repo / 'app/(g)/sales/page.tsx').write_text('export default 5\n')
        (self.map / 'sales.md').write_text(FEATURE.format(id='sales', area='sales') + '- Changed.\n')
        result = fmc.check(self.map, 'main')
        self.assertEqual([t['feature'] for t in result['touched_features']], ['journeys/sell-and-restock.md'])


if __name__ == '__main__':
    unittest.main()
