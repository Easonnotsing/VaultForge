#!/usr/bin/env python3
"""
上下文预提取脚本 — Phase 3.0b

从学习路线图（完整版）解析 source_range 标注，自动从原文中提取对应段落，
输出结构化上下文包 JSON 供 Phase 3 填充 agent 使用。

核心能力：
  - 支持多页码段：source_range: file.pdf:12-15, 45-48, 102
  - 支持多源文件：source_range: A.pdf:12-15, B.md
  - PDF 提取（±1 页缓冲区）
  - Markdown / TXT 全文提取
  - 非 PDF 文件无页码概念时，source_range 可省略页码表示全文
  - pypdf 缺失时优雅降级（跳过 PDF，提取仍可用的非 PDF 内容）

用法:
  python3 context-extractor.py <vault_path> <roadmap_path> --output context_packets.json
  python3 context-extractor.py <vault_path> <roadmap_path> --output packets.json --note-filter note1.md,note2.md

依赖:
  - pypdf（可选，用于 PDF 页码提取；未安装时 PDF 源降级为空文本）

source_range 格式规范:
  source_range: {文件名}:{页码段1}, {页码段2}, ...
  页码段: 单页(102) | 连续区间(12-15) | 全文(.md文件省略页码)

示例:
  source_range: Platform Strategy.pdf:34-41, 78-82, 156
  source_range: Digital Transformation.pdf:12-15, Strategy.md
  source_range: Technical Overview.txt
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ─── PDF 依赖检测 ──────────────────────────────────────────────────

_PDF_BACKEND = None  # "pypdf" or "pypdf2"
_HAS_PDF = False

try:
    import pypdf  # noqa: F401

    _PDF_BACKEND = "pypdf"
    _HAS_PDF = True
except ImportError:
    try:
        import PyPDF2  # noqa: F401

        _PDF_BACKEND = "pypdf2"
        _HAS_PDF = True
    except ImportError:
        pass


def _get_pdf_reader(filepath):
    """统一 PDF reader 工厂，兼容 PyPDF2 和 pypdf"""
    if _PDF_BACKEND == "pypdf2":
        return PyPDF2.PdfReader(str(filepath))
    elif _PDF_BACKEND == "pypdf":
        return pypdf.PdfReader(str(filepath))
    return None


def _warn_pypdf2_missing():
    if not getattr(_warn_pypdf2_missing, "_warned", False):
        print(
            "⚠️  PDF 库未安装。PDF 文件的页码提取将跳过。\n"
            "   安装: pip install pypdf  (或 pip install PyPDF2)\n"
            "   Markdown / TXT 文件提取不受影响。",
            file=sys.stderr,
        )
        _warn_pypdf2_missing._warned = True


# ─── 核心类型 ──────────────────────────────────────────────────────

SourceRange = Dict  # {file: str, pages: List[Tuple[int, int]]}
KnowledgePoint = Dict  # {title, note_file, source_ranges, ...}
ContextPacket = Dict  # {note_file, title, source_excerpts, ...}
Excerpt = Dict  # {source, pages, text}


# ─── 步骤 1: 解析路线图中的 source_range ──────────────────────────


def _is_full_file_hint(pages_str: str) -> bool:
    """判断 pages_str 是否表示全文（空字符串或仅含非数字字符）"""
    stripped = pages_str.strip()
    if not stripped:
        return True
    # 如果看起来不像页码（不含任何数字），也视为全文标记
    return not re.search(r"\d", stripped)


def _parse_page_ranges(pages_str: str) -> List[Tuple[int, int]]:
    """
    解析页码段字符串，返回 [(start, end), ...] 列表（两端均 inclusive）。
    输入: "12-15, 45-48, 102"
    输出: [(12, 15), (45, 48), (102, 102)]
    """
    if _is_full_file_hint(pages_str):
        return []  # 空列表 = 全文标记（由调用方按文件类型处理）

    ranges: List[Tuple[int, int]] = []
    parts = [p.strip() for p in pages_str.split(",") if p.strip()]

    for part in parts:
        if "-" in part:
            m = re.match(r"(\d+)\s*-\s*(\d+)", part)
            if m:
                start, end = int(m.group(1)), int(m.group(2))
                if start > end:
                    start, end = end, start  # 自动修正反转的区间
                ranges.append((start, end))
                continue
        m = re.match(r"(\d+)", part)
        if m:
            page = int(m.group(1))
            ranges.append((page, page))

    return ranges


def _expand_buffer(ranges: List[Tuple[int, int]], buffer: int = 1) -> List[Tuple[int, int]]:
    """给每个页码范围加上 ±buffer 页，合并重叠区间"""
    expanded = [(max(1, s - buffer), e + buffer) for s, e in ranges]
    expanded.sort()
    merged: List[Tuple[int, int]] = []
    for s, e in expanded:
        if merged and s <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


def parse_roadmap_source_ranges(roadmap_path: str) -> List[KnowledgePoint]:
    """
    从完整版路线图中解析所有知识点及其 source_range。

    识别模式：
      **知识点标题**  `source_range: file:pages, file:pages, ...`
    或  **知识点标题**
        source_range: file:pages, file:pages

    返回:
      [
        {
          "title": "数字化与转型的定义区分",
          "note_file": "01. 数字化转型/转型概述/数字化vs数字化转型.md",
          "source_ranges": [
            {"file": "Digital Transformation.pdf", "pages": [(12,15), (78,80)]},
            {"file": "Appendix.md", "pages": []}
          ]
        }
      ]
    """
    with open(roadmap_path, "r", encoding="utf-8") as f:
        content = f.read()

    knowledge_points: List[KnowledgePoint] = []
    current_h2: Optional[str] = None
    current_h3: Optional[str] = None

    # 用行级扫描，逐行识别 H2 / H3 / 知识点 / source_range
    lines = content.split("\n")

    for i, line in enumerate(lines):
        # 跟踪当前 H2 / H3 层级（用于推断文件夹路径）
        h2_match = re.match(r"^##\s+(.+)$", line)
        if h2_match:
            current_h2 = h2_match.group(1).strip()
            # 处理带编号的 H2（如 "01. 数字化转型"）
            h2_num_match = re.match(r"^\d+\.\s+(.+)", current_h2)
            if h2_num_match:
                current_h2 = current_h2
            continue

        h3_match = re.match(r"^###\s+(.+)$", line)
        if h3_match:
            current_h3 = h3_match.group(1).strip()
            continue

        # 识别知识点行：以 ** 开头的粗体标题
        kp_match = re.match(r"^\*\*(.+?)\*\*\s*`?source_range:\s*(.+?)`?\s*$", line)
        if kp_match:
            title = kp_match.group(1).strip()
            raw_source_range = kp_match.group(2).strip()
            source_ranges = _parse_multi_source_ranges(raw_source_range)

            note_file = _infer_note_file_path(title, current_h2, current_h3)

            knowledge_points.append(
                {
                    "title": title,
                    "note_file": note_file,
                    "source_ranges": source_ranges,
                }
            )
            continue

        # 兼容模式：source_range 在后续行（支持空行间隔，向前搜索最多 3 行）
        kp_bare_match = re.match(r"^\*\*(.+?)\*\*\s*$", line)
        if kp_bare_match:
            title = kp_bare_match.group(1).strip()
            # 向前扫描非空行，查找 source_range（最多 3 行）
            sr_found = False
            for j in range(1, min(4, len(lines) - i)):
                look_line = lines[i + j].strip()
                if not look_line:
                    continue
                sr_match = re.match(r"^`?source_range:\s*(.+?)`?\s*$", look_line)
                if sr_match:
                    raw_source_range = sr_match.group(1).strip()
                    source_ranges = _parse_multi_source_ranges(raw_source_range)
                    note_file = _infer_note_file_path(title, current_h2, current_h3)
                    knowledge_points.append(
                        {
                            "title": title,
                            "note_file": note_file,
                            "source_ranges": source_ranges,
                        }
                    )
                    sr_found = True
                    i = i + j  # skip ahead
                    break
                elif not look_line.startswith("source_range:") and look_line != "-":
                    # 这不是 source_range 行，停止搜索
                    break
            if sr_found:
                continue

    return knowledge_points


def _parse_multi_source_ranges(raw: str) -> List[SourceRange]:
    """
    解析原始 source_range 字符串为结构化列表。

    每个 segment 格式: "filename.ext:pages" 或 "filename.ext"
    多页码段以逗号分隔: "file.pdf:12-15, 34-41, 78-82"
    """
    segments = _smart_split_source_range(raw)
    result: List[SourceRange] = []

    for seg in segments:
        file_match = re.match(
            r"^(.+?\.(?:pdf|md|txt)):\s*(.*)$", seg, re.IGNORECASE
        )
        if file_match:
            result.append(
                {
                    "file": file_match.group(1).strip(),
                    "pages": _parse_page_ranges(file_match.group(2)),
                }
            )
        else:
            # 纯文件名，无页码段
            result.append({"file": seg.strip(), "pages": []})

    return result


def _smart_split_source_range(raw: str) -> List[str]:
    """
    用文件扩展名作为锚点分割 source_range。

    核心原则：每个 `.pdf`/`.md`/`.txt` 扩展名标记一个文件的结束。
    扩展名后跟着的 `:页码段` 属于同一个文件片段。
    同一片段内逗号分隔的是多页码范围。

    输入: "Platform Strategy.pdf:34-41, 78-82, Digital Transformation.pdf:12-15, Appendix.md"
    输出: ["Platform Strategy.pdf:34-41, 78-82", "Digital Transformation.pdf:12-15", "Appendix.md"]
    """
    # 匹配: 文件名(允许空格不含逗号) + .ext + 可选的 :页号
    pattern = re.compile(
        r"([^,]+?\.(?:pdf|md|txt))"   # 文件名（贪婪最小匹配，不含逗号）
        r"(?::\s*([\d\-\s,]+))?",      # 可选的 :页码段
        re.IGNORECASE,
    )
    segments: List[str] = []
    for m in pattern.finditer(raw):
        filename = m.group(1).strip()
        pages = (m.group(2) or "").strip().rstrip(",")
        if pages:
            segments.append(f"{filename}:{pages}")
        else:
            segments.append(filename)
    return segments if segments else [raw]


def _infer_note_file_path(title: str, h2: Optional[str], h3: Optional[str]) -> str:
    """从知识点标题和当前 H2/H3 层级推断原子笔记的文件路径"""
    safe_title = _safe_filename(title)
    h2_part = _safe_filename(h2) if h2 else "Uncategorized"
    h3_part = _safe_filename(h3) if h3 else "General"
    return f"{h2_part}/{h3_part}/{safe_title}.md"


def _safe_filename(name: str) -> str:
    """将标题转换为安全的文件名"""
    s = re.sub(r'[<>:"/\\|?*]', "-", name)
    s = s.strip().rstrip(".")
    return s


# ─── 步骤 2: 文本提取 ──────────────────────────────────────────────


def _resolve_source_path(vault_path: str, source_file: str) -> Optional[Path]:
    """
    在 vault 中查找源文件。
    搜索策略：
      1. vault_path/学习材料文件夹/{source_file}
      2. vault_path/{source_file}
      3. vault_path 递归搜索
    """
    vault = Path(vault_path)
    candidates = [
        vault / source_file,
    ]
    # 在 vault 根目录和一级子目录下搜索
    for entry in vault.iterdir():
        if entry.is_dir() and not entry.name.startswith("."):
            candidates.append(entry / source_file)
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    # 递归搜索（性能较差的最终兜底）
    for candidate in vault.rglob(source_file):
        if candidate.is_file():
            return candidate
    return None


def extract_pdf_pages(filepath: Path, ranges: List[Tuple[int, int]], buffer: int = 1) -> str:
    """提取 PDF 的指定页码范围，返回合并后的文本。范围为空则返回空。"""
    if not _HAS_PDF:
        _warn_pypdf2_missing()
        return ""

    reader = _get_pdf_reader(filepath)
    if reader is None:
        return ""
    try:
        total_pages = len(reader.pages)
    except Exception as e:
        print(f"  ⚠️ 无法读取 PDF: {filepath.name} ({e})", file=sys.stderr)
        return ""
    expanded = _expand_buffer(ranges, buffer)
    texts: List[str] = []

    for start, end in expanded:
        for p in range(start, end + 1):
            page_idx = p - 1  # PDF 页码通常从 1 开始，列表索引从 0
            if 0 <= page_idx < total_pages:
                try:
                    page_text = reader.pages[page_idx].extract_text()
                    if page_text:
                        texts.append(f"[p.{p}] {page_text.strip()}")
                except Exception:
                    pass

    return "\n\n".join(texts)


def extract_text_file(filepath: Path) -> str:
    """提取 Markdown / TXT 等纯文本文件的全部内容"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, "r", encoding="latin-1") as f:
                return f.read()
        except Exception as e:
            print(f"  ⚠️ 无法读取文本文件: {filepath.name} ({e})", file=sys.stderr)
            return ""
    except Exception as e:
        print(f"  ⚠️ 无法读取文件: {filepath.name} ({e})", file=sys.stderr)
        return ""


