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

    def test_all_agents_have_language_requirement(self):
        agents_dir = ROOT / "agents"
        for f in sorted(agents_dir.glob("*.md")):
            content = f.read_text(encoding="utf-8")
            self.assertTrue(
                "Language Requirement" in content or "Reading Flow" in content,
                f"{f.name} missing Language Requirement or Reading Flow section"
            )


class CrossFileConsistencyTest(unittest.TestCase):
    """Cross-file invariants that prevent silent drift between SKILL.md and agents."""

    @classmethod
    def setUpClass(cls):
        cls.skill_md = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        cls.roadmap_md = (ROOT / "agents" / "roadmap-generator.md").read_text(encoding="utf-8")
        cls.filler_md = (ROOT / "agents" / "atomic-note-filler.md").read_text(encoding="utf-8")
        cls.creator_md = (ROOT / "agents" / "file-structure-creator.md").read_text(encoding="utf-8")
        cls.reviewer_md = (ROOT / "agents" / "note-reviewer.md").read_text(encoding="utf-8")
        cls.templates_md = (ROOT / "references" / "templates.md").read_text(encoding="utf-8")

    def test_vf_version_consistent(self):
        """All frontmatter templates use the same vf_version."""
        version_pattern = re.compile(r"vf_version:\s*([\w.]+)")
        all_versions = set()
        files = [
            self.skill_md, self.roadmap_md, self.filler_md,
            self.creator_md, self.reviewer_md, self.templates_md,
        ]
        for content in files:
            for m in version_pattern.finditer(content):
                all_versions.add(m.group(1))
        self.assertEqual(
            len(all_versions), 1,
            f"vf_version mismatch across files: {sorted(all_versions)}"
        )

    def test_roadmap_naming_convention_consistent(self):
        """SKILL.md Step 1.5 and roadmap-generator.md agree on naming."""
        naming_v1 = "Learning Roadmap v1 -"
        self.assertIn(naming_v1, self.skill_md,
                      "SKILL.md should use v1 naming for initial roadmap")
        self.assertIn(naming_v1, self.roadmap_md,
                      "roadmap-generator.md should use v1 naming for initial roadmap")

    def test_vf_status_values_defined(self):
        """All three vf_status values appear in docs."""
        for status in ("pristine", "user_modified", "locked"):
            self.assertIn(status, self.skill_md,
                          f"vf_status '{status}' not found in SKILL.md")

    def test_no_stale_version_banners_in_readme(self):
        """README should not contain hardcoded version numbers."""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        # Check that no "v2.x" version banners remain in non-code, non-link contexts
        version_banner = re.findall(r"\(v2\.\d[^)]*\)", readme)
        self.assertEqual(
            version_banner, [],
            f"README contains stale version banners: {version_banner}"
        )

    def test_phase_0_not_in_agents_directory(self):
        """Phase 0 is main-agent orchestration; agents/ should not have a Phase 0 file."""
        agents_dir = ROOT / "agents"
        phase0_files = list(agents_dir.glob("*scanner*")) + list(agents_dir.glob("*phase0*"))
        self.assertEqual(
            phase0_files, [],
            f"Phase 0 should not have a sub-agent file: {phase0_files}"
        )

    def test_incremental_mode_present_in_all_agents(self):
        """All agent files that have incremental behavior should mention incremental_mode."""
        # roadmap-generator has explicit incremental section
        self.assertIn("incremental_mode", self.roadmap_md,
                      "roadmap-generator.md missing incremental_mode")
        # note-reviewer has incremental_mode input parameter
        self.assertIn("incremental_mode", self.reviewer_md,
                      "note-reviewer.md missing incremental_mode")
        # file-structure-creator has "Incremental mode (add-only)" section
        self.assertIn("Incremental mode", self.creator_md,
                      "file-structure-creator.md missing Incremental mode section")
        # atomic-note-filler has refresh mode (incremental sub-feature)
        self.assertIn("Refresh Mode", self.filler_md,
                      "atomic-note-filler.md missing Refresh Mode section")


if __name__ == "__main__":
    unittest.main()
