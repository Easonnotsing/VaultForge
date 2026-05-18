#!/usr/bin/env python3
"""
Double-link candidate builder for Obsidian Learning.

Default behavior is conservative and review-first:

1. Scan atomic notes and generate link candidates in `link-candidates.md`.
2. Do not modify atomic notes unless `--apply` is passed.
3. With `--apply`, apply the generated candidates and roadmap-MOC links.

The note-to-note candidates are based on observable structural signals for the
five relationship types defined in SKILL.md. The script does not use full-text
bag-of-words similarity or keyword similarity alone as a reason to link notes.
"""

from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


RELATION_LABELS = {
    "derivation": "推导关系",
    "analogy": "原理相似",
    "contradiction": "结论矛盾",
    "application": "应用关联",
    "context": "背景关联",
}


@dataclass(frozen=True)
class Note:
    path: Path
    rel_path: str
    title: str
    content: str
    folder: str


@dataclass(frozen=True)
class Moc:
    path: Path
    rel_path: str
    title: str
    folder: str


@dataclass(frozen=True)
class LinkCandidate:
    source: Note
    target: Note
    relation: str
    confidence: str
    reason: str

    @property
    def target_link(self) -> str:
        return f"[[{self.target.title}]]"


def _is_auxiliary_note_file(filename: str) -> bool:
    return (
        filename == "核心问题.md"
        or filename.endswith("- 深度研究.md")
        or filename.endswith("- 争议分析.md")
    )