def extract_text_for_source(
    vault_path: str, source_range: SourceRange, buffer: int = 1
) -> Excerpt:
    """根据单个 source_range 提取文本"""
    filename = source_range["file"]
    pages = source_range.get("pages", [])
    filepath = _resolve_source_path(vault_path, filename)

    # 生成人类可读的 pages 标签（即使文件未找到也保留）
    if pages:
        pages_label = ", ".join(
            f"{s}-{e}" if s != e else str(s) for s, e in pages
        )
    else:
        pages_label = "全文"

    if filepath is None:
        print(f"  ⚠️ 未找到源文件: {filename}", file=sys.stderr)
        return {"source": filename, "pages": pages_label, "text": ""}

    ext = filepath.suffix.lower()
    pages_label = ", ".join(f"{s}-{e}" if s != e else str(s) for s, e in pages) if pages else "全文"

    if ext == ".pdf":
        if pages:
            text = extract_pdf_pages(filepath, pages, buffer)
            with_buffer = _expand_buffer(pages, buffer)
            buffer_label = ", ".join(
                f"{s}-{e}" if s != e else str(s) for s, e in with_buffer
            )
            return {
                "source": filename,
                "pages": f"{pages_label} (buffer: {buffer_label})",
                "text": text,
            }
        else:
            # PDF 无页码 = 全文提取（所有页）
            try:
                if _HAS_PDF:
                    reader = _get_pdf_reader(filepath)
                    if reader:
                        all_text = []
                        for idx, page in enumerate(reader.pages):
                            try:
                                t = page.extract_text()
                                if t:
                                    all_text.append(f"[p.{idx+1}] {t.strip()}")
                            except Exception:
                                pass
                        return {
                            "source": filename,
                            "pages": "全文",
                            "text": "\n\n".join(all_text),
                        }
                    else:
                        return {"source": filename, "pages": "全文", "text": ""}
                else:
                    _warn_pypdf2_missing()
                    return {"source": filename, "pages": "全文", "text": ""}
            except Exception as e:
                print(f"  ⚠️ 无法读取 PDF 全文: {filename} ({e})", file=sys.stderr)
                return {"source": filename, "pages": "全文", "text": ""}

    elif ext in (".md", ".txt"):
        text = extract_text_file(filepath)
        return {"source": filename, "pages": "全文", "text": text}

    else:
        print(f"  ⚠️ 不支持的文件类型: {filename}", file=sys.stderr)
        return {"source": filename, "pages": "", "text": ""}


