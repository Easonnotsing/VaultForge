#!/usr/bin/env python3
"""
双链构建脚本 (v2) - VaultForge

三阶段漏斗策略：
  阶段1: 结构化亲和过滤 — 目录层级、H2/H3 归属关系（零成本，消去 ~80% 无关对）
  阶段2: TF-IDF 语义相似 + 关键词启发式 — 高分候选筛选（低成本，无外部依赖）
  阶段3: 候选对输出 → 由主 Agent 的 LLM 做最终五类关系分类

用法:
  # 完整模式（输出候选对供 LLM 分类）
  python3 double-link-builder.py <folder_path> <roadmap_name> --output candidates.json

  # 严格模式（仅确定性规则，不输出候选对）
  python3 double-link-builder.py <folder_path> <roadmap_name> --mode strict

  # 同时产出确定性链接和候选对
  python3 double-link-builder.py <folder_path> <roadmap_name> --output candidates.json --mode strict

  # 增量模式（新笔记间的链接直接写入；新→旧仅输出建议 JSON）
  python3 double-link-builder.py <folder_path> <roadmap_name> --mode incremental --new-notes new_notes.json --output-suggestions suggestions.json

<folder_path>: 学习材料所在文件夹路径（非 Obsidian vault 根目录）。脚本递归扫描此路径下的所有 .md 文件。
roadmap_name 为此文件夹下「学习路线图 v1 - {roadmap_name}.md」中 {roadmap_name} 一段；
"""

import argparse
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ─── TF-IDF 轻量实现（零外部依赖） ────────────────────────────────


def tokenize(text: str) -> List[str]:
    """中英文混合分词：中文按2-gram切分，英文按空格+词干切分"""
    tokens: List[str] = []
    # 中文部分：2-gram 滑动窗口
    chinese_chars = "".join(re.findall(r"[\u4e00-\u9fff]+", text))
    for i in range(len(chinese_chars) - 1):
        tokens.append(chinese_chars[i : i + 2])
    # 英文部分：词级别
    english_words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    tokens.extend(w for w in english_words if w not in _STOP_WORDS)
    # 数字/专有名词
    tokens.extend(re.findall(r"\d{2,}", text))
    return tokens


_STOP_WORDS: Set[str] = {
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
    "her", "was", "one", "our", "out", "has", "have", "from", "that",
    "this", "with", "were", "which", "their", "will", "each", "about",
    "many", "some", "would", "other", "into", "more", "these",
}


class TfidfIndex:
    """极小 TF-IDF 索引，无外部依赖"""

    def __init__(self):
        self.doc_count = 0
        self.df: Counter = Counter()  # document frequency
        self.doc_vectors: Dict[int, Dict[int, float]] = {}

    def add_document(self, doc_id: int, tokens: List[str]) -> None:
        unique_tokens = set(tokens)
        for t in unique_tokens:
            self.df[t] += 1
        self.doc_count += 1

    def finalize(self) -> None:
        self.idf = {
            t: math.log((self.doc_count + 1) / (df + 1)) + 1.0
            for t, df in self.df.items()
        }

    def vectorize(self, doc_id: int, tokens: List[str]) -> Dict[int, float]:
        tf = Counter(tokens)
        total = len(tokens) or 1
        vec: Dict[int, float] = {}
        for t, count in tf.items():
            if t in self.idf:
                vec[hash(t)] = (count / total) * self.idf[t]
        return vec

    @staticmethod
    def cosine(v1: Dict[int, float], v2: Dict[int, float]) -> float:
        common = set(v1.keys()) & set(v2.keys())
        if not common:
            return 0.0
        dot = sum(v1[k] * v2[k] for k in common)
        mag1 = math.sqrt(sum(x * x for x in v1.values()))
        mag2 = math.sqrt(sum(x * x for x in v2.values()))
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot / (mag1 * mag2)


# ─── 辅助函数 ──────────────────────────────────────────────────────


def _is_auxiliary_note_file(filename: str) -> bool:
    if filename == "核心问题.md":
        return True
    if filename.endswith("- 深度研究.md"):
        return True
    if filename.endswith("- 争议分析.md"):
        return True
    return False


