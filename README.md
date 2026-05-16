# Obsidian Learning Material Processing

这是一个咨询顾问式的学习方法论，旨在帮助你在极短时间内掌握一个新领域的核心知识，快速达到能够与专业人士深入交流的水平。这个工具利用Obsidian+Claude Code来自动整理领域核心问题与框架、明确核心知识点、建立知识点间的逻辑联系、并识别领域知识边界与争议之处。整个过程中，你只需专注于理解、思考、提问，繁琐的手工工作全部由 AI 代为完成，更容易进入心流状态，提高学习效率。

[SKILL.md](./SKILL.md) - 完整技能定义文档

---

## 功能特性

- **完整阅读**：自动完整阅读学习材料，支持大文件分批读取
- **学习路线图**：生成详细版和大纲版两份路线图
- **原子笔记**：创建丰富详尽的原子笔记（200+ 字/篇）
- **MOC 管理**：自动创建主题 MOC，链接相关原子笔记
- **智能双链**：基于逻辑关联建立笔记间双向链接
- **核心问题**：生成 5 个以内核心问题，引导高效学习
- **争议分析**：深度研究识别行业共识与争议，为与资深人士深入探讨提供方向

---

## 安装

### 推荐：Clone 完整仓库

```bash
# Clone 到本地 skills 目录
git clone https://github.com/Easonnotsing/obsidian-learning.git /path/to/your/skills/obsidian-learning
```

### 不推荐：只下载 SKILL.md

只下载 [SKILL.md](./SKILL.md) 只能保留方法论说明；`agents/`、`references/`、`scripts/` 中的子流程、结构规范、双链候选生成器和编辑器不会可用。若要获得完整体验，请安装整个仓库。

---

## 前置要求

1. **Obsidian Vault**：确保你有一个 Obsidian 知识库
2. **Claude Code**：最新版本的 Claude Code CLI
3. **学习材料**：PDF、Markdown 或其他文档格式
4. **deep-research skill**：（可选）用于 Phase 6 深度研究，如未安装则跳过该阶段
5. **Playwright**：（可选）仅网页选择器/路线图编辑器需要。安装命令：

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
```

---

## 使用方法

### 调用技能

- **Claude Code**：若已配置 slash command，可使用例如 `/obsidian-learning`（以你本地的 command 配置为准）。
- **Cursor**：将本仓库放入 Agent Skills 目录后，用自然语言说明「按 obsidian-learning 流程处理学习材料」即可；亦可在规则中引用本 skill。

### 典型工作流程

```
1. 启动技能 → 选择 vault 文件夹 → 自动阅读学习材料
2. 生成并确认学习路线图
3. 自动创建文件夹结构和原子笔记框架
4. 并行填充原子笔记内容（含质量审查，默认执行）
   - 按工作量分配 agents（每个 agent ≤ 5 个笔记）
   - 失败/未通过的笔记自动重试（最多 2 次）
5. 生成笔记间双链候选，由主 Agent 确认后应用
6. 最终审查 + 生成"核心问题"笔记
7. （可选）深度研究与争议分析 → 生成「争议分析」笔记（需 `deep-research` 或等价检索能力）
```

### 输出产物

```
vault/
├── 学习路线图 - {主题}.md              # 大纲版路线图
├── 学习路线图（完整版） - {主题}.md     # 详细版路线图
├── 核心问题.md                         # 核心问题引导笔记
└── {主题}/
    ├── {模块A}/
    │   ├── {模块A} MOC.md              # MOC 索引
    │   └── {原子笔记1}.md              # 原子笔记
    │   └── {原子笔记2}.md
    └── {模块B}/
        └── ...
