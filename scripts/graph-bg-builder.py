#!/usr/bin/env python3
"""
分享卡图谱背景生成器

从 VaultForge 生成的知识库中读取真实的文件夹结构和笔记，
构建节点-边图谱 SVG，模拟 Obsidian Graph View 风格。
"""

import os, re, sys, json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set


def collect_notes(vault_folder: str) -> List[Dict]:
    """收集所有原子笔记的信息"""
    root = Path(vault_folder)
    notes = []
    for md in sorted(root.rglob("*.md")):
        if "MOC" in md.name or "Roadmap" in md.name or "Research" in md.name:
            continue
        rel = str(md.relative_to(root))
        depth = rel.count(os.sep)
        content = md.read_text(encoding="utf-8")
        title_match = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
        h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = (
            title_match.group(1).strip()
            if title_match
            else h1_match.group(1).strip() if h1_match else md.stem
        )
        notes.append({
            "title": title,
            "path": rel,
            "depth": depth,
            "parent": str(Path(rel).parent) if depth > 0 else "",
        })
    return notes


def build_graph(notes: List[Dict]) -> Tuple[List[Tuple[str, str, str]], List[Dict]]:
    """从文件夹结构和字段相似性构造链接"""
    edges = []
    seen = set()
    # 同 folder 的笔记自动建立弱链接
    by_parent = defaultdict(list)
    for n in notes:
        by_parent[n["parent"]].append(n["title"])

    for parent, siblings in by_parent.items():
        for i, a in enumerate(siblings):
            # 直接兄弟节点 (derivation)
            for b in siblings[i + 1 :]:
                key = tuple(sorted([a, b]))
                if key not in seen:
                    seen.add(key)
                    edges.append((a, b, "derivation"))
            # 相邻父节点间的连接 (context)
            # 只连接最近的两个 chunk
            if i + 1 < len(siblings) - 1:
                pass
    # 跨文件夹字段相似 (analogy) —— 基于标题关键词
    # 包含相同核心词的
    keywords = Counter()
    for n in notes:
        for w in re.findall(r"[\w\u4e00-\u9fff]{2,}", n["title"]):
            keywords[w.lower()] += 1
    common_kw = {w for w, c in keywords.most_common(30)}

    for i, a in enumerate(notes):
        at = set(re.findall(r"[\w\u4e00-\u9fff]{2,}", a["title"].lower()))
        for j, b in enumerate(notes):
            if i >= j:
                continue
            bt = set(re.findall(r"[\w\u4e00-\u9fff]{2,}", b["title"].lower()))
            overlap = at & bt & common_kw
            if overlap and a.get("parent") != b.get("parent"):
                key = tuple(sorted([a["title"], b["title"]]))
                if key not in seen:
                    seen.add(key)
                    edges.append((a["title"], b["title"], "analogy"))
    return edges, notes


def layout_graph(
    notes: List[Dict], edges: List[Tuple[str, str, str]], width: int, height: int
) -> Dict[str, Tuple[float, float]]:
    """简单力导向布局"""
    import random, math

    random.seed(42)
    names = [n["title"] for n in notes]
    pos = {
        n: (random.uniform(80, width - 80), random.uniform(80, height - 80))
        for n in names
    }

    # 按深度分组,做出层级感
    depth_groups = defaultdict(list)
    for n in notes:
        depth_groups[n["depth"]].append(n["title"])
    max_depth = max(depth_groups.keys())
    for depth, group in depth_groups.items():
        y = int(80 + (height - 160) * depth / max(max_depth, 1))
        for i, name in enumerate(group):
            x = int(80 + (width - 160) * (i + 1) / (len(group) + 1))
            pos[name] = (x + random.uniform(-30, 30), y + random.uniform(-20, 20))

    # 简单 repulsion/attraction iteration
    for _ in range(50):
        forces = {n: [0.0, 0.0] for n in names}
        for a in names:
            for b in names:
                if a >= b:
                    continue
                dx = pos[b][0] - pos[a][0]
                dy = pos[b][1] - pos[a][1]
                d = max(math.hypot(dx, dy), 1)
                # repulsion
                f = 5000 / (d * d)
                forces[a][0] -= f * dx / d
                forces[a][1] -= f * dy / d
                forces[b][0] += f * dx / d
                forces[b][1] += f * dy / d
        for s, t, _kind in edges:
            if s in pos and t in pos:
                dx = pos[t][0] - pos[s][0]
                dy = pos[t][1] - pos[s][1]
                d = max(math.hypot(dx, dy), 1)
                f = d / 200
                forces[s][0] += f * dx / d
                forces[s][1] += f * dy / d
                forces[t][0] -= f * dx / d
                forces[t][1] -= f * dy / d
        for n in names:
            pos[n] = (
                max(20, min(width - 20, pos[n][0] + forces[n][0] * 0.1)),
                max(20, min(height - 20, pos[n][1] + forces[n][1] * 0.1)),
            )
    return pos


def render_svg(
    pos: Dict[str, Tuple[float, float]],
    edges: List[Tuple[str, str, str]],
    notes: List[Dict],
    width: int,
    height: int,
) -> str:
    svg_lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']
    # Edges
    for s, t, kind in edges:
        if s in pos and t in pos:
            x1, y1 = pos[s]
            x2, y2 = pos[t]
            stroke = "#86868b" if kind == "analogy" else "#0071e3"
            op = "0.15" if kind == "analogy" else "0.22"
            svg_lines.append(
                f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{stroke}" stroke-width="0.5" opacity="{op}"/>'
            )
    # Nodes
    for title, (x, y) in pos.items():
        # Size by connections
        degree = sum(1 for s, t, _ in edges if s == title or t == title)
        r = min(8, max(2, 2 + degree * 0.8))
        note = next((n for n in notes if n["title"] == title), None)
        depth = note["depth"] if note else 0
        colors = {0: "#0071e3", 1: "#0066cc", 2: "#86868b", 3: "#aeaeb2"}
        fill = colors.get(depth, "#c7c7cc") if degree > 0 else "#d2d2d7"
        op = "0.6" if degree > 2 else "0.35"
        svg_lines.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="{fill}" opacity="{op}"/>'
        )
    svg_lines.append("</svg>")
    return "\n".join(svg_lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 graph-bg-builder.py <vault_folder> [width] [height]")
        sys.exit(1)

    folder = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 900
    height = int(sys.argv[3]) if len(sys.argv) > 3 else 1200

    notes = collect_notes(folder)
    edges, notes = build_graph(notes)
    pos = layout_graph(notes, edges, width, height)
    svg = render_svg(pos, edges, notes, width, height)

    out_path = f"/tmp/vaultforge-graph-{Path(folder).name}.svg"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"✅ Graph: {len(notes)} nodes, {len(edges)} links → {out_path}")


if __name__ == "__main__":
    main()
