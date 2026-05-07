#!/usr/bin/env python3
"""
双链构建脚本 - Obsidian Learning Skill

根据逻辑相关性建立笔记间的双链，包括：
1. 推导关系：一篇笔记的结论由另一篇推导而出
2. 原理相似：两篇笔记的原理可以类比借鉴
3. 结论矛盾：两篇笔记的结论存在矛盾
4. 应用关联：一篇笔记的应用涉及另一篇的概念
5. 背景关联：两篇笔记属于同一领域的不同方面

同时建立学习路线图与各 MOC 的双向链接。
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

# 双链关联分析
RELATIONSHIP_TYPES = {
    "derivation": "推导关系",
    "analogy": "原理相似",
    "contradiction": "结论矛盾",
    "application": "应用关联",
    "context": "背景关联"
}

def get_all_notes(vault_path: str) -> List[Dict]:
    """获取 vault 中所有原子笔记"""
    notes = []
    for root, dirs, files in os.walk(vault_path):
        # 跳过隐藏文件夹
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for f in files:
            if f.endswith('.md') and 'MOC' not in f and '学习路线图' not in f:
                path = os.path.join(root, f)
                rel_path = os.path.relpath(path, vault_path)

                # 读取笔记内容
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()

                # 提取标题
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else f

                # 提取所有文本用于关联分析
                # 去除 frontmatter
                body = re.sub(r'^---.*?---\n', '', content, flags=re.DOTALL)
                # 去除 wikilinks
                body = re.sub(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', r'\1', body)
                # 去除 markdown 格式
                body = re.sub(r'#{1,6}\s+', '', body)
                body = re.sub(r'\*\*|__', '', body)
                body = re.sub(r'\*|~|`', '', body)

                notes.append({
                    'path': path,
                    'rel_path': rel_path,
                    'title': title,
                    'content': body,
                    'folder': os.path.dirname(rel_path)
                })

    return notes


def get_all_mocs(vault_path: str) -> List[Dict]:
    """获取 vault 中所有 MOC 笔记"""
    mocs = []
    for root, dirs, files in os.walk(vault_path):
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for f in files:
            if f.endswith('.md') and 'MOC' in f:
                path = os.path.join(root, f)
                rel_path = os.path.relpath(path, vault_path)

                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()

                title_match = re.search(r'^#\s+(.+?)(?:\s*MOC)?$', content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else f.replace(' MOC.md', '')

                mocs.append({
                    'path': path,
                    'rel_path': rel_path,
                    'title': title,
                    'folder': os.path.dirname(rel_path)
                })

    return mocs


def calculate_similarity(text1: str, text2: str) -> float:
    """计算两个文本的相似度（基于词重叠）"""
    words1 = set(re.findall(r'[一-龥a-zA-Z0-9]+', text1.lower()))
    words2 = set(re.findall(r'[一-龥a-zA-Z0-9]+', text2.lower()))

    if not words1 or not words2:
        return 0.0

    intersection = words1 & words2
    union = words1 | words2

    return len(intersection) / len(union) if union else 0.0


def find_relationships(note1: Dict, note2: Dict) -> List[Tuple[str, str]]:
    """分析两个笔记之间的关联类型"""
    relationships = []
    title1, content1 = note1['title'], note1['content']
    title2, content2 = note2['title'], note2['content']

    # 跳过同一笔记
    if note1['path'] == note2['path']:
        return relationships

    # 1. 检查推导关系（关键词检测）
    derivation_keywords = ['因此', '所以', '从而', '导致', '结果表明', '得出结论',
                          'hence', 'therefore', 'thus', 'so', 'consequently',
                          '导致', '由此可见', '证明', '推导']

    content_combined = content1 + content2
    derivation_count = sum(1 for kw in derivation_keywords if kw in content_combined)

    # 2. 检查原理相似（高相似度）
    similarity = calculate_similarity(content1, content2)

    # 3. 检查结论矛盾
    contradiction_keywords = ['但是', '然而', '相反', '不同', '矛盾',
                             'however', 'but', '相反', 'unlike', 'contradict']

    contradiction_count = sum(1 for kw in contradiction_keywords if kw in content_combined)

    # 4. 检查应用关联（同文件夹）
    same_folder = note1['folder'] == note2['folder']

    # 5. 检查背景关联（相同上层文件夹）
    folder1_parts = note1['folder'].split('/')
    folder2_parts = note2['folder'].split('/')
    context_related = len(folder1_parts) >= 2 and len(folder2_parts) >= 2 and \
                      folder1_parts[0] == folder2_parts[0] and \
                      folder1_parts[1] == folder2_parts[1]

    # 判断关联类型
    if similarity > 0.3 and derivation_count >= 2:
        relationships.append(('derivation', '推导关系'))

    if similarity > 0.25:
        relationships.append(('analogy', '原理相似'))

    if contradiction_count >= 2 and similarity > 0.15:
        relationships.append(('contradiction', '结论矛盾'))

    if same_folder and similarity > 0.1:
        relationships.append(('application', '应用关联'))

    if context_related and similarity > 0.08:
        relationships.append(('context', '背景关联'))

    return relationships


def build_note_to_note_links(notes: List[Dict], min_relationships: int = 1) -> Dict[str, List[str]]:
    """建立笔记间的双链"""
    links = {}

    for i, note1 in enumerate(notes):
        links[note1['rel_path']] = []

        for j, note2 in enumerate(notes):
            if i >= j:
                continue

            relationships = find_relationships(note1, note2)

            if len(relationships) >= min_relationships:
                # 获取笔记名称（不含路径和扩展名）
                note_name = note2['title']

                # 根据关联类型添加不同前缀（可选，便于理解）
                rel_types = [r[1] for r in relationships]
                links[note1['rel_path']].append(note_name)

    return links


def add_links_to_notes(vault_path: str, note_links: Dict[str, List[str]]):
    """将双链添加到笔记中"""
    updated_count = 0

    for rel_path, linked_notes in note_links.items():
        if not linked_notes:
            continue

        full_path = os.path.join(vault_path, rel_path)

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否已有相关笔记部分
        if '## 相关笔记' in content:
            # 追加到现有部分
            pass
        else:
            # 添加新的相关笔记部分
            links_text = '\n'.join([f'- [[{note}]]" for note in linked_notes])
            new_section = f"\n## 相关笔记\n\n{links_text}\n"

            content = content.rstrip() + new_section

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            updated_count += 1

    return updated_count


def build_roadmap_moc_links(vault_path: str, roadmap_name: str, mocs: List[Dict]):
    """建立学习路线图与 MOC 的双向链接"""
    roadmap_path = os.path.join(vault_path, f"学习路线图 - {roadmap_name}.md")

    if not os.path.exists(roadmap_path):
        print(f"⚠️ 路线图文件不存在: {roadmap_path}")
        return 0

    # 读取路线图
    with open(roadmap_path, 'r', encoding='utf-8') as f:
        roadmap_content = f.read()

    # 为每个 MOC 在路线图中添加链接
    # 找到路线图中对应的 H3 标题，添加 MOC 链接

    updated_mocs = 0

    for moc in mocs:
        # 从 MOC 标题提取主题名
        moc_title = moc['title']

        # 在路线图中查找对应的 H3（使用正则匹配）
        # 格式：### 主题名称 或 ### 主题名称 MOC
        pattern = rf'(###\s+{re.escape(moc_title)}?\s*$)'

        if re.search(pattern, roadmap_content, re.MULTILINE):
            # 在该行后添加 MOC 链接
            replacement = rf'\1\n\n[[{moc["rel_path"].replace(".md", "")}|{moc_title}]]'
            roadmap_content = re.sub(pattern, replacement, roadmap_content, flags=re.MULTILINE)

        # 同时更新 MOC 文件，添加指向路线图的链接
        moc_rel_path = moc['rel_path']
        with open(os.path.join(vault_path, moc_rel_path), 'r', encoding='utf-8') as f:
            moc_content = f.read()

        # 检查是否已有路线图链接
        if f'[[../../学习路线图 - {roadmap_name}' not in moc_content:
            if '## 相关笔记' not in moc_content:
                new_section = f"\n## 相关笔记\n\n- [[../../学习路线图 - {roadmap_name}|学习路线图]]\n"
                moc_content = moc_content.rstrip() + new_section
            else:
                moc_content = moc_content.rstrip() + f"\n- [[../../学习路线图 - {roadmap_name}|学习路线图]]\n"

            with open(os.path.join(vault_path, moc_rel_path), 'w', encoding='utf-8') as f:
                f.write(moc_content)

            updated_mocs += 1

    # 保存路线图
    with open(roadmap_path, 'w', encoding='utf-8') as f:
        f.write(roadmap_content)

    return updated_mocs


def main():
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 double-link-builder.py <vault_path> [roadmap_name]")
        sys.exit(1)

    vault_path = sys.argv[1]
    roadmap_name = sys.argv[2] if len(sys.argv) > 2 else "Digital Transformation Roadmap"

    print(f"🔗 开始构建双链...")
    print(f"   Vault: {vault_path}")

    # 获取所有笔记和 MOC
    print("\n📚 扫描笔记...")
    notes = get_all_notes(vault_path)
    print(f"   找到 {len(notes)} 个原子笔记")

    mocs = get_all_mocs(vault_path)
    print(f"   找到 {len(mocs)} 个 MOC")

    # 建立笔记间双链
    print("\n🔗 分析笔记关联...")
    note_links = build_note_to_note_links(notes)

    # 统计链接数量
    total_links = sum(len(links) for links in note_links.values())
    print(f"   建立 {total_links} 个笔记间链接")

    # 添加链接到笔记
    print("\n✏️ 更新笔记...")
    updated = add_links_to_notes(vault_path, note_links)
    print(f"   更新了 {updated} 个笔记")

    # 建立路线图与 MOC 的双链
    print("\n📋 建立路线图与 MOC 双链...")
    moc_updated = build_roadmap_moc_links(vault_path, roadmap_name, mocs)
    print(f"   更新了 {moc_updated} 个 MOC")

    print("\n✅ 双链构建完成！")
    print(f"   - 笔记间链接: {total_links}")
    print(f"   - 路线图-MOC 链接: {moc_updated * 2} (双向)")


if __name__ == "__main__":
    main()