def _folder_parts(folder: str) -> List[str]:
    n = folder.replace("\\", "/").strip("/")
    return [p for p in n.split("/") if p]


def _title_tokens(title: str) -> Set[str]:
    t = title.strip().lower()
    return set(re.findall(r"[一-龥]{2,}|[a-zA-Z]{3,}|\d+", t))


def _title_topic_overlap(note1: Dict, note2: Dict) -> bool:
    a, b = _title_tokens(note1["title"]), _title_tokens(note2["title"])
    return len(a & b) >= 1


def _title_cited_in_other(note1: Dict, note2: Dict) -> bool:
    t1, t2 = note1["title"].strip(), note2["title"].strip()
    if len(t1) >= 2 and t1 in note2.get("content", ""):
        return True
    if len(t2) >= 2 and t2 in note1.get("content", ""):
        return True
    return False


def _count_lexemes(text: str, lexemes: Tuple[str, ...]) -> int:
    return sum(1 for w in lexemes if w in text)


def discover_roadmap_theme(vault_path: str) -> Optional[str]:
    vault = Path(vault_path)
    themes: List[str] = []
    for f in sorted(vault.glob("学习路线图 - *.md")):
        if "完整版" in f.name:
            continue
        stem = f.stem
        prefix = "学习路线图 - "
        if stem.startswith(prefix):
            themes.append(stem[len(prefix):])
    if not themes:
        return None
    if len(themes) > 1:
        print(f"⚠️ 检测到多个大纲版路线图文件，将使用: {themes[0]}（共 {len(themes)} 个）")
    return themes[0]


# ─── 数据获取 ──────────────────────────────────────────────────────


