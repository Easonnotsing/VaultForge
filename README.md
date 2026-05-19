# Obsidian Learning

将 PDF / Markdown 学习资料自动转化为结构化的 Obsidian 原子笔记知识库。

> 这是一个咨询顾问式的学习方法论——在极短时间内掌握一个领域，达到能与专业人士深入交流的水平。你只负责理解、思考、提问，繁琐的整理工作全部由 AI 代为完成。

---

## 为什么选择 obsidian-learning

| 传统学习流程 | obsidian-learning |
|-------------|-------------------|
| 通读材料 → 手动摘录 → 整理大纲 → 写笔记 → 建立关联 | 一句话触发，全自动完成 |
| 笔记散乱，难以形成知识网络 | 原子笔记 + MOC + 五类逻辑双链，天然形成语义网络 |
| 学到什么程度？缺少反馈 | 生成核心问题引导学习，争议分析拓展边界 |
| 中断后前功尽弃 | 5 态状态机自动断点恢复 |
| 大量 PDF 阅读耗时 | context-extractor 按 source_range 预提取，避免重复阅读 |

---

## 核心概念

| 概念 | 一句话解释 |
|------|-----------|
| **原子笔记** | 围绕单一知识点的独立笔记，含概念讲解、案例、引用，一篇讲透一件事 |
| **MOC** (Map of Content) | 一个主题下所有原子笔记的索引页，通过双向链接聚合，提供主题导航 |
| **学习路线图** | AI 生成的结构化大纲（类别 → 主题 → 知识点），组织全部学习内容 |
| **双链** | Obsidian `[[笔记名]]` 格式的内部链接，基于逻辑关系而非术语相似建立 |

## 快速开始

```bash
# 1. Clone 到 skills 目录
git clone https://github.com/Easonnotsing/obsidian-learning.git ~/.agents/skills/obsidian-learning

# 2. （推荐）安装 PDF 提取依赖
pip install pypdf
```

在任意 AI Agent 客户端中触发：

| 客户端 | 方式 |
|--------|------|
| **Claude Code / Codex** | 配置 slash command 后 `/obsidian-learning`，或在对话中说「按 obsidian-learning 执行」 |
| **Cursor** | 放入 Agent Skills 目录，用自然语言触发 |
| **其他客户端** | 放入 Skills 目录，对话中显式要求「按 SKILL.md 流程执行」 |

> 详细兼容性说明见 [COMPATIBILITY.md](./COMPATIBILITY.md)

---

## 产物预览

处理完成后，你的 vault 中会生成：

```
vault/
├── 学习路线图 - {主题}.md                  # 大纲版（H2/H3/bullet）
├── 学习路线图（完整版） - {主题}.md         # 详细版（含案例、原文引用、source_range）
├── 核心问题.md                             # ≤5 个引导性核心问题
├── {主题} - 争议分析.md                    # 行业共识 vs 争议 vs 情景依赖
│
├── 01. 数字化转型/
│   ├── 转型概述/
│   │   ├── 转型概述 MOC.md                 # 主题内容地图
│   │   ├── 数字化vs数字化转型.md            # 原子笔记（粗体标签分段排版）
│   │   └── 转型核心框架.md
│   └── 客户领域/
│       ├── 客户领域 MOC.md
│       └── ...
└── 02. 战略管理/
    └── ...
```

---

## 核心能力

### 6 Phase 完整管线

```
Phase 1: 路线图生成       → 完整阅读 → 结构化大纲 + 详细版
Phase 2: 文件结构创建     → 批量创建文件夹/MOC/空白原子笔记
Phase 3: 并行内容填充     → 断点恢复 → 上下文预提取 → 并行代理填充 → 质量审查
Phase 4: 双链建立         → 三阶段漏斗（结构亲和 → TF-IDF → LLM 分类）
Phase 5: 最终审查         → 完整性检查 + 核心问题生成
Phase 6: 深度研究（可选） → 网络检索 → 争议分析笔记
```

### 工程保障

