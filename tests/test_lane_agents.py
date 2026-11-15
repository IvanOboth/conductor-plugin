"""The five pinned lane agents carry the unattended-lane paragraph (bench-factory#686).

Lanes ended their turns on a summary while work was still owed. Orders are told to end with a fixed
paragraph (skills/conductor/SKILL.md, "The loop", step 2); the pinned lane agents carry the same text
in their system prompt, so a lane gets it even when an order leaves it out.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
LANES = ['exec-lane', 'bulk-lane', 'design-lane', 'verify-lane', 'write-lane']
FIRST_SENTENCE = 'A standing instruction from the user, the person you are working for.'


def skill_paragraph():
    text = (ROOT / 'skills/conductor/SKILL.md').read_text()
    match = re.search(r'^> (' + re.escape(FIRST_SENTENCE) + r'.*)$', text, re.MULTILINE)
    if match is None:
        raise AssertionError('skills/conductor/SKILL.md no longer quotes the unattended-lane paragraph')
    return match.group(1).strip()


def agent_body(name):
    text = (ROOT / 'agents' / f'{name}.md').read_text()
    parts = text.split('\n---\n', 1)
    if not text.startswith('---\n') or len(parts) != 2:
        raise AssertionError(f'agents/{name}.md has no front matter')
    return parts[1]


class LaneAgentTests(unittest.TestCase):
    def test_skill_paragraph_is_the_full_text(self):
        paragraph = skill_paragraph()
        self.assertTrue(paragraph.endswith('confirmation on risky or destructive actions.'))

    def test_each_lane_agent_body_carries_the_paragraph_verbatim(self):
        paragraph = skill_paragraph()
        for name in LANES:
            with self.subTest(agent=name):
                body = agent_body(name)
                self.assertIn('## How your turns end', body)
                self.assertEqual(body.count(paragraph), 1)


if __name__ == '__main__':
    unittest.main()
