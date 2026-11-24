"""Conductor routing and structure (IvanOboth/conductor-plugin#59; Ivan, 20 Nov 2026).

GPT-6.2 Sol (`gpt-6.2-sol`) replaced GPT-6.1 Sol in every role (bench-factory#1176: 15 of 20 known review findings
caught against 6 of 20, same price), and Gemini 4 Neon (`ask-gemini -m gemini-4-neon-high --no-fallback`) became the
reviewer when Sol cannot run, before the Opus 5.5 fresh-context fallback. The conductor skill was cut from 116.7 KB
to one routing section plus cold `references/` files, so it must stay small and every reference it links must exist.
The browser-evidence marker block stays in SKILL.md: bench-factory's tools/browser-evidence/install.py copies it.
"""
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/conductor/SKILL.md'
HISTORY_FILE = 'skills/conductor/references/routing-history.md'
MAX_SKILL_BYTES = 65_000

OLD_SOL = re.compile(r'gpt-6\.1-sol|GPT-6\.1 Sol')
# Wording that prescribes a model for a lane: an invocation, a table model cell or a role/effort clause.
PRESCRIBES_OLD_SOL = [
    re.compile(r'-m\s+gpt-6\.1-sol'),
    re.compile(r'gpt-6\.1-sol\s+(--effort|-c\s+model_reasoning_effort)'),
    re.compile(r'model[\'"]?\s*[:=]\s*[\'"]?gpt-6\.1-sol'),
    re.compile(r'\|\s*`?gpt-6\.1-sol`?\s*\|'),
    re.compile(r'GPT-6\.1 Sol,? (at )?\(?`(high|xhigh|max)`\)?(?! scored)'),
    re.compile(r'GPT-6\.1 Sol (is the only GPT model|takes|reviews|owns|runs)'),
]
# A line that still names GPT-6.1 Sol must read as dated history.
HISTORY_MARKER = re.compile(
    r'20 Nov 2026|29 Sep 2026|17 Nov 2026|replaced|replaces|measured on|retired|history|scored|carried over|'
    r'bench-factory#1176|refused')
EPIC_CLOSE_READERS = 'Readers left behind: search the whole tree for anything that still decides this by itself'
LINK = re.compile(r'\]\(([^)\s]+)\)')


def active_files():
    names = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '--cached', '--others', '--exclude-standard',
                            'skills', 'agents', 'team-config', 'README.md', '.claude-plugin', 'bin'],
                           capture_output=True, text=True, check=True).stdout.split()
    for name in sorted(set(names)):
        path = ROOT / name
        if name == HISTORY_FILE or path.is_symlink() or not path.is_file():
            continue
        if path.suffix not in ('.md', '.json', '.yaml', '.yml', '') and not name.startswith('bin/'):
            continue
        yield name, path.read_text(errors='replace')


def local_links(path):
    for target in LINK.findall(path.read_text()):
        if re.match(r'^[a-z][a-z0-9+.-]*:', target) or target.startswith('#'):
            continue
        yield target, (path.parent / target.split('#', 1)[0]).resolve()


class ActiveRoutingTests(unittest.TestCase):
    def test_no_active_file_prescribes_gpt_6_1_sol(self):
        hits = []
        for name, text in active_files():
            for number, line in enumerate(text.splitlines(), 1):
                if not OLD_SOL.search(line):
                    continue
                if any(p.search(line) for p in PRESCRIBES_OLD_SOL):
                    hits.append(f'{name}:{number}: prescribes GPT-6.1 Sol')
                elif not HISTORY_MARKER.search(line):
                    hits.append(f'{name}:{number}: names GPT-6.1 Sol without a dated history marker')
        self.assertEqual(hits, [])

    def test_the_old_clauses_are_caught(self):
        for old in ('ask-codex -m gpt-6.1-sol --effort high --context work-order.md',
                    '| Runtime mechanics and computer-use verification | gpt-6.1-sol | high |',
                    '**GPT-6.1 Sol (`gpt-6.1-sol`) at `high` is the only GPT model for reviewing',
                    'Default runtime execution to **gpt-6.1-sol** at `high`. Pass `-m gpt-6.1-sol`'):
            line_ok = (not any(p.search(old) for p in PRESCRIBES_OLD_SOL)) and HISTORY_MARKER.search(old)
            self.assertFalse(line_ok, old)
        kept = 'GPT-6.2 Sol (20 Nov 2026) replaced GPT-6.1 Sol in every role'
        self.assertFalse(any(p.search(kept) for p in PRESCRIBES_OLD_SOL))
        self.assertTrue(HISTORY_MARKER.search(kept))

    def test_conductor_routes_to_gpt_6_2_sol_and_gemini(self):
        text = re.sub(r'\s+', ' ', SKILL.read_text())
        self.assertIn('ask-codex -m gpt-6.2-sol --effort high', text)
        self.assertIn('ask-gemini -m gemini-4-neon-high --no-fallback', text)
        self.assertIn('`cross-family (Gemini)`', text)
        self.assertIn('`same-model, fresh context`', text)
        self.assertRegex(text, r'Writing \(high stakes\)\s*\|\s*Gemini 4 Neon')
        self.assertIn('no personal-data or vault restrictions', text)
        self.assertNotRegex(text, r'vault runs skip Gemini|client personal-data runs[^|.\n]*skip Gemini|never on client personal-data|never client personal-data')
        self.assertRegex(text, r'[Ss]hadow review \(trial\)')

    def test_no_active_file_restricts_gemini_on_client_personal_data(self):
        banned = re.compile(
            r'client personal-data runs[^|\n]*skip Gemini|'
            r'never on client personal-data|'
            r'never client personal-data|'
            r'never runs on client personal-data|'
            r'never for client personal-data|'
            r'holds no client personal data \(bench-factory#428\)|'
            r'client personal-data run, bench-factory#428|'
            r'Client personal-data runs \(bench-factory#428\) stay Claude-only',
            re.IGNORECASE,
        )
        hits = []
        for name, text in active_files():
            for number, line in enumerate(text.splitlines(), 1):
                if banned.search(line):
                    hits.append(f'{name}:{number}: {line.strip()}')
        self.assertEqual(hits, [])

    def test_conductor_gemini_profile_contract(self):
        gemini_skill = ROOT / 'skills/conductor-gemini/SKILL.md'
        self.assertTrue(gemini_skill.is_file(), 'skills/conductor-gemini/SKILL.md missing')
        text = gemini_skill.read_text()
        self.assertIn('name: conductor-gemini', text)
        self.assertIn('profile: conductor-gemini', text)
        self.assertIn('invoke_subagent', text)
        self.assertIn('run_workflow', text)
        self.assertIn('ask-claude', text)
        self.assertIn('ask-codex -m gpt-6.2-sol --effort high', text)
        self.assertIn('~/bin/report-link.py', text)
        self.assertIn('A standing instruction from the user, the person you are working for.', text)
        self.assertIn('The 3-layer stack', text)
        self.assertIn('../council/SKILL.md', text)
        self.assertIn('[Conductor Gemini](../conductor-gemini/SKILL.md)', SKILL.read_text())

    def test_council_skill_contract(self):
        council_skill = ROOT / 'skills/council/SKILL.md'
        protocol = ROOT / 'skills/council/references/peer-review-protocol.md'
        self.assertTrue(council_skill.is_file(), 'skills/council/SKILL.md missing')
        self.assertTrue(protocol.is_file(), 'skills/council/references/peer-review-protocol.md missing')
        text = council_skill.read_text()
        self.assertIn('name: council', text)
        self.assertIn('Mode A', text)
        self.assertIn('Mode B', text)
        self.assertIn('ask-gemini -m gemini-4-neon-high --no-fallback', text)
        self.assertIn('ask-claude --plan -m opus', text)
        self.assertIn('ask-codex -m gpt-6.2-sol --effort high', text)
        self.assertIn('Proposal A', text)
        self.assertIn('ENDORSE WITH AMENDMENTS', text)
        self.assertIn('references/peer-review-protocol.md', text)
        self.assertEqual(
            [m.start() for m in re.finditer(r'(?<!\\)\$(?=\d)', protocol.read_text())],
            [],
            'peer-review-protocol.md contains unescaped $<digit>',
        )


