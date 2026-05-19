# Obsidian Learning

Automatically transform PDF / Markdown learning materials into structured Obsidian atomic note knowledge bases.

> A consultant-style learning methodology — master a new domain quickly and reach a level where you can discuss it with professionals. You focus on understanding, thinking, and asking questions; the AI handles all the tedious organization.

📖 [中文说明](#chinese)

---

## Why obsidian-learning

| Traditional Workflow | obsidian-learning |
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
git clone https://github.com/Easonnotsing/obsidian-learning.git ~/.agents/skills/obsidian-learning

# 2. (Recommended) Install PDF extraction dependency
pip install pypdf
```

Trigger in any AI Agent client:

| Client | How |
|--------|-----|
| **Claude Code / Codex** | Configure a slash command then `/obsidian-learning`, or say "run obsidian-learning" |
| **Cursor** | Place in Agent Skills directory, trigger with natural language |
| **Other clients** | Place in Skills directory, explicitly request "follow SKILL.md flow" |

> See [COMPATIBILITY.md](./COMPATIBILITY.md) for detailed compatibility notes.

---

## What You Get

After processing, your vault will contain:

```
vault/
├── Learning Roadmap - {Topic}.md              # Outline version (H2/H3/bullets)
├── Learning Roadmap (Full) - {Topic}.md       # Detailed version (cases, citations, source_range)
├── Core Questions.md                          # ≤5 guiding questions
├── {Topic} - Controversy Analysis.md          # Consensus vs disputes vs context-dependent
│
├── 01. Digital Transformation/
│   ├── Overview/
│   │   ├── Overview MOC.md                    # Topic map of content
│   │   ├── Digitization vs Transformation.md  # Atomic note (bold-labeled sections)
│   │   └── Transformation Framework.md
│   └── Customer Domain/
│       ├── Customer Domain MOC.md
│       └── ...
└── 02. Strategic Management/
    └── ...
```

---

## Core Capabilities

### 6-Phase Pipeline

```
Phase 1: Roadmap Generation    → Full reading → structured outline + detailed version
Phase 2: File Structure         → Batch create folders / MOCs / blank atomic notes
Phase 3: Parallel Content Fill  → Resume check → context pre-extraction → parallel agents → quality review
Phase 4: Wikilink Building      → Three-stage funnel (structural → TF-IDF → LLM classification)
Phase 5: Final Review           → Integrity check + core question generation
Phase 6: Deep Research (opt)    → Web search → controversy analysis notes
```

### Engineering Guarantees

- **Interruption Recovery**: Each atomic note has a `status` field (draft → filling → filled → reviewed). Phase 3 auto-scans and prompts "resume from breakpoint".
- **Atomic Write Protection**: `.md.tmp` → verify → rename. Agent crashes never corrupt completed notes.
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
| **deep-research skill** (optional) | Phase 6 deep research; auto-skipped with notice if unavailable |

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

The current version requires re-running the full flow when adding materials to a processed vault. Incremental mode is planned.

### Q: How to trigger Phase 6 deep research?

Phase 5 completion prompts a confirmation. Choose "continue" and the agent auto-detects available search tools (`deep-research` skill, Web Search MCP, etc.), executes if available or notifies if unavailable.

### Q: What file formats are supported?

PDF (requires pypdf/PyPDF2) and Markdown. TXT can extract full text but page numbering is imprecise.

---

## Project Structure

```
obsidian-learning/
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
│   ├── obsidian-structure.md        # Obsidian format specification
│   └── templates.md                 # Output templates (core questions, controversy analysis)
├── scripts/
│   ├── context-extractor.py         # Context pre-extraction (Phase 3.0b)
│   ├── double-link-builder.py       # Wikilink builder (3-stage funnel v2)
│   └── roadmap-editor.py            # Optional: browser-based roadmap editor
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
# Obsidian Learning（中文）

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

### 快速开始

```bash
git clone https://github.com/Easonnotsing/obsidian-learning.git ~/.agents/skills/obsidian-learning
pip install pypdf
```
