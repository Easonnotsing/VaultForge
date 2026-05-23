import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = os.path.join(ROOT, "tests", "fixtures")

spec = importlib.util.spec_from_file_location(
    "double_link_builder", ROOT / "scripts" / "double-link-builder.py"
)
mod = importlib.util.module_from_spec(spec)
sys.modules["double_link_builder"] = mod
spec.loader.exec_module(mod)


SAMPLE_VAULT = ROOT / "tests" / "fixtures" / "sample_vault"


def _make_temp_vault(tmp_root):
    """Copy sample_vault into a temp directory so tests don't mutate fixtures."""
    import shutil

    dst = Path(tmp_root) / "vault"
    shutil.copytree(SAMPLE_VAULT, dst)
    return dst


class FindRelationshipsHeuristicTest(unittest.TestCase):
    def test_derivation_detected(self):
        note1 = {
            "path": "/a/1.md",
            "title": "网络效应",
            "content": "网络效应导致平台增长，因此用户越多价值越高。所以平台常形成规模优势。",
            "folder": "01. 平台战略/网络效应",
        }
        note2 = {
            "path": "/a/2.md",
            "title": "平台增长",
            "content": "平台增长基于网络效应，因此早期获客至关重要。由此可见冷启动是成功关键。",
            "folder": "01. 平台战略/网络效应",
        }
        rels = mod.find_relationships_heuristic(note1, note2)
        self.assertTrue(any(r[0] == "derivation" for r in rels))

    def test_analogy_detected(self):
        note1 = {
            "path": "/a/1.md",
            "title": "网络效应",
            "content": "网络效应类似于生物学中的正反馈机制，正如生态系统的自我强化。",
            "folder": "01. 平台战略/网络效应",
        }
        note2 = {
            "path": "/a/2.md",
            "title": "网络效应",
            "content": "平台增长的原理可以类比病毒传播模型。",
            "folder": "01. 平台战略/网络效应",
        }
        rels = mod.find_relationships_heuristic(note1, note2)
        self.assertTrue(any(r[0] == "analogy" for r in rels))

    def test_contradiction_detected(self):
        note1 = {
            "path": "/a/1.md",
            "title": "平台控制",
            "content": "平台应该加强控制以维持生态秩序。",
            "folder": "01. 平台战略/生态治理",
        }
        note2 = {
            "path": "/a/2.md",
            "title": "平台控制",
            "content": "然而过度控制会抑制创新，反而导致生态僵化。这种矛盾在实践中有大量争议。",
            "folder": "01. 平台战略/生态治理",
        }
        rels = mod.find_relationships_heuristic(note1, note2)
        self.assertTrue(any(r[0] == "contradiction" for r in rels))

    def test_application_detected(self):
        note1 = {
            "path": "/a/1.md",
            "title": "网络效应",
            "content": "网络效应是平台的核心驱动力。",
            "folder": "01. 平台战略/网络效应",
        }
        note2 = {
            "path": "/a/2.md",
            "title": "冷启动策略",
            "content": "冷启动策略适用于网络效应显著的平台市场。",
            "folder": "01. 平台战略/网络效应",
        }
        rels = mod.find_relationships_heuristic(note1, note2)
        self.assertTrue(any(r[0] == "application" for r in rels))

    def test_context_detected(self):
        note1 = {
            "path": "/a/1.md",
            "title": "网络效应",
            "content": "网络效应是平台的发展阶段理论的基础。",
            "folder": "01. 平台战略/网络效应",
        }
        note2 = {
            "path": "/a/2.md",
            "title": "平台治理",
            "content": "平台治理从历史视角来看经历了多个演进阶段。",
            "folder": "01. 平台战略/生态治理",
        }
        rels = mod.find_relationships_heuristic(note1, note2)
        self.assertTrue(any(r[0] == "context" for r in rels))

    def test_no_false_positive_unrelated(self):
        note1 = {
            "path": "/a/1.md",
            "title": "网络效应",
            "content": "网络效应驱动平台增长。",
            "folder": "01. 平台战略/网络效应",
        }
        note2 = {
            "path": "/b/2.md",
            "title": "财务管理",
            "content": "现金流管理是企业生存的基础。",
            "folder": "02. 财务管理/现金",
        }
        rels = mod.find_relationships_heuristic(note1, note2)
        self.assertEqual(rels, [])


class StructuralAffinityTest(unittest.TestCase):
    def test_same_h3_folder(self):
        n1 = {"folder": "01. 平台战略/网络效应"}
        n2 = {"folder": "01. 平台战略/网络效应"}
        self.assertEqual(mod.structural_affinity(n1, n2), 1.0)

    def test_same_h2_diff_h3(self):
        n1 = {"folder": "01. 平台战略/网络效应"}
        n2 = {"folder": "01. 平台战略/生态治理"}
        self.assertEqual(mod.structural_affinity(n1, n2), 0.5)

    def test_different_h2(self):
        n1 = {"folder": "01. 平台战略/网络效应"}
        n2 = {"folder": "02. 财务管理/现金"}
        self.assertEqual(mod.structural_affinity(n1, n2), 0.0)


class GenerateCandidatesTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.vault = str(_make_temp_vault(self.tmpdir.name))

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_candidates_have_scores(self):
        notes = mod.get_all_notes(self.vault)
        idx = mod.TfidfIndex()
        doc_tokens = {}
        doc_map = {}
        for i, n in enumerate(notes):
            tokens = mod.tokenize(n["content"])
            doc_tokens[i] = tokens
            doc_map[n["rel_path"]] = i
            idx.add_document(i, tokens)
        idx.finalize()
        candidates = mod.generate_candidates(notes, idx, doc_tokens, doc_map)
        for c in candidates:
            self.assertIn("structural", c["scores"])
            self.assertIn("tfidf_cosine", c["scores"])
            self.assertIn("keyword_rules", c["scores"])

    def test_structural_filter_respected(self):
        notes = mod.get_all_notes(self.vault)
        idx = mod.TfidfIndex()
        doc_tokens = {}
        doc_map = {}
        for i, n in enumerate(notes):
            tokens = mod.tokenize(n["content"])
            doc_tokens[i] = tokens
            doc_map[n["rel_path"]] = i
            idx.add_document(i, tokens)
        idx.finalize()
        candidates = mod.generate_candidates(notes, idx, doc_tokens, doc_map)
        for c in candidates:
            n1 = next(n for n in notes if n["rel_path"] == c["note_a"])
            n2 = next(n for n in notes if n["rel_path"] == c["note_b"])
            aff = mod.structural_affinity(n1, n2)
            self.assertGreaterEqual(aff, 0.5, f"{c['note_a']} <-> {c['note_b']}")


class TokenizeTest(unittest.TestCase):
    def test_chinese_bigram(self):
        tokens = mod.tokenize("网络效应驱动平台增长")
        self.assertIn("网络", tokens)
        self.assertIn("效应", tokens)

    def test_english_words(self):
        tokens = mod.tokenize("platform strategy framework")
        self.assertIn("platform", tokens)
        self.assertIn("strategy", tokens)

    def test_stop_words_filtered(self):
        tokens = mod.tokenize("the platform and the strategy")
        self.assertNotIn("the", tokens)
        self.assertNotIn("and", tokens)


class AddLinksToNotesTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.vault = str(_make_temp_vault(self.tmpdir.name))

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_links_added_and_dedup(self):
        notes = mod.get_all_notes(self.vault)
        n1 = notes[0]
        note_links = {n1["rel_path"]: [notes[1]["title"]]}
        updated = mod.add_links_to_notes(self.vault, note_links)
        self.assertGreaterEqual(updated, 1)
        updated2 = mod.add_links_to_notes(self.vault, note_links)
        self.assertEqual(updated2, 0)


class BuildRoadmapMocLinksTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.vault = str(_make_temp_vault(self.tmpdir.name))

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_links_created(self):
        mocs = mod.get_all_mocs(self.vault)
        self.assertGreater(len(mocs), 0)
        updated = mod.build_roadmap_moc_links(self.vault, "平台战略", mocs)
        self.assertGreaterEqual(updated, 1)


class EnglishRoadmapTest(unittest.TestCase):
    """P0-2 regression: English roadmap filenames and bilingual headers."""

    def test_discover_roadmap_theme_english(self):
        vault = os.path.join(FIXTURES_DIR, "english-vault")
        theme = mod.discover_roadmap_theme(vault)
        self.assertEqual(theme, "Platform Strategy")

    def test_discover_roadmap_theme_chinese(self):
        vault = os.path.join(FIXTURES_DIR, "sample_vault")
        theme = mod.discover_roadmap_theme(vault)
        self.assertIsNotNone(theme)

    def test_get_related_notes_header_english(self):
        content = "## Related Notes\n- [[Note1]]"
        self.assertEqual(mod._get_related_notes_header(content), "## Related Notes")

    def test_get_related_notes_header_chinese(self):
        content = "## 相关笔记\n- [[Note1]]"
        self.assertEqual(mod._get_related_notes_header(content), "## 相关笔记")

    def test_english_roadmap_moc_links(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            import shutil
            src = os.path.join(FIXTURES_DIR, "english-vault")
            dst = os.path.join(tmpdir, "english-vault")
            shutil.copytree(src, dst)
            mocs = mod.get_all_mocs(dst)
            updated = mod.build_roadmap_moc_links(dst, "Platform Strategy", mocs)
            self.assertGreaterEqual(updated, 0)
            # Verify English backlink was written, not Chinese
            for moc in mocs:
                moc_path = os.path.join(dst, moc["rel_path"])
                content = open(moc_path, encoding="utf-8").read()
                self.assertIn("Learning Roadmap", content)
                self.assertNotIn("学习路线图", content)


class RoadmapVersionTest(unittest.TestCase):
    """P1 regression: numeric version sorting (v10 > v2)."""

    def test_numeric_version_sort(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create roadmap files with different versions
            for name in ("Learning Roadmap v10 - Test.md",
                         "Learning Roadmap v2 - Test.md",
                         "学习路线图 v3 - Test.md"):
                Path(tmpdir, name).write_text("# Test")
            result = mod._find_roadmap_file(tmpdir, "Test")
            self.assertIn("v10", result)  # v10 > v3 > v2

    def test_legacy_fallback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "Learning Roadmap - Test.md").write_text("# Test")
            result = mod._find_roadmap_file(tmpdir, "Test")
            self.assertIn("Learning Roadmap - Test", result)


if __name__ == "__main__":
    unittest.main()