class ConductorStructureTests(unittest.TestCase):
    def test_skill_stays_small(self):
        size = len(SKILL.read_bytes())
        self.assertLessEqual(size, MAX_SKILL_BYTES, f'skills/conductor/SKILL.md is {size} bytes')

    def test_one_routing_section(self):
        headings = [l for l in SKILL.read_text().splitlines() if l.startswith('## ')]
        self.assertEqual(headings.count('## Model routing and lanes'), 1)
        for old in ('## Model selection contract', '## Model routing', '## The lanes'):
            self.assertFalse([h for h in headings if h == old or h.startswith(old + ' —')], old)

    def test_every_linked_reference_exists_and_none_is_orphaned(self):
        linked = set()
        for target, resolved in local_links(SKILL):
            if target.startswith('references/'):
                self.assertTrue(resolved.is_file(), target)
                linked.add(resolved.name)
        self.assertTrue(linked)
        on_disk = {p.name for p in (SKILL.parent / 'references').glob('*.md')}
        self.assertEqual(on_disk - linked, set(), 'reference files not linked from SKILL.md')

    def test_cross_references_resolve(self):
        files = [ROOT / 'README.md', *sorted((ROOT / 'team-config').glob('*.md')),
                 *sorted((ROOT / 'skills').glob('conductor*/SKILL.md')),
                 ROOT / 'skills/council/SKILL.md',
                 *sorted((ROOT / 'skills/council/references').glob('*.md')),
                 *sorted((ROOT / 'skills/conductor/references').glob('*.md'))]
        broken = [f'{f.relative_to(ROOT)}: {t}' for f in files for t, r in local_links(f) if not r.exists()]
        self.assertEqual(broken, [])

    def test_post_compaction_rules_stay_in_the_skill(self):
        text = SKILL.read_text()
        for heading in ('## Profile scope', '## Long-horizon runs', '## Orchestrator calibration',
                        '## The loop', '## Review gates', '## Closing step: run-report', '## Worked example',
                        '## What earns an agent', '## Sizing the fan-out', '## Turn-by-turn or Workflow'):
            self.assertIn(heading, text)
        self.assertIn('Review rounds: decide by round 2', text)
        self.assertIn('compact in place', text)

    def test_browser_evidence_block_stays_in_the_skill(self):
        text = SKILL.read_text()
        self.assertRegex(text, r'(?s)<!-- browser-evidence:start -->.*## Choose evidence before recording.*<!-- browser-evidence:end -->')
        for ref in (SKILL.parent / 'references').glob('*.md'):
            self.assertNotIn('<!-- browser-evidence:start -->', ref.read_text(), ref.name)

    def test_references_escape_dollar_digits(self):
        raw = [f'{p.name}:{m.start()}' for p in (SKILL.parent / 'references').glob('*.md')
               for m in re.finditer(r'(?<!\\)\$(?=\d)', p.read_text())]
        self.assertEqual(raw, [])

    def test_epic_close_checks_are_present(self):
        text = re.sub(r'\s+', ' ', SKILL.read_text())
        self.assertIn(EPIC_CLOSE_READERS, text)
        self.assertRegex(text, r'claims completeness[^.]*check that completeness table against the inventory')


if __name__ == '__main__':
    unittest.main()
