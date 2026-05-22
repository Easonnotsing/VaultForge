# VaultForge

> [!TIP]
> If you find VaultForge useful, consider [**starring the repo ⭐**](https://github.com/Easonnotsing/VaultForge) — it helps others discover it.

AI agent skill for Obsidian — transforms PDFs and Markdown files into structured knowledge bases with atomic notes, bi-directional wikilinks, Maps of Content (MOCs), and learning roadmaps. Supports English and Chinese. Works with Claude Code, Codex, and Cursor.

> **Note:** This is an **AI agent skill** (installed in `~/.agents/skills/`), not an MCP server or Obsidian plugin. Use it with Claude Code, Codex, or Cursor.

> A consultant-style learning methodology — master a new domain quickly and reach a level where you can discuss it with professionals. You focus on understanding, thinking, and asking questions; the AI handles all the tedious organization.

📖 [中文说明](#chinese)

> 🆕 **See what's new in v3.1.0** — [Release Page](https://easonnotsing.github.io/VaultForge/) · [Dev.to](https://dev.to/easonnotsing/how-i-turned-6-cognitive-science-principles-into-an-ai-agent-that-builds-obsidian-vaults-103e)

---

## Why VaultForge

| Traditional Workflow | VaultForge |
|---------------------|-------------------|
| Read → extract → outline → write notes → link | One trigger, fully automated |
| Scattered notes, no knowledge network | Atomic notes + MOC + 5-type logical wikilinks form a semantic network |
| No feedback on learning depth | Core questions guide learning; controversy analysis expands boundaries |
| Interruption = start over | 5-state state machine auto-resumes from breakpoint |
| Repeated full-text reading wastes tokens | context-extractor pre-fetches per source_range, reducing token usage 5×+ |

---

## Core Concepts

| Concept | One-liner |
|---------|-----------|
| **Atomic Note** | A standalone note centered on a single knowledge point with concept explanation, case study, citation, and reflection questions |
| **MOC** (Map of Content) | An index page linking all atomic notes under a topic, providing navigation and overview |
| **Learning Roadmap** | AI-generated structured outline (Category → Topic → Knowledge Point) organizing all content |
| **Wikilink** | Obsidian `[[note]]` internal links, established via logical relationships (derivation/analogy/contradiction/application/context), not mere term similarity |
| **Core Questions** | ≤5 guiding questions driving active exploratory learning, connecting knowledge to real-world applications |
| **Controversy Analysis** | Deep research supplementing diverse perspectives on consensus, disputes, unknowns, and exploration directions |

---

## Quick Start

```bash
# 1. Clone to skills directory
git clone https://github.com/Easonnotsing/VaultForge.git ~/.agents/skills/VaultForge

# 2. (Recommended) Install PDF extraction dependency
pip install pypdf
```

Trigger in any AI Agent client:

| Client | How |
|--------|-----|
| **Claude Code / Codex** | Configure a slash command then `/VaultForge`, or say "run VaultForge" |
| **Cursor** | Place in Agent Skills directory, trigger with natural language |
| **Other clients** | Place in Skills directory, explicitly request "follow SKILL.md flow" |

> See [COMPATIBILITY.md](./COMPATIBILITY.md) for detailed compatibility notes.

---

## What You Get

After processing, your vault will contain:

```
vault/
├── .obsidian-learning-progress.md             # Progress tracking & vf_processed_files
├── Learning Roadmap v1 - {Topic}.md              # Outline version (H2/H3/bullets)
├── Learning Roadmap (Full) v1 - {Topic}.md       # Detailed version (cases, citations, source_range)
├── Core Questions.md                          # ≤5 guiding questions
├── {Topic} - Controversy Analysis.md          # Consensus vs disputes vs context-dependent
├── VaultForge Update Report - {date}.md       # (incremental) new files, links, refresh suggestions
│
├── 01. Digital Transformation/
│   ├── Overview/
│   │   ├── Overview MOC.md                    # Topic map of content
│   │   ├── Digitization vs Transformation.md  # Atomic note (vf_ frontmatter, bold-labeled sections)
│   │   └── Transformation Framework.md
│   └── Customer Domain/
│       ├── Customer Domain MOC.md
│       └── ...
└── 02. Strategic Management/
    └── ...
```

---

## Core Capabilities

### 7-Phase Pipeline

```
Phase 0: Vault Scan             → Auto-detect existing vf notes → incremental vs fresh vs skip
Phase 1: Roadmap Generation    → Full reading → structured outline + detailed version
Phase 2: File Structure         → Batch create folders / MOCs / blank atomic notes (add-only in incremental)
Phase 3: Parallel Content Fill  → Resume check → context pre-extraction → parallel agents → quality review
Phase 4: Wikilink Building      → Three-stage funnel (structural → TF-IDF → LLM classification; new→old suggestions)
Phase 5: Final Review           → Integrity check + core question generation + update report + **pristine refresh** (incremental)
Phase 6: Deep Research (opt)    → Web search → controversy analysis notes
```

### Engineering Guarantees

- **Interruption Recovery**: Each atomic note has a `status` field (draft → filling → filled → reviewed). Phase 3 auto-scans and prompts "resume from breakpoint".
- **Atomic Write Protection**: `.md.tmp` → verify → rename. Agent crashes never corrupt completed notes.
- **vf_ Frontmatter Standard**: All notes carry `vf: true`, `vf_version`, `vf_status` (pristine/user_modified/locked), `vf_session` for traceability and incremental detection.
- **Incremental Update**: Phase 0 auto-detects existing VaultForge notes, classifies new vs processed files, and offers incremental (add-only, never modifies user edits) or fresh generation.
- **Pristine Note Refresh**: When new source material covers existing topics, auto-detects refresh-eligible notes in the Update Report. User selects which to regenerate — frontmatter preserved, body replaced with expanded content.
- **Context Pre-extraction**: `context-extractor.py` extracts source paragraphs per `source_range` annotation. Each agent receives only relevant snippets — token usage reduced 5×+.
- **Auto Retry**: Notes failing quality review enter a repair queue with up to 2 retries.
- **Wikilink Precision**: Three-stage funnel (structural filtering + TF-IDF semantics + LLM classification), ~60-80% coverage.

### Atomic Note Structure

Every note uses **bold-labeled sections** for readability:

```markdown
# Knowledge Point Title

## Core Concepts
**Background**: ...
**Definition**: ...
**Principle**: ...
**Application**: ...
**Relationship to Other Concepts**: ...

## Case Study
### {Case Name}
**Background**: ...
**Process**: ...
**Outcome**: ...
**Insight**: ...

## Original Text
> {Core original passage, 50-150 words}

> — Source: {Document}, Author: {Author}, pp.{Page Range}

## Reflection Questions
1. ...
2. ...
```

> Section headers adapt to the user's chosen output language (English / 中文 / etc.).

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Obsidian Vault** | Install and initialize Obsidian |
| **AI Agent Client** | Claude Code / Codex / Cursor or any client supporting Skill loading |
| **Python 3** | Required by `context-extractor.py`, `double-link-builder.py` |
| **pypdf** (recommended) | PDF page extraction: `pip install pypdf` (or `PyPDF2`) |

### Phase 6 Deep Research (optional)

Phase 6 produces controversy analysis by searching the web for mainstream views, disputes, and different perspectives. It uses the **deep-research** skill with Firecrawl and Exa MCP servers as backends. At least one backend required.

**Step 1 — Get API keys** (both have free tiers):

- [Firecrawl](https://firecrawl.dev) — Register → API Key (format: `fc-...`)
- [Exa](https://exa.ai) — Register → API Key

**Step 2 — Configure opencode** (`~/.config/opencode/opencode.json`):

```json
{
  "mcp": {
    "firecrawl": {
      "type": "local",
      "command": ["npx", "-y", "firecrawl-mcp"],
      "environment": { "FIRECRAWL_API_KEY": "fc-..." }
    },
    "exa": {
      "type": "local",
      "command": ["npx", "-y", "exa-mcp"],
      "environment": { "EXA_API_KEY": "..." }
    }
  }
}
```

**Step 3 — Start a new session.** MCP tools are only injected on session creation. Resume/reconnect won't pick them up — you must start a fresh conversation.

Without MCP backends, VaultForge falls back to built-in web search, or skips Phase 6 if no search tools are available.

---

## FAQ

### Q: How do I start?

Place learning materials (PDF/MD) in your vault folder, trigger the skill, select the folder. Start with small materials (< 50 pages) for testing.

### Q: What if the task is interrupted?

Re-trigger the skill. Phase 3 scans all notes' `status` fields, identifies completed/incomplete/corrupted, and prompts "resume from breakpoint" or "restart".

### Q: Wikilinks seem inaccurate?

Default uses the three-stage funnel: keyword heuristics + TF-IDF semantics + LLM classification. Without LLM access, use `--mode strict` for deterministic links (~40-50% coverage). Both can be manually adjusted in Obsidian.

### Q: Note content too thin?

The skill requires 200+ word core explanations, 150+ word case analysis, and 50-150 word original citations. Quality review auto-detects substandard notes and triggers rewrites.

### Q: Can I incrementally add new materials?

Yes. Place new PDF/MD files in the same vault folder and re-trigger the skill. Phase 0 auto-detects existing VaultForge notes, marks new files pre-selected, and runs in **add-only incremental mode** — new notes are created, existing notes are never modified, and new-to-old wikilinks are suggested (not auto-written). See `VaultForge Update Report - {date}.md` for a summary.

### Q: How to trigger Phase 6 deep research?

Phase 5 completion prompts a confirmation. Choose "continue" and the agent loads the `deep-research` skill. It requires Firecrawl MCP or Exa MCP as backends to function. If the skill is unavailable (not installed or no MCP backends configured), VaultForge falls back to websearch, or skips Phase 6 if no search tools are available.

### Q: What file formats are supported?

PDF (requires pypdf/PyPDF2) and Markdown. TXT can extract full text but page numbering is imprecise.

---

## Project Structure

```
VaultForge/
├── README.md
├── SKILL.md                         # Full skill definition
├── HISTORY.md                       # Failure cases & improvement log
├── COMPATIBILITY.md                 # Multi-client compatibility guide
├── agents/
│   ├── roadmap-generator.md         # Roadmap generation agent
│   ├── file-structure-creator.md    # File structure creation agent
│   ├── atomic-note-filler.md        # Atomic note filling agent
│   └── note-reviewer.md             # Note review agent
├── references/
│   │   └── templates.md                 # Output templates (core questions, controversy analysis)
├── scripts/
│   ├── context-extractor.py         # Context pre-extraction (Phase 3.0b)
│   ├── double-link-builder.py       # Wikilink builder (3-stage funnel v2)
│   └── share-card.html              # Achievement card template
└── tests/
    ├── fixtures/
    └── test_*.py
```

---

## Contributing

Issues and Pull Requests welcome.

## License

MIT

---

<a name="chinese"></a>
# VaultForge（中文）

> [!TIP]
> 觉得好用的话，[**点个 Star ⭐**](https://github.com/Easonnotsing/VaultForge) 帮更多人看到它。

将 PDF / Markdown 学习资料自动转化为结构化的 Obsidian 原子笔记知识库。

> 咨询顾问式的学习方法论——在极短时间内掌握一个领域，达到能与专业人士深入交流的水平。你只负责理解、思考、提问，AI 代为完成繁琐整理。

### 核心概念

| 概念 | 说明 |
|------|------|
| **原子笔记** | 围绕单一知识点的独立笔记，含概念讲解、案例、引用、思考问题 |
| **MOC** | 一个主题下所有原子笔记的索引页，通过双向链接聚合 |
| **学习路线图** | AI 生成的结构化大纲（类别 → 主题 → 知识点） |
| **双链** | 基于逻辑关系（推导/类比/矛盾/应用/背景）而非术语相似建立 |
| **核心问题** | ≤5 个引导性问题，驱动主动探索式学习 |
| **争议分析** | 深度研究呈现共识、争议、未知与探索方向 |
| **增量更新** | 自动检测已有笔记，仅添加新笔记，不修改用户编辑，生成更新报告 |

### 7 阶段流水线

```
Phase 0: Vault 扫描           → 自动检测已有 vf 笔记 → 增量/全新/跳过 三选一
Phase 1: 路线图生成           → 完整阅读 → 结构化大纲 + 详细版本
Phase 2: 文件结构创建         → 批量创建文件夹/MOC/空白原子笔记（增量模式仅添加）
Phase 3: 并行内容填充         → 断点恢复 → 上下文预提取 → 并行 Agent → 质量审核
Phase 4: 双向链接构建         → 三阶段漏斗（结构→TF-IDF→LLM 分类；新→旧仅建议）
Phase 5: 终审                 → 完整性检查 + 核心问题 + 更新报告 + **已有笔记刷新**（增量模式）
Phase 6: 深度研究（可选）     → 网络搜索 → 争议分析笔记
```

### 快速开始

> 🆕 **查看 v3.1.0 更新** — [发布页](https://easonnotsing.github.io/VaultForge/) · [Dev.to](https://dev.to/easonnotsing/how-i-turned-6-cognitive-science-principles-into-an-ai-agent-that-builds-obsidian-vaults-103e)

```bash
git clone https://github.com/Easonnotsing/VaultForge.git ~/.agents/skills/VaultForge
pip install pypdf
```
