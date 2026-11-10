"""No SKILL.md body may carry a `$<digit>` that Claude Code fills with an argument.

When a skill runs as `/name some words`, Claude Code replaces `$N` (a dollar sign directly followed by
digits) in the SKILL.md body with the N-th argument. A price such as `$8/$40` then reaches the model as the
arguments' words. Invoked with no arguments the text is left alone, so the fault shows only on some runs
(bench-factory#340). The documented escape is one backslash: `\\$8` reaches the model as `$8`. A backslash
that is itself preceded by a backslash does not escape, so `\\\\$1` still expands.
"""
from pathlib import Path
import re
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOLLAR_DIGIT = re.compile(r'\$(?=\d)')


def unescaped_dollar_digits(text):
    """(line, column) for each `$` followed by a digit without the one-backslash escape."""
    found = []
    for m in DOLLAR_DIGIT.finditer(text):
        i = m.start()
        if i >= 1 and text[i - 1] == '\\' and not (i >= 2 and text[i - 2] == '\\'):
            continue
        found.append((text.count('\n', 0, i) + 1, i - text.rfind('\n', 0, i)))
    return found


def problems(skills_dir):
    out = []
    for p in sorted(Path(skills_dir).rglob('SKILL.md')):
        for line, col in unescaped_dollar_digits(p.read_text(encoding='utf-8')):
            out.append(f'{p.relative_to(skills_dir)}:{line}:{col}')
    return out


class SkillBodyTest(unittest.TestCase):
    def test_plugin_skills_have_no_unescaped_dollar_digit(self):
        self.assertEqual(problems(ROOT / 'skills'), [])

    def test_prices_are_flagged(self):
        self.assertEqual(unescaped_dollar_digits('It costs $8/$40 per Mtok.\nAbout $1.50 a task.\n'),
                         [(1, 10), (1, 13), (2, 7)])

    def test_one_backslash_escapes_and_two_do_not(self):
        self.assertEqual(unescaped_dollar_digits(r'It costs \$8/\$40 per Mtok.'), [])
        self.assertEqual(unescaped_dollar_digits(r'Not escaped: \\$1'), [(1, 16)])

    def test_other_dollars_are_not_flagged(self):
        self.assertEqual(unescaped_dollar_digits('USD 8, $ARGUMENTS, ${CLAUDE_SKILL_DIR}, $HOME, a lone $'), [])

    def test_a_new_skill_with_a_price_fails_the_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'priced').mkdir()
            (Path(tmp) / 'priced' / 'SKILL.md').write_text('---\nname: priced\n---\nAbout $0.05 an image.\n')
            self.assertEqual(problems(tmp), ['priced/SKILL.md:4:7'])


if __name__ == '__main__':
    unittest.main()