- **中断恢复**：每个原子笔记含 `status` 字段（draft → filling → filled → reviewed），Phase 3 启动时自动扫描并提示「从断点继续」
- **原子写保护**：`.md.tmp` → 验证 → rename，Agent 崩溃不损坏已完成笔记
- **上下文预提取**：`context-extractor.py` 按 `source_range` 提取原文段落，每个 Agent 只收相关片段，Token 消耗降低 5×+
- **自动重试**：质量审查未通过的笔记进入修复队列，最多重试 2 次
- **双链精确度**：三阶段漏斗（结构化过滤 + TF-IDF 语义 + LLM 关系分类），覆盖率 ~60-80%

### 原子笔记结构

每篇原子笔记按**粗体标签分段排版**，清晰可读：

```markdown
# 知识点名称

## 核心知识点
**背景**：...
**定义**：...
**原理**：...
**应用场景**：...
**与其他概念的关系**：...

## 相关案例
### {案例名称}
**背景**：...
**过程**：...
**结果**：...
**启示**：...

## 原文引用
> {核心原文段落，50-150 字}

> — 来源：{文档名}，作者：{作者名}，第{页码段}页

## 核心思考
1. ...
2. ...
```

---

## 前置要求

| 要求 | 说明 |
|------|------|
| **Obsidian Vault** | 安装并初始化 Obsidian |
| **AI Agent 客户端** | Claude Code / Codex / Cursor 等任意支持 Skill 加载的客户端 |
| **Python 3** | `context-extractor.py`、`double-link-builder.py` 需要 |
| **pypdf**（推荐） | PDF 页码提取：`pip install pypdf`（或 `PyPDF2`） |
| **deep-research skill**（可选） | Phase 6 深度研究，无此 skill 时自动跳过并提示 |

---

## 常见问题

### Q: 如何开始？

将学习材料（PDF/MD）放入 vault 文件夹，启动 skill，选择文件夹即可。建议首次在小规模材料（< 50 页）上测试。

### Q: 任务中断后如何恢复？

重新触发 skill，Phase 3 会扫描所有笔记的 `status` 字段，识别已完成/未完成/残骸，提示「从断点继续」或「重新开始」。

### Q: 双链不准怎么办？

默认使用三阶段漏斗：关键词启发式 + TF-IDF 语义 + LLM 分类。若环境不支持 LLM，使用 `--mode strict` 降级为确定性链接（覆盖率 ~40-50%）。两种情况均可在 Obsidian 中手动调整。

### Q: 原子笔记内容不够丰富？

Skill 要求 200+ 字核心讲解、150+ 字案例分析、50-150 字原文引用。质量审查自动检测不达标笔记并触发重写。

### Q: 可以增量添加新学习材料吗？

当前版本对已处理的 vault 添加新材料需重新执行流程。计划在后续版本支持增量模式。

### Q: 如何触发 Phase 6 深度研究？

Phase 5 完成后会弹出确认提示。选择「继续」后 Agent 自动检测可用检索工具（`deep-research` skill、Web Search MCP 等），有则执行、无则告知跳过。

### Q: 支持哪些文件格式？

PDF（需 pypdf/PyPDF2）和 Markdown。TXT 也可提取全文但页码不精确。未来计划支持更多格式。

---

## 项目结构

```
obsidian-learning/
├── README.md
├── SKILL.md                         # 完整技能定义
├── HISTORY.md                       # 失败案例与改进记录
├── COMPATIBILITY.md                 # 多客户端兼容性说明
├── agents/
│   ├── roadmap-generator.md         # 路线图生成 Agent
│   ├── file-structure-creator.md    # 文件结构创建 Agent
│   ├── atomic-note-filler.md        # 原子笔记填充 Agent
│   └── note-reviewer.md             # 笔记审查 Agent
├── references/
│   ├── obsidian-structure.md        # Obsidian 格式规范
│   └── templates.md                 # 生成物模板（核心问题、争议分析）
├── scripts/
│   ├── context-extractor.py         # 上下文预提取（Phase 3.0b）
│   ├── double-link-builder.py       # 双链构建（三阶段漏斗 v2）
│   └── roadmap-editor.py            # 可选：路线图网页编辑
└── tests/
    ├── fixtures/
    └── test_scripts.py
```

---

## 贡献

欢迎提交 Issue 和 Pull Request。

## License

MIT