def discover_roadmap_theme(vault_path: str) -> Optional[str]:
    vault = Path(vault_path)
    themes: List[str] = []
    for file_path in sorted(vault.glob("学习路线图 - *.md")):
        if "完整版" in file_path.name:
            continue
        prefix = "学习路线图 - "
        if file_path.stem.startswith(prefix):
            themes.append(file_path.stem[len(prefix) :])
    if not themes:
        return None
    if len(themes) > 1:
        print(f"检测到多个大纲版路线图文件，将使用: {themes[0]}（共 {len(themes)} 个）")
    return themes[0]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _strip_markdown(content: str) -> str:
    body = re.sub(r"^---.*?---\n", "", content, flags=re.DOTALL)
    body = re.sub(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", r"\1", body)
    body = re.sub(r"#{1,6}\s+", "", body)
    body = re.sub(r"\*\*|__", "", body)
    body = re.sub(r"\*|~|`", "", body)
    return body


def get_all_notes(vault_path: str) -> List[Note]:
    vault = Path(vault_path)
    notes: List[Note] = []
    for root, dirs, files in os.walk(vault):
        dirs[:] = [name for name in dirs if not name.startswith(".")]
        for filename in files:
            if not filename.endswith(".md"):
                continue
            if "MOC" in filename or "学习路线图" in filename or _is_auxiliary_note_file(filename):
                continue
            path = Path(root) / filename
            content = _read_text(path)
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else path.stem
            rel_path = path.relative_to(vault).as_posix()
            notes.append(
                Note(
                    path=path,
                    rel_path=rel_path,
                    title=title,
                    content=_strip_markdown(content),
                    folder=str(Path(rel_path).parent).replace("\\", "/"),
                )
            )
    return notes


def get_all_mocs(vault_path: str) -> List[Moc]:
    vault = Path(vault_path)
    mocs: List[Moc] = []
    for root, dirs, files in os.walk(vault):
        dirs[:] = [name for name in dirs if not name.startswith(".")]
        for filename in files:
            if not filename.endswith(".md") or "MOC" not in filename:
                continue
            path = Path(root) / filename
            content = _read_text(path)
            title_match = re.search(r"^#\s+(.+?)(?:\s*MOC)?$", content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else filename.replace(" MOC.md", "")
            rel_path = path.relative_to(vault).as_posix()
            mocs.append(
                Moc(
                    path=path,
                    rel_path=rel_path,
                    title=title,
                    folder=str(Path(rel_path).parent).replace("\\", "/"),
                )
            )
    return mocs


def _folder_parts(folder: str) -> List[str]:
    return [part for part in folder.replace("\\", "/").strip("/").split("/") if part]


def _english_tokens(text: str) -> Set[str]:
    return set(re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower()))


def _chinese_common_phrase(a: str, b: str, min_len: int = 2) -> str:
    # Longest common substring for short note titles. This is only a topical
    # anchor, never a standalone link reason.
    best = ""
    for i in range(len(a)):
        for j in range(i + min_len, len(a) + 1):
            candidate = a[i:j]
            if len(candidate) > len(best) and candidate in b:
                best = candidate
    return best


def _title_anchor(note1: Note, note2: Note) -> Tuple[bool, str]:
    english_overlap = _english_tokens(note1.title) & _english_tokens(note2.title)
    if english_overlap:
        return True, "标题共享英文主题词: " + ", ".join(sorted(english_overlap))

    phrase = _chinese_common_phrase(note1.title, note2.title)
    if phrase:
        return True, f"标题共享中文主题片段: {phrase}"

    if _title_cited_in_other(note1, note2):
        return True, "一篇笔记正文显式提到另一篇笔记标题"

    return False, ""


def _title_cited_in_other(note1: Note, note2: Note) -> bool:
    title1, title2 = note1.title.strip(), note2.title.strip()
    return (
        len(title1) >= 2
        and title1 in note2.content
        or len(title2) >= 2
        and title2 in note1.content
    )


def _count_lexemes(text: str, lexemes: Sequence[str]) -> int:
    lowered = text.lower()
    return sum(1 for word in lexemes if word.lower() in lowered)


def _same_folder(note1: Note, note2: Note) -> bool:
    return note1.folder == note2.folder


def _same_h2_different_h3(note1: Note, note2: Note) -> bool:
    p1, p2 = _folder_parts(note1.folder), _folder_parts(note2.folder)
    return len(p1) >= 2 and len(p2) >= 2 and p1[0] == p2[0] and p1[1] != p2[1]


def _folder_topic_cited(note1: Note, note2: Note) -> bool:
    topics = []
    for note in (note1, note2):
        parts = _folder_parts(note.folder)
        if len(parts) >= 2:
            topics.append(parts[1])
    return any(topic and (topic in note1.content or topic in note2.content) for topic in topics)


def find_relationships(note1: Note, note2: Note) -> List[Tuple[str, str, str]]:
    relationships: List[Tuple[str, str, str]] = []
    if note1.path == note2.path:
        return relationships
    topical_anchor = _title_topic_overlap(note1, note2) or _title_cited_in_other(
        note1, note2
    )

    combined = note1.content + "\n" + note2.content
    has_anchor, anchor_reason = _title_anchor(note1, note2)

    derivation_lexemes = (
        "因此",
        "所以",
        "从而",
        "导致",
        "结果表明",
        "得出结论",
        "由此可见",
        "证明",
        "推导",
        "意味着",
        "therefore",
        "thus",
        "consequently",
        "implies",
        "it follows",
    )
    if has_anchor and _count_lexemes(combined, derivation_lexemes) >= 2:
        relationships.append(("derivation", "high", f"{anchor_reason}；出现多个因果/推论表达"))

    analogy_lexemes = (
        "类比",
        "类似于",
        "类似",
        "同理",
        "正如",
        "好比",
        "异曲同工",
        "analogous",
        "similarly",
        "likewise",
        "by analogy",
        "comparable to",
    )
    if has_anchor and _count_lexemes(combined, analogy_lexemes) >= 1:
        relationships.append(("analogy", "medium", f"{anchor_reason}；出现类比/平行说理表达"))

    contradiction_lexemes = (
        "但是",
        "然而",
        "相反",
        "不同于",
        "矛盾",
        "对立",
        "争议",
        "however",
        "nevertheless",
        "unlike",
        "contradict",
        "tension between",
    )
    if has_anchor and _count_lexemes(combined, contradiction_lexemes) >= 2:
        relationships.append(("contradiction", "medium", f"{anchor_reason}；出现多个转折/对立表达"))

    application_lexemes = (
        "应用",
        "适用于",
        "用于",
        "借助",
        "基于",
        "运用",
        "实践",
        "落地",
        "实施",
        "部署",
        "apply",
        "application of",
        "used for",
    )
    if _same_folder(note1, note2) and has_anchor and _count_lexemes(combined, application_lexemes) >= 1:
        relationships.append(("application", "medium", f"{anchor_reason}；同主题文件夹且出现应用/实践表达"))

    context_lexemes = (
        "背景",
        "阶段",
        "发展",
        "演进",
        "历史",
        "时期",
        "维度",
        "视角",
        "层面",
        "语境",
        "context",
        "phase",
        "historically",
    )
    if (
        _same_h2_different_h3(note1, note2)
        and (has_anchor or _folder_topic_cited(note1, note2))
        and _count_lexemes(combined, context_lexemes) >= 1
    ):
        reason = anchor_reason or "正文提到对方主题文件夹"
        relationships.append(("context", "low", f"{reason}；同 H2 不同 H3 且出现背景/阶段/视角表达"))

    return relationships


def build_link_candidates(notes: List[Note]) -> List[LinkCandidate]:
    candidates: List[LinkCandidate] = []
    seen_pairs: Set[Tuple[str, str]] = set()

    for index, note1 in enumerate(notes):
        for note2 in notes[index + 1 :]:
            relationships = find_relationships(note1, note2)
            if not relationships:
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

            relation, confidence, reason = relationships[0]
            pair_key = tuple(sorted((note1.rel_path, note2.rel_path)))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            source, target = _choose_source_target(note1, note2)
            candidates.append(
                LinkCandidate(
                    source=source,
                    target=target,
                    relation=relation,
                    confidence=confidence,
                    reason=reason,
                )
            )

    return candidates


def _choose_source_target(note1: Note, note2: Note) -> Tuple[Note, Note]:
    # Prefer linking from the note that mentions the other title. If neither
    # does, use stable path order.
    if note2.title in note1.content and note1.title not in note2.content:
        return note1, note2
    if note1.title in note2.content and note2.title not in note1.content:
        return note2, note1
    return (note1, note2) if note1.rel_path <= note2.rel_path else (note2, note1)


def _candidate_markdown(candidates: List[LinkCandidate], vault_path: str) -> str:
    lines = [
        "# 双链候选 - 主 Agent 确认清单",
        "",
        "> 本文件由 `scripts/double-link-builder.py` 生成。默认不修改原子笔记。",
        "> 主 Agent 应逐条确认候选是否符合 SKILL.md 的五类逻辑关系，再手动应用或运行 `--apply`。",
        "",
        f"Vault: `{vault_path}`",
        f"候选数量: {len(candidates)}",
        "",
    ]

    if not candidates:
        lines.append("未发现满足结构化条件的笔记间双链候选。")
        lines.append("")
        return "\n".join(lines)

    for index, candidate in enumerate(candidates, start=1):
        label = RELATION_LABELS[candidate.relation]
        lines.extend(
            [
                f"## {index}. {candidate.source.title} -> {candidate.target.title}",
                "",
                f"- 状态：待主 Agent 确认",
                f"- 关系类型：{label}",
                f"- 置信度：{candidate.confidence}",
                f"- 来源笔记：`{candidate.source.rel_path}`",
                f"- 目标笔记：`{candidate.target.rel_path}`",
                f"- 建议写入：`- [[{candidate.target.title}]]`",
                f"- 判定理由：{candidate.reason}",
                "",
            ]
        )
    return "\n".join(lines)


def write_link_candidates(vault_path: str, candidates: List[LinkCandidate], output_name: str) -> Path:
    output_path = Path(vault_path) / output_name
    output_path.write_text(_candidate_markdown(candidates, vault_path), encoding="utf-8")
    return output_path


def _has_wikilink(content: str, title: str) -> bool:
    return f"[[{title}]]" in content or f"[[{title}|" in content


def apply_link_candidates(candidates: List[LinkCandidate]) -> int:
    updated_paths: Set[Path] = set()
    by_source: Dict[Path, List[LinkCandidate]] = {}
    for candidate in candidates:
        by_source.setdefault(candidate.source.path, []).append(candidate)

    for source_path, source_candidates in by_source.items():
        content = _read_text(source_path)
        missing = [c for c in source_candidates if not _has_wikilink(content, c.target.title)]
        if not missing:
            continue

        lines = [f"- [[{c.target.title}]]" for c in missing]
        if "## 相关笔记" in content:
            content = content.rstrip() + "\n" + "\n".join(lines) + "\n"
        else:
            content = content.rstrip() + "\n\n## 相关笔记\n\n" + "\n".join(lines) + "\n"

        source_path.write_text(content, encoding="utf-8")
        updated_paths.add(source_path)

    return len(updated_paths)


def build_roadmap_moc_links(vault_path: str, roadmap_name: str, mocs: List[Moc], apply: bool) -> int:
    roadmap_path = Path(vault_path) / f"学习路线图 - {roadmap_name}.md"
    if not roadmap_path.exists():
        print(f"路线图文件不存在: {roadmap_path}")
        return 0

    roadmap_content = _read_text(roadmap_path)
    updated_count = 0

    for moc in mocs:
        moc_title = moc.title
        pattern = rf"(^###\s+{re.escape(moc_title)}\s*$)"
        link_target = moc.rel_path.replace(".md", "")
        link_line = f"[[{link_target}|{moc_title}]]"

        if link_target not in roadmap_content.replace("\\", "/") and re.search(pattern, roadmap_content, re.MULTILINE):
            roadmap_content = re.sub(pattern, rf"\1\n\n{link_line}", roadmap_content, count=1, flags=re.MULTILINE)
            updated_count += 1

        moc_content = _read_text(moc.path)
        roadmap_link = f"[[../../学习路线图 - {roadmap_name}|学习路线图]]"
        if roadmap_link not in moc_content:
            if "## 相关笔记" not in moc_content:
                moc_content = moc_content.rstrip() + f"\n\n## 相关笔记\n\n- {roadmap_link}\n"
            else:
                moc_content = moc_content.rstrip() + f"\n- {roadmap_link}\n"
            if apply:
                moc.path.write_text(moc_content, encoding="utf-8")
            updated_count += 1

    if apply:
        roadmap_path.write_text(roadmap_content, encoding="utf-8")

    return updated_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate reviewable Obsidian note link candidates; apply only with --apply."
    )
    parser.add_argument("vault_path", help="Obsidian vault path")
    parser.add_argument(
        "roadmap_name",
        nargs="?",
        help="Name between `学习路线图 - ` and `.md`; auto-detected when omitted.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply generated note candidates and roadmap-MOC links. Use only after main Agent review.",
    )
    parser.add_argument(
        "--candidates-file",
        default="link-candidates.md",
        help="Candidate markdown file written at the vault root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    vault_path = args.vault_path
    roadmap_name = args.roadmap_name or discover_roadmap_theme(vault_path)
    if not roadmap_name:
        print("错误: 未找到大纲版「学习路线图 - *.md」。请显式传入 roadmap_name。")
        return 1

    print("开始扫描 Obsidian vault")
    print(f"Vault: {vault_path}")

    notes = get_all_notes(vault_path)
    mocs = get_all_mocs(vault_path)
    candidates = build_link_candidates(notes)
    candidates_path = write_link_candidates(vault_path, candidates, args.candidates_file)

    print(f"原子笔记: {len(notes)}")
    print(f"MOC: {len(mocs)}")
    print(f"候选双链: {len(candidates)}")
    print(f"候选清单: {candidates_path}")

    if args.apply:
        note_updates = apply_link_candidates(candidates)
        roadmap_updates = build_roadmap_moc_links(vault_path, roadmap_name, mocs, apply=True)
        print("已应用候选双链与路线图-MOC 链接")
        print(f"更新原子笔记: {note_updates}")
        print(f"路线图/MOC 更新项: {roadmap_updates}")
    else:
        build_roadmap_moc_links(vault_path, roadmap_name, mocs, apply=False)
        print("默认模式未修改原子笔记或路线图。请由主 Agent 审查候选后再应用。")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