def get_all_notes(vault_path: str) -> List[Dict]:
    notes = []
    for root, dirs, files in os.walk(vault_path):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if f.endswith(".md") and "MOC" not in f and "学习路线图" not in f:
                if _is_auxiliary_note_file(f):
                    continue
                path = os.path.join(root, f)
                rel_path = os.path.relpath(path, vault_path)
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
                title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                title = title_match.group(1) if title_match else f
                # 去除 frontmatter 和 markdown 格式后的纯文本（用于 TF-IDF）
                body = re.sub(r"^---.*?---\n", "", content, flags=re.DOTALL)
                clean_body = re.sub(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", r"\1", body)
                clean_body = re.sub(r"#{1,6}\s+", "", clean_body)
                clean_body = re.sub(r"\*\*|__|\*|~|`", "", clean_body)
                # 提取前 300 字符作为预览（给 LLM 用的摘要）
                preview = clean_body.strip()[:300]
                notes.append(
                    {
                        "path": path,
                        "rel_path": rel_path,
                        "title": title,
                        "content": clean_body,
                        "preview": preview,
                        "folder": os.path.dirname(rel_path),
                    }
                )
    return notes


def get_all_mocs(vault_path: str) -> List[Dict]:
    mocs = []
    for root, dirs, files in os.walk(vault_path):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if f.endswith(".md") and "MOC" in f:
                path = os.path.join(root, f)
                rel_path = os.path.relpath(path, vault_path)
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
                title_match = re.search(
                    r"^#\s+(.+?)(?:\s*MOC)?$", content, re.MULTILINE
                )
                title = (
                    title_match.group(1).strip()
                    if title_match
                    else f.replace(" MOC.md", "")
                )
                mocs.append(
                    {
                        "path": path,
                        "rel_path": rel_path,
                        "title": title,
                        "folder": os.path.dirname(rel_path),
                    }
                )
    return mocs


# ─── 阶段1: 结构化亲和 ────────────────────────────────────────────


def structural_affinity(note1: Dict, note2: Dict) -> float:
    """
    基于目录层级计算亲和力得分 (0.0 ~ 1.0)。
    同一 H3 文件夹 → 高亲和；同一 H2 类别不同 H3 → 中亲和；其他 → 0。
    """
    f1, f2 = note1["folder"], note2["folder"]
    if f1 == f2:
        return 1.0  # 同一 H3 主题文件夹
    p1 = _folder_parts(f1)
    p2 = _folder_parts(f2)
    if len(p1) >= 2 and len(p2) >= 2 and p1[0] == p2[0]:
        return 0.5  # 同一 H2 类别，不同 H3
    return 0.0


# ─── 阶段2: 关键词启发式关系检测（保持原有逻辑）──────────────────


def find_relationships_heuristic(
    note1: Dict, note2: Dict
) -> List[Tuple[str, str]]:
    """按五类逻辑关系做关键词判定（每类需多项条件同时成立）"""
    relationships: List[Tuple[str, str]] = []
    content1, content2 = note1["content"], note2["content"]
    combined = content1 + "\n" + content2
    if note1["path"] == note2["path"]:
        return relationships
    topical_anchor = _title_topic_overlap(note1, note2) or _title_cited_in_other(
        note1, note2
    )

    derivation_lexemes = (
        "因此", "所以", "从而", "导致", "结果表明", "得出结论",
        "由此可见", "证明", "推导", "意味着", "可见",
        "hence", "therefore", "thus", "consequently", "implies", "it follows",
    )
    if _count_lexemes(combined, derivation_lexemes) >= 2 and topical_anchor:
        relationships.append(("derivation", "推导关系"))

    analogy_lexemes = (
        "类比", "类似于", "类似", "同理", "正如", "好比",
        "比照", "异曲同工", "parallel", "analogous", "similarly",
        "likewise", "by analogy", "comparable to",
    )
    if _count_lexemes(combined, analogy_lexemes) >= 1 and topical_anchor:
        relationships.append(("analogy", "原理相似"))

    contradiction_lexemes = (
        "但是", "然而", "相反", "不同于", "矛盾", "对立", "争议",
        "however", "nevertheless", "unlike", "contradict", "tension between",
    )
    if _count_lexemes(combined, contradiction_lexemes) >= 2 and _title_topic_overlap(
        note1, note2
    ):
        relationships.append(("contradiction", "结论矛盾"))

    same_folder = note1["folder"] == note2["folder"]
    application_lexemes = (
        "应用", "适用于", "用于", "借助", "基于", "运用",
        "实践", "落地", "实施", "部署", "apply",
        "application of", "used for",
    )
    if same_folder and _count_lexemes(combined, application_lexemes) >= 1 and topical_anchor:
        relationships.append(("application", "应用关联"))

    p1, p2 = _folder_parts(note1["folder"]), _folder_parts(note2["folder"])
    same_h2_diff_h3 = (
        len(p1) >= 2
        and len(p2) >= 2
        and p1[0] == p2[0]
        and p1[1] != p2[1]
    )
    context_lexemes = (
        "背景", "阶段", "发展", "演进", "历史", "时期",
        "维度", "视角", "层面", "语境",
        "context", "phase", "historically",
    )
    if same_h2_diff_h3 and _count_lexemes(combined, context_lexemes) >= 1:
        relationships.append(("context", "背景关联"))

    return relationships


# ─── 阶段3: 候选对生成（供 LLM 分类） ──────────────────────────────


def generate_candidates(
    notes: List[Dict],
    tfidf_index: TfidfIndex,
    doc_tokens: Dict[int, List[str]],
    doc_id_map: Dict[str, int],
    structural_threshold: float = 0.5,
    tfidf_threshold: float = 0.15,
) -> List[Dict]:
    """
    对阶段 1+2 仍为"无链接"的笔记对，检查是否应提升为 LLM 候选：

    - 阶段1: structural_affinity >= structural_threshold（同一 H3 或同一 H2 类别）
    - 阶段2: TF-IDF cosine >= tfidf_threshold

    两者同时满足的笔记对 → candidates.json 输出
    """
    candidates: List[Dict] = []
    seen: Set[Tuple[str, str]] = set()

    for i, note_a in enumerate(notes):
        for j, note_b in enumerate(notes):
            if i >= j:
                continue
            # 检查结构化亲和
            aff = structural_affinity(note_a, note_b)
            if aff < structural_threshold:
                continue
            # 计算 TF-IDF 相似度
            id_a = doc_id_map.get(note_a["rel_path"])
            id_b = doc_id_map.get(note_b["rel_path"])
            if id_a is None or id_b is None:
                continue
            vec_a = tfidf_index.vectorize(id_a, doc_tokens.get(id_a, []))
            vec_b = tfidf_index.vectorize(id_b, doc_tokens.get(id_b, []))
            cosine = TfidfIndex.cosine(vec_a, vec_b)
            if cosine < tfidf_threshold:
                continue
            # 检查是否已被关键词启发式覆盖
            heuristic_hits = find_relationships_heuristic(note_a, note_b)
            keyword_score = len(heuristic_hits)
            # 生成候选（即使关键词已有部分命中，仍作为候选以提升覆盖率）
            candidates.append(
                {
                    "note_a": note_a["rel_path"],
                    "note_b": note_b["rel_path"],
                    "title_a": note_a["title"],
                    "title_b": note_b["title"],
                    "scores": {
                        "structural": aff,
                        "tfidf_cosine": round(cosine, 4),
                        "keyword_rules": keyword_score,
                    },
                    "preview_a": note_a["preview"],
                    "preview_b": note_b["preview"],
                }
            )
    # 按综合得分排序（structural + tfidf + keyword）
    candidates.sort(
        key=lambda c: c["scores"]["structural"] * 2.0
        + c["scores"]["tfidf_cosine"]
        + c["scores"]["keyword_rules"] * 0.5,
        reverse=True,
    )
    return candidates


# ─── 确定性链接写入（strict 模式） ─────────────────────────────────


def build_note_to_note_links(notes: List[Dict]) -> Dict[str, List[str]]:
    links: Dict[str, List[str]] = {}
    for note1 in notes:
        links[note1["rel_path"]] = []
        for note2 in notes:
            if note1["path"] >= note2["path"]:
                continue
            rels = find_relationships_heuristic(note1, note2)
            if rels:
                links[note1["rel_path"]].append(note2["title"])
    return links


def add_links_to_notes(vault_path: str, note_links: Dict[str, List[str]]) -> int:
    updated = 0
    for rel_path, linked_notes in note_links.items():
        if not linked_notes:
            continue
        full_path = os.path.join(vault_path, rel_path)
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        missing = [
            n
            for n in linked_notes
            if f"[[{n}]]" not in content and f"[[{n}|" not in content
        ]
        if not missing:
            continue
        append_block = "\n".join(f"- [[{note}]]" for note in missing)
        if "## 相关笔记" in content:
            content = content.rstrip() + "\n" + append_block + "\n"
        else:
            content = (
                content.rstrip()
                + f"\n## 相关笔记\n\n{append_block}\n"
            )
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        updated += 1
    return updated


def build_roadmap_moc_links(
    vault_path: str, roadmap_name: str, mocs: List[Dict]
) -> int:
    roadmap_path = os.path.join(vault_path, f"学习路线图 - {roadmap_name}.md")
    if not os.path.exists(roadmap_path):
        print(f"⚠️ 路线图文件不存在: {roadmap_path}")
        return 0
    with open(roadmap_path, "r", encoding="utf-8") as f:
        roadmap_content = f.read()
    updated_mocs = 0
    for moc in mocs:
        moc_title = moc["title"]
        pattern = rf"(^###\s+{re.escape(moc_title)}\s*$)"
        link_target = moc["rel_path"].replace(".md", "").replace("\\", "/")
        link_line = f"[[{link_target}|{moc_title}]]"
        if link_target not in roadmap_content.replace("\\", "/"):
            if re.search(pattern, roadmap_content, re.MULTILINE):
                replacement = rf"\1\n\n{link_line}"
                roadmap_content = re.sub(
                    pattern, replacement, roadmap_content, count=1, flags=re.MULTILINE
                )
        moc_rel_path = moc["rel_path"]
        with open(os.path.join(vault_path, moc_rel_path), "r", encoding="utf-8") as f:
            moc_content = f.read()
        if f"[[../../学习路线图 - {roadmap_name}" not in moc_content:
            if "## 相关笔记" not in moc_content:
                new_section = f"\n## 相关笔记\n\n- [[../../学习路线图 - {roadmap_name}|学习路线图]]\n"
                moc_content = moc_content.rstrip() + new_section
            else:
                moc_content = (
                    moc_content.rstrip()
                    + f"\n- [[../../学习路线图 - {roadmap_name}|学习路线图]]\n"
                )
            with open(os.path.join(vault_path, moc_rel_path), "w", encoding="utf-8") as f:
                f.write(moc_content)
            updated_mocs += 1
    with open(roadmap_path, "w", encoding="utf-8") as f:
        f.write(roadmap_content)
    return updated_mocs


def estimate_coverage(
    notes: List[Dict], heuristic_links: Dict[str, List[str]]
) -> float:
    """估算关键词启发式的覆盖率：对数线性推估"""
    total_pairs = len(notes) * (len(notes) - 1) / 2
    heuristic_pairs = sum(len(v) for v in heuristic_links.values())
    # 每对笔记至少 1 条链接 → 大概率的逻辑关联上限约 10-15%
    realistic_links = total_pairs * 0.12
    if realistic_links == 0:
        return 0.0
    return min(1.0, heuristic_pairs / realistic_links)


# ─── Main ──────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="VaultForge v2")
    parser.add_argument("vault_path", help="Vault 根目录路径")
    parser.add_argument(
        "roadmap_name",
        nargs="?",
        help="路线图主题名（可选，自动从 vault 根目录检测）",
    )
    parser.add_argument(
        "--output", "-o", help="候选对 JSON 输出路径（用于 LLM 阶段 3）"
    )
    parser.add_argument(
        "--mode",
        choices=["full", "strict", "incremental"],
        default="full",
        help="full=输出候选对+确定性链接; strict=仅确定性链接; incremental=新笔记间写入链接+新→旧输出建议",
    )
    parser.add_argument(
        "--new-notes",
        help="增量模式下新笔记路径的 JSON 文件（含相对路径列表）",
    )
    parser.add_argument(
        "--output-suggestions",
        help="增量模式下新→旧建议链接的 JSON 输出路径",
    )
    parser.add_argument(
        "--tfidf-threshold",
        type=float,
        default=0.15,
        help="TF-IDF 余弦相似度阈值（默认 0.15）",
    )
    parser.add_argument(
        "--structural-threshold",
        type=float,
        default=0.5,
        help="结构化亲和力阈值（默认 0.5，即同一 H2 类别即可）",
    )
    args = parser.parse_args()

    vault_path = args.vault_path
    roadmap_name: Optional[str] = args.roadmap_name
    if not roadmap_name:
        roadmap_name = discover_roadmap_theme(vault_path)
    if not roadmap_name:
        print(
            "错误: 未找到大纲版「学习路线图 - *.md」，或无法解析主题名。\n"
            "请显式传入第 2 参数 roadmap_name。"
        )
        sys.exit(1)

    print(f"🔗 双链构建 v2 — 三阶段漏斗")
    print(f"   Vault: {vault_path}")
    print(f"   模式: {args.mode}")

    # 获取所有笔记和 MOC
    print("\n📚 扫描笔记...")
    notes = get_all_notes(vault_path)
    print(f"   找到 {len(notes)} 个原子笔记")
    mocs = get_all_mocs(vault_path)
    print(f"   找到 {len(mocs)} 个 MOC")

    # ─── 阶段1: 报告结构化亲和统计 ───
    total_pairs = len(notes) * (len(notes) - 1) // 2
    affinity_pairs = 0
    for i, n1 in enumerate(notes):
        for j, n2 in enumerate(notes):
            if i >= j:
                continue
            if structural_affinity(n1, n2) >= args.structural_threshold:
                affinity_pairs += 1
    print(f"\n🔍 阶段1 结构化过滤: {affinity_pairs}/{total_pairs} 对通过 "
          f"({affinity_pairs/max(total_pairs,1)*100:.1f}%)")

    # ─── 阶段2: TF-IDF 索引构建 ───
    print("\n📊 阶段2 构建 TF-IDF 索引...")
    tfidf = TfidfIndex()
    doc_tokens: Dict[int, List[str]] = {}
    doc_id_map: Dict[str, int] = {}
    for idx, note in enumerate(notes):
        tokens = tokenize(note["content"])
        doc_tokens[idx] = tokens
        doc_id_map[note["rel_path"]] = idx
        tfidf.add_document(idx, tokens)
    tfidf.finalize()
    print(f"   词表大小: {len(tfidf.df)}")

    # ─── 阶段2: 关键词启发式链接 ───
    print("\n🔗 阶段2 关键词启发式检测...")
    note_links = build_note_to_note_links(notes)
    total_heuristic = sum(len(v) for v in note_links.values())
    coverage = estimate_coverage(notes, note_links)
    print(f"   启发式命中: {total_heuristic} 个链接（预估覆盖率 ~{coverage*100:.0f}%）")

    # ─── 阶段3: 候选对生成 ───
    if args.output:
        print("\n🎯 阶段3 生成 LLM 候选对...")
        candidates = generate_candidates(
            notes,
            tfidf,
            doc_tokens,
            doc_id_map,
            structural_threshold=args.structural_threshold,
            tfidf_threshold=args.tfidf_threshold,
        )
        output_data = {
            "vault_path": vault_path,
            "roadmap_name": roadmap_name,
            "total_notes": len(notes),
            "total_pairs": total_pairs,
            "affinity_pairs": affinity_pairs,
            "heuristic_links": total_heuristic,
            "estimated_coverage": round(coverage, 2),
            "candidate_count": len(candidates),
            "candidates": candidates,
        }
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"   候选对: {len(candidates)} → 已写入 {args.output}")
        print(f"   预估 LLM 总覆盖率: ~{min(1.0, coverage + len(candidates)*0.3/max(total_pairs,1)):.0%}")
        if len(candidates) > 200:
            print(f"   ⚠️ 候选对较多 ({len(candidates)})，建议调高 --tfidf-threshold 减少 LLM 调用")

    # ─── 增量模式：新笔记间写入链接，新→旧仅输出建议 ───
    incremental_new: Set[str] = set()
    if args.mode == "incremental":
        if not args.new_notes:
            print("错误: 增量模式需要 --new-notes 参数")
            sys.exit(1)
        with open(args.new_notes, "r", encoding="utf-8") as f:
            incremental_new = set(json.load(f))
        print(f"\n📦 增量模式: {len(incremental_new)} 个新笔记")

    # ─── 确定性链接写入 ───
    if args.mode == "strict":
        print("\n✏️ 写入确定性链接（strict 模式）...")
        updated = add_links_to_notes(vault_path, note_links)
        print(f"   更新了 {updated} 个笔记")

    elif args.mode == "incremental":
        print("\n✏️ 增量模式: 新笔记间写入链接...")
        new_links: Dict[str, List[str]] = {}
        old_to_new_suggestions: List[Dict] = []
        # 分离新→新和新→旧
        for note_path, targets in note_links.items():
            note_in_new = note_path in incremental_new
            new_targets = [t for t in targets if t in incremental_new]
            old_targets = [t for t in targets if t not in incremental_new]
            if note_in_new and new_targets:
                new_links[note_path] = new_targets
            if note_in_new and old_targets:
                for t in old_targets:
                    old_to_new_suggestions.append({
                        "from": note_path,
                        "to": t,
                    })
        updated = add_links_to_notes(vault_path, new_links)
        print(f"   新笔记间写入: {sum(len(v) for v in new_links.values())} 个链接（{updated} 个笔记）")
        print(f"   新→旧建议: {len(old_to_new_suggestions)} 个（未写入，等待用户确认）")
        if args.output_suggestions:
            with open(args.output_suggestions, "w", encoding="utf-8") as f:
                json.dump(old_to_new_suggestions, f, ensure_ascii=False, indent=2)
            print(f"   建议已写入 {args.output_suggestions}")

    # ─── 路线图 ↔ MOC 双向链接（与模式无关，始终执行） ───
    print("\n📋 建立路线图与 MOC 双向链接...")
    moc_updated = build_roadmap_moc_links(vault_path, roadmap_name, mocs)
    print(f"   更新了 {moc_updated} 个 MOC")

    print("\n✅ 双链构建完成！")
    print(f"   - 关键词启发式链接: {total_heuristic}（预估覆盖率 ~{coverage*100:.0f}%）")
    if args.output:
        print(f"   - LLM 候选对: {len(candidates) if args.output else 0} → {args.output}")
    print(f"   - 路线图-MOC 双向链接: {moc_updated * 2}")


if __name__ == "__main__":
    main()
