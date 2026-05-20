import py_compile
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SkillFileIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_md = (ROOT / "SKILL.md").read_text(encoding="utf-8")

    def test_referenced_files_exist(self):
        refs = re.findall(r"\[([^\]]+)\]\(\./([^)]+)\)", self.skill_md)
        missing = []
        for label, path in refs:
            full = ROOT / path
            if not full.exists():
                missing.append(path)
        self.assertEqual(
            missing, [], f"Broken references in SKILL.md: {missing}"
        )

    def test_phase_numbering_continuous(self):
        phases = re.findall(r"### Phase (\d+):", self.skill_md)
        nums = [int(p) for p in phases]
        expected = list(range(0, max(nums) + 1)) if nums else []
        self.assertEqual(
            nums, expected, f"Phase numbering not continuous: {nums}"
        )

    def test_interaction_convention_present(self):
        self.assertIn("## Interaction Conventions", self.skill_md)

    def test_no_duplicate_sections(self):
        lines = self.skill_md.split("\n")
        sections = []
        in_code = False
        for line in lines:
            if line.startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            m = re.match(r"^## (.+)$", line)
            if m:
                sections.append(m.group(1))
        seen = {}
        dupes = []
        for s in sections:
            if s in seen:
                dupes.append(s)
            seen[s] = 1
        self.assertEqual(dupes, [], f"Duplicate H2 sections: {dupes}")


class ScriptSyntaxTest(unittest.TestCase):
    def test_context_extractor_syntax(self):
        py_compile.compile(
            str(ROOT / "scripts" / "context-extractor.py"), doraise=True
        )

    def test_double_link_builder_syntax(self):
        py_compile.compile(
            str(ROOT / "scripts" / "double-link-builder.py"), doraise=True
        )

    def test_roadmap_editor_syntax(self):
        py_compile.compile(
            str(ROOT / "scripts" / "roadmap-editor.py"), doraise=True
        )


class AgentFileFormatTest(unittest.TestCase):
    def test_all_agents_have_name(self):
        agents_dir = ROOT / "agents"
        for f in sorted(agents_dir.glob("*.md")):
            content = f.read_text(encoding="utf-8")
            self.assertIn("name:", content[:200], f"{f.name} missing name field")

    def test_all_agents_have_description(self):
        agents_dir = ROOT / "agents"
        for f in sorted(agents_dir.glob("*.md")):
            content = f.read_text(encoding="utf-8")
            self.assertIn(
                "description:", content[:300], f"{f.name} missing description field"
            )


if __name__ == "__main__":
    unittest.main()
