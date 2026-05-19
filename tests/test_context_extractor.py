import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location(
    "context_extractor", ROOT / "scripts" / "context-extractor.py"
)
mod = importlib.util.module_from_spec(spec)
sys.modules["context_extractor"] = mod
spec.loader.exec_module(mod)


class ParsePageRangesTest(unittest.TestCase):
    def test_single_range(self):
        self.assertEqual(mod._parse_page_ranges("12-15"), [(12, 15)])

    def test_multi_ranges(self):
        self.assertEqual(
            mod._parse_page_ranges("34-41, 78-82, 156"),
            [(34, 41), (78, 82), (156, 156)],
        )

    def test_single_page(self):
        self.assertEqual(mod._parse_page_ranges("102"), [(102, 102)])

    def test_reversed_range_auto_correct(self):
        self.assertEqual(mod._parse_page_ranges("15-12"), [(12, 15)])

    def test_spaces_in_ranges(self):
        self.assertEqual(
            mod._parse_page_ranges(" 12 - 15 , 20 - 22 "), [(12, 15), (20, 22)]
        )

    def test_empty_string(self):
        self.assertEqual(mod._parse_page_ranges(""), [])

    def test_full_file_hint(self):
        self.assertTrue(mod._is_full_file_hint(""))
        self.assertTrue(mod._is_full_file_hint("全文"))
        self.assertFalse(mod._is_full_file_hint("12-15"))


class ExpandBufferTest(unittest.TestCase):
    def test_single_range_plus_one(self):
        self.assertEqual(mod._expand_buffer([(12, 15)], 1), [(11, 16)])

    def test_non_overlapping_ranges(self):
        self.assertEqual(
            mod._expand_buffer([(12, 15), (78, 82)], 1), [(11, 16), (77, 83)]
        )

    def test_overlapping_buffers_merge(self):
        self.assertEqual(mod._expand_buffer([(12, 15), (16, 17)], 1), [(11, 18)])

    def test_page_one_boundary(self):
        self.assertEqual(mod._expand_buffer([(1, 3)], 1), [(1, 4)])

    def test_adjacent_merge(self):
        result = mod._expand_buffer([(20, 25), (26, 30), (31, 35)], 1)
        self.assertEqual(result, [(19, 36)])

    def test_single_page_buffer(self):
        self.assertEqual(mod._expand_buffer([(102, 102)], 1), [(101, 103)])


class ParseMultiSourceRangesTest(unittest.TestCase):
    def test_single_pdf_single_range(self):
        result = mod._parse_multi_source_ranges("Platform Strategy.pdf:12-15")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["file"], "Platform Strategy.pdf")
        self.assertEqual(result[0]["pages"], [(12, 15)])

    def test_single_pdf_multi_ranges(self):
        result = mod._parse_multi_source_ranges(
            "Platform Strategy.pdf:34-41, 78-82, 156"
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["pages"], [(34, 41), (78, 82), (156, 156)])

    def test_multi_file_pdf_and_markdown(self):
        result = mod._parse_multi_source_ranges(
            "Digital Transformation.pdf:12-15, Strategy.md"
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["file"], "Digital Transformation.pdf")
        self.assertEqual(result[0]["pages"], [(12, 15)])
        self.assertEqual(result[1]["file"], "Strategy.md")
        self.assertEqual(result[1]["pages"], [])

    def test_two_pdfs_with_pages(self):
        result = mod._parse_multi_source_ranges("A.pdf:12-15, B.pdf:34-41, 78-82")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["pages"], [(12, 15)])
        self.assertEqual(result[1]["pages"], [(34, 41), (78, 82)])

    def test_pure_markdown_full_text(self):
        result = mod._parse_multi_source_ranges("Appendix.md")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["file"], "Appendix.md")
        self.assertEqual(result[0]["pages"], [])

    def test_spaces_in_filename(self):
        result = mod._parse_multi_source_ranges("Platform Strategy.pdf:12-15")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["file"], "Platform Strategy.pdf")


class ParseRoadmapSourceRangesTest(unittest.TestCase):
    def setUp(self):
        self.roadmap = """# 学习路线图（完整版）：平台战略

## 01. 平台战略

### 网络效应

**网络效应类型**  `source_range: Platform Strategy.pdf:45-52, 112-118`
- 详细解释：...

**网络效应与平台增长**  `source_range: Platform Strategy.pdf:120-125`
- 详细解释：...

### 生态治理

**平台治理机制**  `source_range: Platform Strategy.pdf:200-210, Appendix.md`
- 详细解释：...
"""
        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        self.tmp.write(self.roadmap)
        self.tmp.close()

    def tearDown(self):
        Path(self.tmp.name).unlink(missing_ok=True)

    def test_parse_all_knowledge_points(self):
        kps = mod.parse_roadmap_source_ranges(self.tmp.name)
        self.assertEqual(len(kps), 3)

    def test_parse_titles(self):
        kps = mod.parse_roadmap_source_ranges(self.tmp.name)
        titles = [kp["title"] for kp in kps]
        self.assertIn("网络效应类型", titles)
        self.assertIn("网络效应与平台增长", titles)
        self.assertIn("平台治理机制", titles)

    def test_parse_multi_range_source(self):
        kps = mod.parse_roadmap_source_ranges(self.tmp.name)
        net_effect = next(k for k in kps if k["title"] == "网络效应类型")
        self.assertEqual(len(net_effect["source_ranges"]), 1)
        self.assertEqual(
            net_effect["source_ranges"][0]["pages"], [(45, 52), (112, 118)]
        )

    def test_parse_multi_file_source(self):
        kps = mod.parse_roadmap_source_ranges(self.tmp.name)
        governance = next(k for k in kps if k["title"] == "平台治理机制")
        self.assertEqual(len(governance["source_ranges"]), 2)
        self.assertEqual(governance["source_ranges"][1]["file"], "Appendix.md")

    def test_note_file_paths_inferred(self):
        kps = mod.parse_roadmap_source_ranges(self.tmp.name)
        net_effect = next(k for k in kps if k["title"] == "网络效应类型")
        self.assertIn("网络效应", net_effect["note_file"])


class ExtractTextForSourceTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.vault = self.tmpdir.name
        md_path = Path(self.vault) / "test.md"
        md_path.write_text("# Test\n\nContent line one.\nContent line two.\n", encoding="utf-8")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_markdown_full_extraction(self):
        result = mod.extract_text_for_source(self.vault, {"file": "test.md", "pages": []})
        self.assertIn("Content line one", result["text"])
        self.assertEqual(result["pages"], "全文")

    def test_missing_source_preserves_label(self):
        result = mod.extract_text_for_source(
            self.vault, {"file": "nonexistent.pdf", "pages": [(12, 15)]}
        )
        self.assertEqual(result["text"], "")
        self.assertIn("12-15", result["pages"])


if __name__ == "__main__":
    unittest.main()