```

---

## 核心原则

### 必须完整阅读

> **绝对禁止基于部分内容生成学习路线图或笔记。**

技能会自动完整阅读所有学习材料，大文件自动分批处理，无需手动确认。

### 原子笔记质量标准

> **原子笔记不是提纲，而是要让初学者能够完整理解和学习的教学材料。**

每篇原子笔记必须包含：
- 核心概念详细讲解（200+ 字）
- 完整案例说明（背景、过程、结果）
- 准确原文引用（文档名、页码）
- 促进深度理解的思考问题

### 双链建立标准

基于逻辑相关性，而非术语相似：

1. **推导关系** - 一篇笔记的结论由另一篇推导而出
2. **原理相似** - 两篇笔记的原理可以类比借鉴
3. **结论矛盾** - 两篇笔记的结论存在矛盾
4. **应用关联** - 一篇笔记的应用涉及另一篇的概念
5. **背景关联** - 两篇笔记属于同一领域的不同方面

---

## 注意事项

### 1. 首次使用

- 建议先在小规模学习材料上测试流程
- 路线图生成后仔细审核，必要时提出修改意见

### 2. 内容审查

- AI 生成的内容可能存在误差，请务必人工审核原文引用的准确性
- 核心问题仅作为学习引导，不能替代原文阅读

### 3. 双链质量

- `scripts/double-link-builder.py` 默认只生成 `link-candidates.md`，不直接修改原子笔记
- 主 Agent 应逐条确认候选是否符合五类逻辑关系；确认后可手动应用，或运行脚本 `--apply`
- 如有不需要的双链，可以在阅读时手动删除或调整

### 4. 文件管理

- 技能会在你指定的 vault 文件夹下创建文件
- 建议定期备份你的 vault

### 5. 大文件处理

- PDF 等大文件会自动分批读取（每批 50 页）
- 无需手动确认，自动继续

### 6. Phase 6 深度研究

- **可选**：仅当已安装并可调用 `deep-research` skill（或等价 MCP）时执行；否则跳过该阶段，不影响 Phase 1–5 产物。
- Phase 5 与 Phase 6 之间无需额外确认；若跳过 Phase 6，主 Agent 应向用户说明原因。

### 7. 可选本地脚本（网页选择器 / 路线图编辑器）

- `scripts/run-picker.py`、`scripts/roadmap-editor.py`、`generate-picker.sh` 用于在本机生成简易网页并通过浏览器选择目录或编辑路线图，**依赖本机已安装的 Python、浏览器与 Playwright**；若你只用对话式流程，可以不安装、不运行这些脚本。
- 脚本不会自动安装依赖；缺少 Playwright 时会给出安装提示。
- `scripts/roadmap-editor.py` 保存后会写回原路线图文件，并在同目录生成 `.bak` 备份。

---

## 文件结构

```
obsidian-learning/
├── README.md                        # 本文件
├── SKILL.md                         # 完整技能定义
├── COMPATIBILITY.md                 # Claude Code / Cursor / Codex 兼容性说明
├── agents/
│   ├── roadmap-generator.md         # 路线图生成
│   ├── file-structure-creator.md    # 文件结构创建
│   ├── atomic-note-filler.md        # 原子笔记填充
│   └── note-reviewer.md             # 笔记审查
├── references/
│   └── obsidian-structure.md        # Obsidian 结构规范
├── scripts/
│   ├── double-link-builder.py       # 双链候选生成器（默认只输出 link-candidates.md）
│   ├── roadmap-editor.py            # 可选：路线图网页编辑
│   ├── run-picker.py                # 可选：vault 选择器网页
│   └── generate-picker.sh           # 可选：调用选择器
└── tests/
    ├── fixtures/                    # 测试夹具说明
    └── test_scripts.py              # 本地脚本回归测试
```

---

## 本地验证

```bash
python3 -m unittest discover -s tests
```

双链候选生成：

```bash
python3 scripts/double-link-builder.py /path/to/vault
```

主 Agent 确认候选后再应用：

```bash
python3 scripts/double-link-builder.py /path/to/vault --apply
```

---

## 常见问题

### Q: 技能无法调用怎么办？

确保已将本 skill 安装到对应客户端的 skills 目录：Claude Code 下可配置 slash command；Cursor 下依赖 Agent Skills 匹配或显式在对话中要求按 `SKILL.md` 执行。

### Q: 双链不准确怎么办？

双链由主流程按逻辑标准撰写；若使用 `double-link-builder.py`，其仅在满足 SKILL 五类关系对应的**结构化条件**（互引、标题主题重叠、领域词汇与目录关系等）时生成候选，**不**根据全文词面相似度单独建链。脚本默认不会写入原子笔记；主 Agent 确认后再应用。

### Q: 可以处理非 Markdown 文件吗？

技能主要设计用于处理 Markdown 文件。PDF 等其他格式会自动提取文本内容，但格式可能需要后续调整。

### Q: 原子笔记内容太少怎么办？

技能要求每篇原子笔记至少 200 字、包含案例和原文引用。如果内容不符合要求，技能会自动识别并要求返工重写。

---

## 贡献

欢迎提交 Issue 和 Pull Request！

---

## License

MIT