# ─── 步骤 3: 主流程 — 生成上下文包 ────────────────────────────────


def build_context_packets(
    vault_path: str,
    knowledge_points: List[KnowledgePoint],
    buffer: int = 1,
) -> List[ContextPacket]:
    """为所有知识点构建上下文包"""
    packets: List[ContextPacket] = []
    total = len(knowledge_points)

    for idx, kp in enumerate(knowledge_points):
        title = kp["title"]
        note_file = kp["note_file"]
        source_ranges = kp.get("source_ranges", [])

        if not source_ranges:
            print(f"  [{idx+1}/{total}] ⚠️ {title}: 无 source_range，跳过")
            continue

        print(f"  [{idx+1}/{total}] 📄 {title}")
        excerpts: List[Excerpt] = []

        for sr in source_ranges:
            excerpt = extract_text_for_source(vault_path, sr, buffer)
            # 只保留有内容的 excerpt
            if excerpt["text"]:
                text_len = len(excerpt["text"])
                print(f"         └─ {sr['file']}: {excerpt['pages']} → {text_len} 字符")
            else:
                print(f"         └─ {sr['file']}: {excerpt['pages']} → ⚠️ 空（降级标记）")
            excerpts.append(excerpt)

        packets.append(
            {
                "note_file": note_file,
                "title": title,
                "source_excerpts": excerpts,
            }
        )

    return packets


