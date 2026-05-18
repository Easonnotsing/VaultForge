import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


double_link = load_module("double_link_builder", "scripts/double-link-builder.py")
roadmap_editor = load_module("roadmap_editor", "scripts/roadmap-editor.py")


class DoubleLinkBuilderTest(unittest.TestCase):
    def make_vault(self, root):
        vault = Path(root)
        network_dir = vault / "01. 平台战略" / "网络效应"
        governance_dir = vault / "01. 平台战略" / "生态治理"
        network_dir.mkdir(parents=True)
        governance_dir.mkdir(parents=True)

        (vault / "学习路线图 - 平台战略.md").write_text(
            "# 学习路线图 - 平台战略\n\n"
            "## 01. 平台战略\n\n"
            "### 网络效应\n\n"
            "- 网络效应类型\n"
            "- 网络效应与平台增长\n\n"
            "### 生态治理\n\n"
            "- 平台治理机制\n",
            encoding="utf-8",
        )
        (network_dir / "网络效应 MOC.md").write_text("# 网络效应 MOC\n", encoding="utf-8")
        (governance_dir / "生态治理 MOC.md").write_text("# 生态治理 MOC\n", encoding="utf-8")
        (network_dir / "网络效应类型.md").write_text(
            "# 网络效应类型\n\n"
            "## 核心知识点\n"
            "网络效应会导致平台增长，因此用户越多，价值越高。所以平台常形成规模优势。\n",
            encoding="utf-8",
        )
        (network_dir / "网络效应与平台增长.md").write_text(
            "# 网络效应与平台增长\n\n"
            "## 核心知识点\n"
            "平台增长基于网络效应的应用，实践中可用于冷启动和扩张。\n",
            encoding="utf-8",
        )
        (governance_dir / "平台治理机制.md").write_text(
            "# 平台治理机制\n\n"
            "## 核心知识点\n"
            "平台治理关注规则设计、参与者激励和生态秩序。\n",
            encoding="utf-8",
        )
        return vault

    def test_default_generates_candidates_without_mutating_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = self.make_vault(tmp)
            notes = double_link.get_all_notes(str(vault))
            candidates = double_link.build_link_candidates(notes)
            candidate_path = double_link.write_link_candidates(str(vault), candidates, "link-candidates.md")

            note_content = (vault / "01. 平台战略" / "网络效应" / "网络效应类型.md").read_text(encoding="utf-8")
            candidate_text = candidate_path.read_text(encoding="utf-8")

            self.assertIn("网络效应类型", candidate_text)
            self.assertIn("网络效应与平台增长", candidate_text)
            self.assertNotIn("平台治理机制 -> 网络效应类型", candidate_text)
            self.assertNotIn("## 相关笔记", note_content)

    def test_apply_adds_note_and_roadmap_links_after_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = self.make_vault(tmp)
            notes = double_link.get_all_notes(str(vault))
            mocs = double_link.get_all_mocs(str(vault))
            candidates = double_link.build_link_candidates(notes)

            note_updates = double_link.apply_link_candidates(candidates)
            roadmap_updates = double_link.build_roadmap_moc_links(str(vault), "平台战略", mocs, apply=True)

            type_text = (vault / "01. 平台战略" / "网络效应" / "网络效应类型.md").read_text(encoding="utf-8")
            growth_text = (vault / "01. 平台战略" / "网络效应" / "网络效应与平台增长.md").read_text(encoding="utf-8")
            roadmap_text = (vault / "学习路线图 - 平台战略.md").read_text(encoding="utf-8")
            moc_text = (vault / "01. 平台战略" / "网络效应" / "网络效应 MOC.md").read_text(encoding="utf-8")

            self.assertEqual(note_updates, 1)
            self.assertGreaterEqual(roadmap_updates, 2)
            self.assertTrue(
                "[[网络效应与平台增长]]" in type_text
                or "[[网络效应类型]]" in growth_text
            )
            self.assertIn("[[01. 平台战略/网络效应/网络效应 MOC|网络效应]]", roadmap_text)
            self.assertIn("[[../../学习路线图 - 平台战略|学习路线图]]", moc_text)


class RoadmapEditorTest(unittest.TestCase):
    def test_render_roundtrip_preserves_header_and_structure(self):
        markdown = (
            "# 学习路线图 - 平台战略\n\n"
            "## 01. 平台战略\n\n"
            "### 网络效应\n\n"
            "- 网络效应类型\n"
        )
        parsed = roadmap_editor.parse_markdown_roadmap(markdown)
        parsed["sections"][0]["topics"][0]["content"] = "- 网络效应类型\n- 网络效应与平台增长"

        rendered = roadmap_editor.render_markdown_roadmap(parsed)

        self.assertIn("# 学习路线图 - 平台战略", rendered)
        self.assertIn("## 01. 平台战略", rendered)
        self.assertIn("### 网络效应", rendered)
        self.assertIn("- 网络效应与平台增长", rendered)

    def test_write_roadmap_with_backup_updates_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            roadmap_path = Path(tmp) / "学习路线图 - 平台战略.md"
            original = (
                "# 学习路线图 - 平台战略\n\n"
                "## 01. 平台战略\n\n"
                "### 网络效应\n\n"
                "- 网络效应类型\n"
            )
            roadmap_path.write_text(original, encoding="utf-8")

            result = {
                "sections": [
                    {
                        "title": "01. 平台战略",
                        "topics": [
                            {
                                "title": "网络效应",
                                "content": "- 网络效应类型\n- 网络效应与平台增长",
                            }
                        ],
                    }
                ]
            }

            backup_path = roadmap_editor.write_roadmap_with_backup(str(roadmap_path), original, result)

            self.assertEqual(backup_path.read_text(encoding="utf-8"), original)
            self.assertIn("网络效应与平台增长", roadmap_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