# ─── 统计报告 ──────────────────────────────────────────────────────


def print_summary(packets: List[ContextPacket]) -> None:
    total_kp = len(packets)
    total_excerpts = sum(len(p["source_excerpts"]) for p in packets)
    total_chars = sum(
        len(e["text"]) for p in packets for e in p["source_excerpts"]
    )
    empty_excerpts = sum(
        1 for p in packets for e in p["source_excerpts"] if not e["text"]
    )
    covered_kp = sum(
        1 for p in packets if any(e["text"] for e in p["source_excerpts"])
    )

    print(f"\n📊 上下文预提取摘要")
    print(f"   知识点总数: {total_kp}")
    print(f"   已覆盖知识点: {covered_kp}/{total_kp}")
    print(f"   原文片段总数: {total_excerpts}")
    print(f"   空片段（需降级）: {empty_excerpts}")
    print(f"   提取总字符数: {total_chars:,}")

    if empty_excerpts > 0:
        print(f"\n   ⚠️ {empty_excerpts} 个原文片段为空。")
        if not _HAS_PDF:
            print(f"   修复: pip install pypdf")
        print(f"   后果: 对应的填充 agent 将降级为从头阅读全量材料。")

    if covered_kp == 0 and len(packets) > 0:
        print(f"\n   ❌ 所有知识点均无法自动提取上下文。")
        print(f"   请检查:")
        print(f"   1. 源文件是否在 vault 路径下可访问")
        print(f"   2. source_range 中的文件名拼写是否与实际一致")
        print(f"   3. pypdf 是否已安装（PDF 文件）")


# ─── 检查依赖（主入口前调用）───────────────────────────────────────


def check_dependencies(packets: List[ContextPacket]) -> None:
    """检查是否有 PDF 源文件但 PyPDF2 未安装"""
    has_pdf = any(
        e["source"].lower().endswith(".pdf")
        for p in packets
        for e in p["source_excerpts"]
    )
    if has_pdf and not _HAS_PDF:
        _warn_pypdf2_missing()


# ─── CLI 入口 ──────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="上下文预提取 — 从路线图 source_range 提取原文段落",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 context-extractor.py ~/vault "学习路线图（完整版） - 数字化转型.md" -o packets.json
  python3 context-extractor.py ~/vault roadmap.md -o packets.json --buffer 2
        """,
    )
    parser.add_argument("vault_path", help="Obsidian vault 根目录路径")
    parser.add_argument("roadmap_path", help="完整版学习路线图文件路径")
    parser.add_argument(
        "--output", "-o", required=True, help="上下文包 JSON 输出路径"
    )
    parser.add_argument(
        "--buffer",
        "-b",
        type=int,
        default=1,
        help="页码范围缓冲区（±N 页，默认 1）",
    )
    parser.add_argument(
        "--note-filter",
        help="逗号分隔的笔记文件名列表，仅提取匹配的上下文包（用于增量刷新）",
    )
    args = parser.parse_args()

    vault_path = os.path.abspath(args.vault_path)
    roadmap_path = args.roadmap_path
    if not os.path.isabs(roadmap_path):
        roadmap_path = os.path.join(vault_path, roadmap_path)

    if not os.path.exists(roadmap_path):
        print(f"❌ 路线图文件不存在: {roadmap_path}", file=sys.stderr)
        sys.exit(1)

    # 应用 note 过滤
    note_filter: Optional[Set[str]] = None
    if args.note_filter:
        note_filter = set(n.strip() for n in args.note_filter.split(","))
        print(f"🎯 按笔记过滤: {note_filter}")

    print(f"📖 上下文预提取")
    print(f"   Vault: {vault_path}")
    print(f"   路线图: {os.path.basename(roadmap_path)}")
    print(f"   缓冲区: ±{args.buffer} 页\n")

    # 步骤 1: 解析路线图
    print("🔍 解析路线图 source_range...")
    knowledge_points = parse_roadmap_source_ranges(roadmap_path)
    print(f"   找到 {len(knowledge_points)} 个知识点")
    if not knowledge_points:
        # 诊断：显示路线图中找到的粗体标题（如果有的话）
        print("   ── 诊断信息 ──")
        with open(roadmap_path, "r", encoding="utf-8") as f:
            bold_items = re.findall(r"^\*\*(.+?)\*\*", f.read(), re.MULTILINE)
        if bold_items:
            print(f"   找到 {len(bold_items)} 个粗体标题，但均无有效 source_range。")
            print(f"   前 5 个标题: {bold_items[:5]}")
            print(f"   请确认 source_range 格式：`source_range: 文件名.pdf:页码-页码`")
        else:
            print(f"   未找到任何粗体标题。路线图格式可能不兼容。")
        print(f"   ── 诊断结束 ──")

    if note_filter:
        knowledge_points = [kp for kp in knowledge_points if kp.get("note_file", "") in note_filter]
        print(f"   过滤后: {len(knowledge_points)} 个知识点")
        if not knowledge_points:
            print("   ❌ 过滤后无匹配的知识点")
            sys.exit(1)

    if not knowledge_points:
        print("   ❌ 路线图中未找到任何 source_range 标注。请检查路线图格式。")
        sys.exit(1)

    print()

    # 步骤 2: 构建上下文包
    print("📄 提取原文段落...")
    packets = build_context_packets(vault_path, knowledge_points, args.buffer)

    # 检查依赖
    check_dependencies(packets)

    # 步骤 3: 输出 JSON
    output_data = {
        "vault_path": vault_path,
        "roadmap_path": roadmap_path,
        "buffer": args.buffer,
        "total_knowledge_points": len(knowledge_points),
        "packets": packets,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print_summary(packets)
    print(f"\n✅ 上下文包已写入: {args.output}")


if __name__ == "__main__":
    main()
