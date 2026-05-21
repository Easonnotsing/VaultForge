---
name: VaultForge
description: >-
  Process learning materials into structured Obsidian atomic notes with roadmaps, MOCs, and double-links.
  Auto-generate study vaults from PDFs/Markdown with AI-powered note-taking, knowledge linking, and deep research.
  Supports English and Chinese output. Use when the user wants to build a study vault from PDFs/Markdown.
  将学习资料（PDF/Markdown 等）转为带路线图、MOC、双链与终检的 Obsidian 原子笔记知识库。支持中英文输出。用户希望「从材料到笔记库」时使用。
---

# VaultForge

Complete workflow for transforming learning materials into structured Obsidian atomic note knowledge bases.

## Core Principles

### ⚠️ CRITICAL: Must Read All Designated Files Completely

**Absolutely forbidden to generate a learning roadmap or notes based on partial content.**

- Must read **all** learning files selected by the user
- **Prefer single-pass full reads** of entire files; use batched reading only when encountering technical limits
- If batched reading is necessary (e.g., PDF at 50 pages/batch), **auto-continue without user confirmation**
- Only generate the learning roadmap after confirming all content has been read

### ⚠️ CRITICAL: Atomic Notes to Knowledge Points — Default 1:1 + Proportion Calibration

**Default**: Each bullet knowledge point in the outline maps to **one** atomic note; note titles match bullet text (or are normalized filenames).

**Allowed exceptions** (must satisfy the "proportional to source material" rule below **simultaneously**, and include a **brief rationale** during roadmap confirmation):

- Knowledge point with very little source material: may **merge** with adjacent bullet into one atomic note (outline must sync: merge bullets or mark "merged")
- Knowledge point with extensive source material: may **split** into multiple atomic notes (outline splits into multiple bullets or sub-numbering)

**Forbidden**: Arbitrary merging/splitting without material evidence; mismatch between outline bullet count and atomic note count.

---

### ⚠️ CRITICAL: Knowledge Point Granularity Proportional to Source Material

**Avoid over-fragmentation or content neglect:**

| Situation | Principle | Example |
|-----------|-----------|---------|
| Source material on a knowledge point is sparse | Merge into a related topic; do not create a standalone atomic note | 1 page → merge with adjacent knowledge point |
| Source material on a knowledge point is rich | Split into multiple standalone atomic notes | 10 pages → split into 2-3 knowledge points |
| Large content span but logically complete | Keep as one knowledge point; ensure discussion is complete | 15 coherent pages → 1 detailed atomic note |

**Judgment criteria**:
- Content volume of a single atomic note should be proportional to the corresponding section in the source material
- Sparse knowledge points may be merged; rich ones may be split
- Goal: each atomic note has **sufficiently rich content** to support a 200+ word detailed explanation

---

### ⚠️ CRITICAL: Atomic Note Content Must Be Rich and Thorough

**Atomic notes are teaching materials, not outlines. They must enable a complete beginner to understand the knowledge point.**

Every atomic note must contain:
- **Detailed explanation**: no less than 200 words of core concept exposition — background, definition, principle, application scenarios
- **Case study**: a complete case from the learning materials, with background, process, outcome analysis
- **Original citation**: quote the most relevant original passage (50-150 words), with complete source attribution (document name, author, page range)
- **Reflection questions**: thought-provoking questions that promote deep understanding, not superficial queries

If a note is overly simplified (e.g., bullet points only), it must be reworked.

### Batch Confirmation Principle

**Avoid one-by-one confirmation; use batch confirmation mode:**
- Phase 1: After roadmap generation, present the full version once, ask "continue" or "modify"
- Phase 2: After file structure creation, present all created folders and files once
- Phase 3: After content filling, present a fill result summary once
- Phase 4: After wikilink establishment, present a link summary once

### Wikilink Standard

**Wikilinks are not keyword associations — they are based on logical relevance:**

1. **Derivation**: one note's conclusion is derived from another
2. **Analogy**: the principles of two notes can be analogized
3. **Contradiction**: two notes reach contradictory conclusions requiring debate
4. **Application**: one note's application scenario involves another's concept
5. **Context**: two notes belong to different aspects or development stages of the same domain

**Forbidden: establishing wikilinks based purely on term similarity.**

## Interaction Conventions

All user confirmation points follow a uniform pattern:
- Reply "continue" / "confirm" → proceed to next step
- Reply "modify + specific feedback" → revise and re-present for confirmation
- Reply with numbers (e.g., "1,3") → select corresponding options
- File list format: number + [✓/ ] + emoji + filename + meta info
- Progress report format: emoji + percentage bar + completed/in-progress status
- **Batch confirmation principle**: complete a phase → present results once → request confirmation once

## 开始前：选择输出语言 / Select Output Language

**这是整个 skill 的第一步，在任何其他操作之前必须执行。**
**This is the first step. It MUST execute before anything else.**

```
🌐 请选择输出语言 / Please select output language：

  1. English
  2. 中文

请回复编号 / Reply with number：
```

用户选择后 / After selection，**立即执行以下切换**：

1. **对话语言切换**：此后的所有用户对话、进度报告、确认提示、错误信息**必须**使用所选语言。The agent MUST use the selected language for ALL subsequent dialogue.
2. **生成内容语言**：全部后续生成文本使用所选语言。All generated content uses the selected language.
3. **笔记章节标题**：使用所选语言对应的标签。Section headers use the selected language's labels.
4. **原文引用**：保留源语言，不翻译。Original citations remain in source language.

| Section / 章节 | English | 中文 |
|------|---------|------|
| Core Concepts / 核心概念 | `## Core Concepts` | `## 核心知识点` |
| Case Study / 相关案例 | `## Case Study` | `## 相关案例` |
| Original Text / 原文引用 | `## Original Text` | `## 原文引用` |
| Reflection Questions / 核心思考 | `## Reflection Questions` | `## 核心思考` |

如果用户选择了 English，你在此之后对用户说的**每一句话**都必须是 English。

## Use Cases

- User provides learning materials (PDF, Markdown, etc.)
- Need to generate a learning roadmap
- Need to create atomic notes and MOCs
- Need to establish inter-note wikilinks

## Complete Workflow

### Phase 0: Vault Scan and Mode Selection

> **Execution note**: Phase 0 is executed directly by the main agent from these SKILL.md instructions. It does not have a separate sub-agent file — unlike Phases 1-3 which delegate to `roadmap-generator`, `file-structure-creator`, and `atomic-note-filler`. The scan logic (file detection, vf status counting, mode selection) requires direct filesystem access and cross-phase orchestration decisions that are best handled by the main agent's tool set.

**Executed before Phase 1.** Scans the selected folder to detect whether an existing VaultForge knowledge base is present. Determines fresh generation vs incremental update.

**Step 0.1: Scan for Existing VaultForge Notes**
- Scan the selected folder and subfolders for `.md` files with `vf: true` in frontmatter
- Load `.obsidian-learning-progress.md` if it exists (contains `vf_processed_files` list)
- **Detect existing roadmap**: look for `Learning Roadmap v* - {Topic}.md` files (v1, v2, ...) AND legacy files named `Learning Roadmap - {Topic}.md` (no version suffix, pre-v2.2.0). If both exist, prefer the highest v-number.
- Count notes by `vf_status`:

```
Phase 0 scan result:
  Existing VaultForge notes: 48
    pristine (auto-updatable): 32
    user_modified (read-only): 14
    locked (untouched): 2
```

**Step 0.2: Detect New Materials**
- List all files in the selected folder
- Compare against `vf_processed_files` from `.obsidian-learning-progress.md` (by filename + hash if available)
- Classify each file using a two-layer label: **Status** (processing state) + **Format** (file type):

**Status labels** (mutually exclusive):

| Label | Condition | Meaning |
|-------|-----------|---------|
| `NEW` | Not in `vf_processed_files` | Unprocessed; will be read in this session |
| `DONE` | In `vf_processed_files` | Already processed in a previous session |

**Format labels** (applied alongside status):

| Label | Condition |
|-------|-----------|
| `📄 [PDF]` | Extension `.pdf` |
| `📝 [Markdown]` | Extension `.md` |
| `📋 [Text]` | Extension `.txt` |
| `❓ [Unknown]` | Any other extension |

**Combined display format**: `NEW   📄 [PDF]`, `DONE  📄 [PDF]`

In the user-facing file list, format labels are shown inline; the Phase 0.3 mode selection and Phase 1.2 file selection use only the status label (NEW/DONE) for logic.

**Step 0.3: Mode Selection**

If both existing notes and new materials are detected, present mode selection:

```
📋 VaultForge knowledge base detected: Digital Transformation

   New materials found: 2 files
   Existing notes: 48 (32 pristine / 14 user_modified / 2 locked)

   1. Incremental update — add new notes, extend existing framework, never modify user edits (recommended)
   2. Full regenerate — rebuild from scratch (existing notes preserved but superseded)
   3. Skip — do nothing

   Reply with number:
```

- **Incremental update** → set `incremental_mode = true` for all subsequent Phases
- **Full regenerate** → proceed with existing Phase 1-6 as-is (user keeps old notes but new pipeline runs fresh)
- **Skip** → end workflow

If no existing notes are found, proceed directly to Phase 1 (normal mode).

**Step 0.4: Degradation and Error Handling**

| Failure Scenario | Handling |
|------------------|----------|
| `.obsidian-learning-progress.md` missing | Treat all files as NEW (fresh generation). No error — this is the initial-run case. |
| `.obsidian-learning-progress.md` corrupt / unparseable | Warn the user: "Progress file unreadable — treating all files as NEW." Proceed to mode selection as if it didn't exist. |
| `vf_processed_files` missing or empty in progress file | Treat all files as NEW (same as missing progress file). |
| Permission error / inaccessible file during scan | Skip the file, continue scanning. Report skipped count at end of scan: "⚠️ 3 files skipped (inaccessible)." |
| Zero scan-able files in folder | "📁 Selected folder contains no readable files. Please choose a folder with PDF or Markdown files." → return to Step 1.1. |
| Hash mismatch in `vf_processed_files` | File name matches but content hash differs → treat as NEW (user may have updated the source). Log a note: "h: hash mismatch for {filename} — treated as NEW." |
| Existing notes detected but no roadmap file found | Warn: "Found {N} VaultForge notes but no roadmap file. Suggesting fresh generation." → offer only options 2 (Full regenerate) and 3 (Skip). |
| `vf: true` false positives | Phase 0.1 scan checks frontmatter for `vf: true`. If non-VaultForge notes happen to also have this field, they will be miscounted. Mitigation: document that `vf: true` is reserved for VaultForge use. |

### Phase 1: Learning Roadmap Generation

**Step 1.1: Detect Vault and Select Folder**
- Auto-detect the Obsidian vault root directory
- Present a text list for the user to select a folder
- Proceed after user confirmation

**Step 1.2: Auto-Detect File List**

In **normal mode**: identical to existing behavior — list all files, user selects.

In **incremental mode**: use the file classification from Phase 0.2. NEW files default to selected; DONE files default to unselected.

```
📁 Selected folder: Digital Transformation/

  File list (incremental mode — new files pre-selected):

  NEW     1. [✓] 📄 [PDF] Platform Model Research.pdf         - 89 pages
  NEW     2. [ ] 📝 [Markdown] Industry Analysis Report.md     - 4,200 words
  DONE    3. [ ] 📄 [PDF] Digital Transformation Guide.pdf    - 329 pages
  DONE    4. [ ] 📄 [PDF] Customer Strategy Core.pdf          - 156 pages

  Selected: 1 file (new material)

  Confirm to start reading (reply "continue"), or enter numbers to adjust selection (e.g., "1,3"):
```

**Step 1.3: Complete Reading of Learning Materials**
- Prefer **single-pass full reads** of each file
- If a file is too large (e.g., PDF), auto-batch (50 pages/batch), **no user confirmation needed**
- Real-time progress: `📖 Reading: filename.pdf - [150/329 pages] (46%)`
- Completion report: `✅ Reading complete! X/Y pages (100%)`
- **Record stat**: append `vf_source_words={total word count}` to `.obsidian-learning-progress.md`. The agent counts words across all selected source files and records the total.

**Step 1.4: Generate and Confirm Roadmap**
- Generate the learning roadmap based on the complete reading
- Present the **full version** roadmap (with detailed knowledge points, cases, original citations) for user preview
- User replies "continue" to proceed to saving; replies "modify + feedback" to revise and re-confirm

**Display format example**:
```
📋 Generated full learning roadmap

## 01. Digital Transformation Fundamentals

### Core Concept Framework

**Digitization vs Transformation**
- Detailed explanation: ...
- Case: ...
- Original citation: ...

---

Would you like to modify? Reply:
  - "continue" → save and proceed to next step
  - "modify + specific feedback" → revise
```

**Step 1.5: Save Two Files**

**⚠️ The outline version MUST contain knowledge points (bullet points). Only keeping H2/H3 is forbidden.**

Save two files:
- `Learning Roadmap (Full) v1 - {Topic}.md` — detailed version (with full descriptions, cases, original citations)
- `Learning Roadmap v1 - {Topic}.md` — outline version (**must contain H2/H3/bullet three-level structure**)

**Correct outline format example**:
```markdown
# Learning Roadmap v1 - Digital Transformation

## 01. Digital Transformation Fundamentals

### Digitization vs Transformation

- Definition of digitization and transformation
- Core difference: incremental change vs fundamental change
- Three elements of transformation

### Transformation Framework

- Five Stage model
- Digital maturity assessment
- Transformation roadmap design
```

**⚠️ Outline bullet rules**:
- Bullets contain only knowledge point **names/titles**; descriptions, citations, or explanations are forbidden
- Correct: `- Definition of digitization and transformation`
- Wrong: contains explanatory text or original citation references
- The outline **must contain the H2/H3/bullet three-level structure**; missing bullets = missing knowledge points during file structure creation

**Step 1.5b: Parse Roadmap Statistics (auto-executed after save)**

**The Agent reads the saved complete roadmap file to parse structure — NOT model self-reported numbers.** This is a deterministic operation, unaffected by model size.

Procedure:
1. Use the Read tool to open the saved complete roadmap `.md` file
2. Parse line by line:
   - `^## ` → H2 category count +1
   - `^### ` → H3 topic count +1
   - `^- ` → knowledge point bullet count +1
3. Aggregate and report actual statistics:

```
📊 Roadmap statistics (parsed from saved file):

   H2 categories: 4
   H3 topics: 12
   Knowledge points (bullets): 48
   📊 Estimated atomic notes: 48, MOCs: 12
   ⏱️ Estimated time: ~15-20 minutes

⚠️ Knowledge point / page proportion check:
   - Transformation Overview: 6 points / 12 pages → ⚠️ high ratio (0.5), suggest merge
   - Customer Strategy: 3 points / 28 pages → ✅ reasonable ratio (0.11)

⚠️ Hierarchy structure check (each H2 must have ≥2 H3):
   - Transformation Overview: 4 H3s → ✅ structure is reasonable
   - Strategic Management: 1 H3 → ❌ redundant hierarchy
     Suggestions: a) split b) merge into adjacent H2 c) elevate H3 to H2

Would you like to modify the roadmap?
  - "continue" → proceed to Phase 2
  - "modify + specific feedback" → return to Step 1.4 to revise, re-save, and re-parse
```

**Proportion check standards**:
| Ratio (points/pages) | Assessment | Suggestion |
|----------------------|------------|------------|
| > 1.0 | ⚠️ Over-fragmented | Merge adjacent knowledge points |
| 0.1 - 1.0 | ✅ Reasonable | No adjustment needed |
| < 0.1 | ⚠️ Content may be sparse | Consider merging or expanding |

**Hierarchy check standards**:
| H3s under H2 | Assessment | Suggestion |
|-------------|------------|------------|
| 0 | ❌ Fatal | H2 must have H3 topics |
| 1 | ❌ Redundant hierarchy | a) Split into multiple H3s b) Merge into adjacent H2 c) Elevate H3 to H2 |
| ≥ 2 | ✅ Reasonable | No adjustment needed |

> Reason for switching statistics source from "model self-report" to "file parse": to avoid counting inaccuracies caused by medium-scale models (e.g., Minimax-M2.7) estimating their own generation.

### Phase 2: File Structure Creation

**In incremental mode**, Phase 2 operates in **add-only** mode:
- Never rename, move, or delete existing folders/files
- Create only what is new in the incremental roadmap
- MOCs for new H3 topics are created as new files; existing MOCs are not modified
- Existing folders are left untouched even if the new roadmap suggests restructuring

**Step 2.1: Batch Create Folders and Files**

**Folder structure rules**:
- H2 → first-level folder (format: `XX. Category Name`)
- H3 → second-level folder under H2 (placed directly inside the H2 folder)
- MOC → **must be placed inside the H3 folder**, not the H2 folder
- Atomic notes → placed in the corresponding H3 folder

**Correct structure example**:
```
vault/
├── 01. Digital Transformation/
│   ├── Overview/              ← H3 topic folder
│   │   ├── Overview MOC.md    ← ✅ MOC inside H3 folder
│   │   ├── Digitization vs Transformation.md
│   │   └── Transformation Framework.md
│   └── Customer Domain/
│       ├── Customer Domain MOC.md    ← ✅ MOC inside H3 folder
│       └── ...
├── 02. Strategic Management/
│   ├── Strategic Analysis/
│   │   ├── Strategic Analysis MOC.md    ← ✅ MOC inside H3 folder
│   │   └── ...
```

**Incorrect structure example** (MOC in H2 folder, **must avoid**):
```
vault/
├── 01. Digital Transformation/
│   ├── Overview MOC.md        ← ❌ Wrong! MOC must not be at H2 level
│   ├── Overview/              ← H3 topic folder
│   │   └── ...
```

**Creation steps**:
0. **Pre-creation validation**: first read the outline roadmap, parse the H2/H3/bullet hierarchy, and cross-validate with the planned folder structure
1. Create folder structure following H2/H3 hierarchy
2. Create MOC notes (blank template) **inside each H3 topic folder**
3. Create **blank atomic note files** for each bullet knowledge point (frontmatter with `vf: true` and `status: draft`, title only, **no body content**)
4. **Present all created files at once** after creation

**⚠️ Important: Step 2 only creates empty files, does not fill content**
- MOC notes: frontmatter and title only, body empty
- Atomic note files: frontmatter (with `status: draft`) and title only; sections like `## Core Concepts`, `## Case Study` etc. are blank
- **Content filling is done in Phase 3**; Step 2 strictly forbids writing any body content

**Step 2.1 Validation and Confirmation**:

**Validated items**:
- H2 category count matches the outline
- H3 topic count matches the outline
- Knowledge point (bullet) count matches the outline
- Folder naming matches outline titles

**Confirmation display**:
```
📋 Phase 2 File Structure Creation Preview

📁 Folder structure to be created:
├── 01. Digital Transformation/
│   ├── Overview/
│   │   ├── Overview MOC.md
│   │   ├── Digitization vs Transformation.md
│   │   └── ...
│   └── ...

📊 Statistics:
- H2 categories: 4
- H3 topics: 12
- Atomic notes: 48

Confirm creation? Reply:
  - "confirm" → start creating
  - "cancel" → return to modify roadmap
```

**Step 2.2: Fill MOC Content (Atomic Note Links Only)**
- Write each atomic note's wikilink from the H3 topic folder into the corresponding MOC's `## Related Notes` (or equivalent section)
- **Do not modify the outline roadmap in this step**: bidirectional links between the outline roadmap's "H3 ↔ MOC" and "MOC ↔ Roadmap" are **unified in Phase 4.3** (or via the `scripts/double-link-builder.py` roadmap-MOC logic), avoiding duplicate insertion with Phase 4

**`## Related Notes` section: shared responsibility**:

| Writer | Content | When |
|--------|---------|------|
| Phase 2.2 | `- [[atomic note name]]` (links to atomic notes in same H3 folder) | After file creation, before content fill |
| Phase 4.3 | `- [[../../Learning Roadmap v1 - {Topic}\|Learning Roadmap]]` (backlink to outline roadmap) | After wikilink building |
| Phase 4.2b | `- [[other note]] (relationship_type)` (inter-note wikilinks) | During wikilink classification |

Each phase only adds its own links; never removes links from a previous phase. Scan for duplicates before insertion.

**Step 2.3: Validate Structure**
- Check that folder structure and note counts match the roadmap
- If discrepancies exist, fix before proceeding to Phase 3

### Phase 3: Content Generation (Parallel)

**Step 3.0: Breakpoint Recovery Check (Mandatory)**

Must execute before entering Phase 3:

1. Scan the frontmatter `status` field of all atomic note files in the vault:
   - `status: draft` → unfilled, eligible for fill queue
   - `status: filling` → crashed residue, two cases:
     - **`{note}.md.tmp` exists**: crashed before rename. If .tmp content is complete (file size > 0, frontmatter closed), rename to `.md` and set status to `filled`; otherwise delete .tmp, keep original `.md` as `draft`
     - **`{note}.md.tmp` does not exist**: rename succeeded but status update crashed. The `.md` file content is complete; directly change status from `filling` to `filled`
   - `status: filled` → already filled, skip
   - `status: reviewed` → already reviewed, skip
   - `status: needs_review` → exceeded max retries, report to user for manual handling, do not enter fill queue
2. Clean orphan `.md.tmp` files (no corresponding `.md` exists, or the corresponding `.md` status is neither `filling` nor `draft`)
3. Read `.obsidian-learning-progress.md` to confirm the last interruption point
4. Report breakpoint recovery status to user:
   ```
   📊 Breakpoint Recovery Check

   Total 48 atomic notes:
     ✅ Completed (filled/reviewed): 25
     ⏳ Pending fill (draft): 21
     ⚠️ Needs manual review (needs_review): 2
     🗑️ Residue cleaned: 0

   Resume from breakpoint?
     "continue" → fill only 21 incomplete notes
     "restart" → reset all notes to draft and refill all
   ```

**Step 3.0b: Context Pre-Extraction**

**Automatically executed by `scripts/context-extractor.py`.** Replaces the old manual "read roadmap → extract source paragraphs per knowledge point" workflow.

**Execution**:
```
python3 scripts/context-extractor.py <vault_path> <complete_roadmap_path> --output context_packets.json
```

**Script capabilities**:
1. Parse `source_range` annotations in the complete roadmap (supports multi-range: `file.pdf:12-15, 45-48, 102`)
2. For PDF sources: use PyPDF2 to extract specified pages (with ±1 page buffer), stitch page-by-page
3. For Markdown/TXT sources: extract full file content (proportional extraction if page numbers are annotated)
4. Output structured context packet JSON (top-level fields: `vault_path`, `buffer`, `total_knowledge_points`, `packets`):
   - Each packet contains `note_file`, `title`, `source_excerpts` (array, each item `{source, pages, text}`)

**Degradation strategy**: If PDF source lacks PyPDF2 dependency or file is unreadable, the script outputs a stderr warning, skips that file, and sets the corresponding excerpt's `text` to an empty string. The filling agent then degrades to locating content from the full source material.

**Only when** no `source_range` annotations exist in the complete roadmap (extremely old legacy roadmaps), skip this step and fall back to passing the **full original source files** (PDFs, Markdown) directly to the filler agent.

> ⚠️ **Critical: the degradation source is the original learning material (PDF/Markdown files), NEVER the roadmap.** The roadmap is a structural outline — it has been condensed, summarized, and may not contain case studies or detailed exposition. If the filling agent receives only the roadmap as input, the resulting notes will be lossy (information decay), miss case studies, and potentially introduce hallucinations.

**When context-extractor.py cannot extract context, the filler must:**
1. Receive the **full text of all selected source files** (not the roadmap)
2. Read the relevant sections from those source files to fill each note
3. **Never** use the roadmap's descriptive text as a replacement for source content

**Step 3.1: Compute Parallel Task Distribution**

Calculate required agent count based on **pending** atomic note count (i.e., status=draft count):

```
Required agents = ceil(pending note count / 10)
```

**Examples**:
- 8 notes → ceil(8/10) = 1 agent (sequential)
- 15 notes → ceil(15/10) = 2 agents
- 35 notes → ceil(35/10) = 4 agents
- 60 notes → ceil(60/10) = 6 agents

**Distribution principles**:
- Each agent handles **no more than 10** atomic notes
- Distribute as evenly as possible for balanced workload per agent
- Each agent receives only the **context packets** for its assigned notes (not the full learning material)
- Record each agent's assigned note list

**⚠️ When atomic notes exceed 50**:
- System prompt: `📢 Detected {N} atomic notes — a large count`
- Suggest the user consider:
  1. Should the learning roadmap be streamlined to reduce knowledge points?
  2. Should processing be batched (handle core chapters first)?
  3. Continue with the current flow?
- **Default to continue**, unless the user explicitly requests returning to modify the roadmap

**Step 3.2: Parallel Content Fill**

Launch the specified number of agents **in parallel** to execute the fill task. Each agent must follow the **atomic write specification**:

**Environment and degradation**: If the current client does not support sub-agent orchestration, or if no sub-agent produces output within 5 minutes of parallel dispatch, fall back to sequential execution. In sequential mode, group notes in batches of ≤10 and fill batch by batch. Progress report format remains unchanged.

**Atomic write specification (vf_ frontmatter)**:
1. The filling agent first creates `{note}.md.tmp` with the complete content (**note: extension is `.md.tmp`, not `.tmp`**)
2. All generated notes **must** include these frontmatter fields:
   ```yaml
   ---
   vf: true
   vf_version: v3.1.0
   vf_status: pristine
   vf_session: initial|incremental-{date}
   status: filling
   ---
   ```
   - `vf: true` — marks the note as VaultForge-generated
   - `vf_status: pristine` — initial value; system may detect user edits later by comparing `mtime` vs `date`
   - `vf_session` — `initial` for first generation, `incremental-YYYY-MM-DD` for incremental sessions

**`vf_status` values**:

| Value | Set By | Meaning | Refresh Behavior |
|-------|--------|---------|------------------|
| `pristine` | System (auto-generated) | Note never edited by user; auto-updatable | Eligible for Phase 5.4b refresh |
| `user_modified` | System (detected) | User edited the note (mtime > date + delta); read-only | Excluded from auto-refresh |
| `locked` | User (manually edits frontmatter) | User explicitly froze this note; no auto-touch | Excluded from auto-refresh |

- **`locked`**: A user who wants to protect a specific pristine note from auto-refresh sets `vf_status: locked` in the frontmatter. The system never changes this value. It differs from `user_modified` in that the note body is unchanged — the user is simply choosing to keep it frozen.
- **`user_modified`**: Detected automatically when a note's file modification time diverges from its frontmatter `date` by more than 5 minutes, or when the content hash changes. The system sets this during Phase 0 scanning.
3. After writing, verify `.md.tmp` file integrity (file size > 0, frontmatter enclosed)
4. After verification passes, rename `.md.tmp` to `.md` (filesystem-level atomic operation)
5. Update frontmatter `status` to `filled`
6. **Immediately** append to `.obsidian-learning-progress.md`: `[Phase 3] {note}.md → filled`

```
[agent-1] 📝 Filling: NoteA, NoteB, NoteC
[agent-2] 📝 Filling: NoteD, NoteE, NoteF
[agent-3] 📝 Filling: NoteG, NoteH
...
```

**Progress report** (real-time display):
```
📊 Phase 3 Progress: [████░░░░░░] 40% (4/10 notes filled)
  ✅ Done: NoteA, NoteB, NoteC, NoteD
  ⏳ In progress: agent-2 (NoteE, NoteF)
  ⏳ In progress: agent-3 (NoteG, NoteH, NoteI, NoteJ)
```

**Step 3.3: Quality Review (Default On)**

**Quality review is executed by default**, unless the user explicitly requests skipping:
- Use the `note-reviewer` agent to review all **filled** atomic notes (skip `status: draft` and `.tmp` files)
- **In incremental mode**: pass `incremental_mode: true` to the reviewer — only review newly filled notes; skip existing `reviewed` notes
- Check content richness (200+ words, case study, original citation)
- Check for no significant duplication
- Check for no obvious errors
- Check format compliance

**Review output format**:
```
📋 Quality Review Report

## Results
✅ Pass: 8 notes
⚠️ Needs Fix: 2 notes

## Notes Needing Fixes
- [HIGH] NoteX: content too simplified, missing case study
- [MEDIUM] NoteY: missing original citation

## Suggestions
Fix the above issues and resubmit for review
```

**Step 3.4: Repair and Retry**

If any notes fail quality review or an agent execution fails:

**Failed notes enter the repair queue**:
```
🔧 Repair queue: NoteX, NoteY
```

**Reassign tasks**:
- Reassign failed notes to agents (prefer the agent that previously handled that note)
- Reset status to `draft` before repair (ensures breakpoint recovery can identify)
- Re-execute fill
- Re-submit for review

**Retry limit**: maximum **2 retries**. Notes exceeding this limit:
- Marked as "needs manual review" in the final report
- Status set to `needs_review`

**Step 3.5: Batch Report Results**

Present once after completion:
```
📊 Phase 3 Completion Report

Total: 12 atomic notes
  ✅ Direct pass: 10
  🔧 Passed after repair: 1
  ⚠️ Needs manual review: 1 (NoteZ - exceeded max retries)

📋 Progress file updated: .obsidian-learning-progress.md
Duration: X minutes
```

Also append `vf_atomic_notes={count}` to `.obsidian-learning-progress.md` (count of non-MOC, non-roadmap notes).

**In incremental mode**, also update `vf_processed_files` in `.obsidian-learning-progress.md` to include the newly processed source files from this session, recording filename and hash for future incremental scans.

### Phase 4: Wikilink Building

**In incremental mode**, Phase 4 establishes links with two tiers:
- **New ↔ New**: all three funnel stages execute normally, links written directly
- **New ↔ Old**: only **suggestions** are generated; no existing notes are modified
- **Old ↔ New**: never modify existing notes

The agent runs the three-stage funnel on all note pairs (new + old) but writes links only for new-to-new pairs. New-to-old suggestions are collected into a JSON file for the Phase 5 Update Report.

#### Phase 4 Execution Strategy (Three-Stage Funnel — Main Agent & Script Collaboration)

**Design intent**: Classifying the 5 logical relationship types (derivation/analogy/contradiction/application/context) is fundamentally a semantic understanding task. Pure keyword matching achieves only ~20-30% recall. Use a "funnel" strategy for layered processing:

```
All note pairs (n*(n-1)/2)
    ↓ Stage 1: Structural affinity filter (zero cost, eliminates 80-85%)
Structurally affine candidates (~n*3 to n*5)
    ↓ Stage 2: TF-IDF semantic similarity + keyword heuristics (low cost)
High-similarity candidates (~n/2 to n)
    ↓ Stage 3: LLM batch classification (controlled token cost)
Final links
```

**Detailed flow**:

1. **Default path (recommended)**
   - **Step 4.1**: Run `scripts/double-link-builder.py`, executing stage 1+2 (structural filtering + TF-IDF + keyword heuristics), producing a **candidate pair list** (`candidates.json`).
   - **Step 4.2**: The main agent reads the candidate pair list and uses LLM to classify each candidate pair into the 5 relationship types (can batch process, 5-10 pairs per batch). Only writes to `## Related Notes` when a relationship type is positively identified.
   - **Step 4.3**: The main agent completes bidirectional links between the outline roadmap ↔ each MOC (coexisting with the atomic note list already written in Phase 2.2), **scanning before insertion** for existing equivalent `[[...]]` links; **duplicate lines forbidden**.

2. **Script-only path (non-LLM degradation)**
   - When the environment does not support LLM calls: `double-link-builder.py` runs with `--mode strict`, using only stage 1+2 deterministic rules (structural filtering + TF-IDF > threshold + keyword triggers). Produced links have **high precision but low recall** (covering ~40-50% of logical relationships). The script outputs an estimated coverage percentage.
   - Users can manually complete missing links in Obsidian.

3. **Fully agent-driven path**
   - When note count ≤ 20: the script can be skipped; the main agent directly reads all notes + roadmap and completes relationship classification in one pass. Token-wise this remains manageable (~400 pairs, batch processing ~40 calls).

4. **Forbidden**
    - Double-linking from "main agent already wrote Step 4.2 + uncleaned script run" within the same Phase;
   - Duplicate lines of `- [[same target]]` in `## Related Notes` (merge into one line).
   - Building links when stage 3 LLM outputs "none" (unrelated).

**Step 4.1: Run double-link-builder.py (Stages 1+2)**

```
python3 scripts/double-link-builder.py <learning_folder_path> <roadmap_name> --output candidates.json
```

> ⚠️ **Scope**: The `<learning_folder_path>` is the folder selected in Phase 1.1 — the one containing the learning materials and generated atomic notes. **Do not pass the Obsidian vault root.** The script recursively scans from this path, so passing the entire vault will process unrelated notes and produce massively inflated results.

The script outputs `candidates.json`, with a top-level `pairs` array. Each element contains `note_a`, `note_b`, `title_a`, `title_b`, `scores` (`{structural, tfidf_cosine, keyword_rules}`), `preview_a`, `preview_b`.

**Step 4.2: LLM Batch Classification (Stage 3)**

The main agent reads `candidates.json`, batches candidate pairs (5-10 pairs per batch), and sends them to an LLM for classification:

**LLM Classification Prompt Elements** (constructed by the main agent):

- Context: tell the LLM to act as a knowledge graph builder
- Relationship definitions: list the 5 relationship types + `none` (must have `none` to enforce "when in doubt, link nothing")
- Input: batch-filled candidate note pairs (each pair includes title + preview)
- Output format: `<id>|<relation>|<reason>` (pipe-delimited, reason limited to one sentence)
- Example: `1|derivation|Digitization is a technical prerequisite for transformation` / `2|none|`

**Classification result handling**:
- `none` → skip, do not build a link
- One of the 5 types → add bidirectional wikilinks to both `note_a`'s and `note_b`'s `## Related Notes`, optionally annotating the relationship type in parentheses (e.g., `[[Transformation Framework]] (derivation)`)
- Dedup check before insertion (skip if an equivalent wikilink already exists)

**Step 4.3: Build Roadmap ↔ MOC Bidirectional Links**
- This is the **single canonical entry point**: in the outline roadmap, add a wikilink pointing to the corresponding MOC after each H3; in each MOC's `## Related Notes`, add a backlink to the outline roadmap (coexisting with the atomic note list already written in Phase 2.2; **do not re-insert** existing links)
- If equivalent links already exist, only fill in gaps
- Example (`##` = H2 category, `###` = H3 topic; MOC link immediately follows the corresponding **H3** title line):
  ```markdown
  <!-- In the outline roadmap -->
  ## 02. Customer Domain

  ### Customer Strategy Core

  [[02. Customer Domain/Customer Strategy Core/Customer Strategy Core MOC|Customer Strategy Core]]

  - Knowledge Point 1
  - Knowledge Point 2

  <!-- In the corresponding MOC -->
  ## Related Notes

  - [[../../Learning Roadmap - Digital Transformation Roadmap|Learning Roadmap]]
  ```

**Step 4.4: Batch Report Results**
- Present a summary of all added wikilinks. **Must include an exact count** of inter-note wikilinks written (excluding MOC and roadmap links) — this count is used in Step 6.5 for the achievement card.
- **Record stat**: append `vf_wikilinks={count}` to `.obsidian-learning-progress.md`
- Confirm completion

### Phase 5: Final Review and Core Question Generation

**Step 5.1: Review All Atomic Notes**

Must check the following items item by item; **issues found must be fixed**:

#### 5.1.1 Atomic Note Integrity Check
- [ ] Atomic note count matches roadmap knowledge point count
- [ ] Every atomic note file has been created
- [ ] **All atomic notes have `status` of `filled` or `reviewed`** (no residual `draft` / `filling`)
- [ ] `needs_review` notes have been listed and acknowledged: N total require manual review
- [ ] No orphan `.md.tmp` files remain
- [ ] Note content meets richness requirements (Core Concepts 200+ words, case study complete, original citation accurate)
- [ ] No significant content duplication
- [ ] No obvious errors or misinterpretations

#### 5.1.2 MOC ↔ Atomic Note Wikilink Check
- [ ] Every MOC file has a `## Related Notes` section
- [ ] All atomic notes under that MOC's folder have been wikilinked to the MOC
- [ ] Link format is correct: `[[filename|display text]]`
- See [references/obsidian-structure.md](./references/obsidian-structure.md) "MOC and Atomic Notes" section for format specification

#### 5.1.3 Roadmap ↔ MOC Wikilink Check
- [ ] Each H3 topic in the outline roadmap has been linked to the corresponding MOC
- [ ] Each MOC note has a backlink to the outline roadmap
- See [references/obsidian-structure.md](./references/obsidian-structure.md) "Roadmap and MOC Bidirectional Links" section for format specification

**Step 5.2: Generate "Core Questions" Note**

**Storage location**: `{vault}/{learning materials folder}/Core Questions.md`

Create the `Core Questions.md` file directly in the same folder as the learning materials (PDF/MD files).

#### 5.2.1 Question Requirements

**Quantity limit**: no more than 5 core questions

**Quality standards**:
1. **Essential**: questions should cover the most essential knowledge, principles, and methodologies from the learning material
2. **Guiding**: questions should guide the user to learn more efficiently with a purpose, not simply retrieve information
3. **Logical**: questions should have logical progression among them; no obvious repetition or contradiction

#### 5.2.2 Question Structure

Each question should include:
- **Question title**: a concise core question
- **Question background**: explain why this question matters, what it addresses, the context
- **Sub-questions** (optional): break complex questions into 2-3 sub-questions

#### 5.2.3 Output Format

See [references/templates.md](./references/templates.md) for the complete `Core Questions Template`. Key format elements:

- No more than 5 core questions, each with question title + background + optional 2-3 sub-questions
- End with a `## Study Tips` section to guide active learning
- Storage location: `{learning materials folder}/Core Questions.md`

**Record stat**: append `vf_core_questions={count}` (the number of questions generated, always ≤5) to `.obsidian-learning-progress.md`.

**Step 5.3: Batch Report Final Results**

Present once:
- Total atomic notes, creation status, content quality review results
- MOC ↔ atomic note wikilink status
- Roadmap ↔ MOC bidirectional link status
- "Core Questions" note generated

If any check item is not passed, fix it before reporting the final results.

**After completion**: append `[Phase 5] Final review complete` to `.obsidian-learning-progress.md`.

**Step 5.4: Generate Incremental Update Report (incremental mode only)**

If `incremental_mode = true`, generate a `VaultForge Update Report - {date}.md` in the learning materials folder.

The agent compiles the report by aggregating:
- Phase 2: list of newly created folders, MOCs, and atomic notes
- Phase 3: count of filled notes (pristine vs user_modified vs locked)
- Phase 4: new-to-new link count + new-to-old suggestions
- Phase 5: any pristine notes eligible for content refresh (when new source pages cover existing notes)

**Report template**:
```markdown
---
title: VaultForge Update Report - {date}
date: YYYY-MM-DD
tags:
  - vaultforge-report
  - {topic}
---

# VaultForge Update Report - {date}

## New Files Created

**New H2 categories** (new folders):
- 03. New Category/...

**New notes in existing folders**:
- 01. Digital Transformation/Customer Domain/Customer Journey Map.md
- 01. Digital Transformation/Customer Domain/Omnichannel Strategy.md

## Wikilinks Established

| Scope | Count |
|-------|-------|
| New ↔ New | 28 |
| New → Existing (suggested) | 4 |

**Suggested new-to-existing links** (review and add manually if desired):
- [[Customer Journey Map]] → [[digitization-and-transformation]] (derivation)
- [[Omnichannel Strategy]] → [[digital-maturity-model]] (application)

## Notes Eligible for Refresh (pristine)

These notes have new source content available and can be auto-refreshed:

- [ ] digital-maturity-model.md — 8 new source pages available
- [ ] five-stage-model.md — 3 new source pages available

Reply "refresh 1,2" to regenerate selected notes, or "skip" to ignore.

## Protected Notes (not modified)

| Status | Count |
|--------|-------|
| User-modified (preserved as-is) | 14 |
| Locked (untouched) | 2 |

## Update Session

- Previous roadmap: Learning Roadmap v1 - {Topic}.md
- New roadmap: Learning Roadmap v2 - {Topic}.md
- `vf_session` on new notes: incremental-{date}
```

**After report generation**: append `[Phase 5] Incremental update report generated` to `.obsidian-learning-progress.md`.

**Step 5.4b: Execute Pristine Note Refresh (incremental mode, user-triggered)**

After the Update Report is presented, the agent **pauses** and hands control to the user:

```
📋 Notes eligible for refresh:

   1. [ ] digital-maturity-model.md — 8 new source pages available (original: 3, now: 11)
   2. [ ] five-stage-model.md — 3 new source pages available (original: 5, now: 8)

   Reply "refresh 1,2" to regenerate selected notes, or "skip" to ignore.
```

**Detection logic**: during Phase 5.4 report compilation, scan all notes with `vf_status: pristine` (exclude `locked` and `user_modified`). A note is refresh-eligible when:
- Its topic matches a knowledge point in the new roadmap (same or similar title, or same H3 folder membership)
- The new roadmap's `source_range` for that topic covers **more pages** than the note's original `source_range`
- Delta (new_pages − original_pages) is the number shown beside each entry

**User actions**:
- `skip` → no refresh, proceed to Step 5.5
- `refresh 1,2` → execute refresh for notes at those positions
- `refresh all` → execute refresh for all listed notes

**Refresh execution flow**:

1. Re-run `scripts/context-extractor.py` with `--note-filter digital-maturity-model.md,five-stage-model.md` (only extract packets for selected notes, using the new roadmap's `source_range`)

2. For each selected note, invoke `atomic-note-filler` in **refresh mode** — the filler:
   - Reads the existing `.md` file to preserve frontmatter
   - **Preserves**: `title`, `vf`, `vf_version`, `vf_status`, `tags`, `aliases`
   - **Updates**: `date` → current, `vf_session` → `refresh-YYYY-MM-DD`, `source_range` → new value (if changed)
   - Replaces the **body** (everything after `---` closing frontmatter) with fresh content
   - Uses atomic write protection (`.md.tmp` → verify → rename)

3. Progress report:
   ```
   🔄 Refreshing pristine notes...

   [1/2] ✅ digital-maturity-model.md — refreshed (11 pages)
   [2/2] ✅ five-stage-model.md — refreshed (8 pages)

   📊 Refresh complete: 2 notes updated
   ```

4. Append to `.obsidian-learning-progress.md`:
   ```
   [Phase 5.4b] Refreshed: digital-maturity-model.md, five-stage-model.md (2 notes, refresh-2026-XX-XX)
   ```

**After refresh (or skip)** → proceed to Step 5.5 (Phase 6 confirmation).

**Step 5.5: Phase 6 Execution Confirmation**

After Phase 5 completes, **must** ask the user whether to enter Phase 6:

```
📋 Phase 5 final review complete. Core Questions note generated.

Enter Phase 6 (Deep Research & Controversy Analysis)?
  Requires: deep-research skill or equivalent MCP / Web search tool
  - "continue" → enter Phase 6
  - "skip" → end workflow
```

- User selects "skip" → append `[Phase 5] Complete — Phase 6 skipped by user` to progress file, workflow ends
- User selects "continue" → enter Phase 6

### Phase 6: Deep Research & Controversy Analysis

**Step 6.1: Execute Deep Research**

#### 6.1.1 Research Topic Extraction

Extract from the learning roadmap:
- **Topic name**: the core topic of the learning material (e.g., "Digital Transformation")
- **Supplementary keywords**: key concepts, theoretical framework names

#### 6.1.2 Detect and Execute Deep Research

Execute the following steps:

1. **Execute deep research** using Firecrawl and Exa MCP tools. Use the full tool suite as appropriate — `firecrawl_search` to discover sources, `firecrawl_scrape` for full content, `firecrawl_agent` for autonomous multi-step research, `firecrawl_map` to explore sites, `exa_search` for academic or neural searches. Follow deep-research methodology: multi-source → synthesize → cited report.

2. If Firecrawl or Exa tools are unavailable, fall back to any available web search. If nothing available, skip Phase 6.

#### 6.1.3 Research Report Reception

Extract from the deep research output:
- **Executive Summary**: used for the summary section of the controversy analysis note
- **Sources**: used for the reference source list
- **Findings by topic**: used to identify consensus and controversies

Save the complete research report to:
`{learning materials folder}/{Topic} - Deep Research.md`

**Step 6.2: Parse Research Results**

#### 6.2.1 Mapping Research Output to Note Content

| Controversy Analysis Section | Corresponding Research Output |
|------------------------------|-------------------------------|
| Summary | Executive Summary |
| Undisputed (industry consensus) | Content consistently recognized across multiple sources in topic findings |
| Controversial (different views) | Content with divergent views across topic findings |
| Context-dependent | Content in Key Takeaways mentioning "depends on context" |
| Reference Sources | Sources list (extract the most valuable 5-10) |
| Discussion Questions | Generated based on controversial content |

#### 6.2.2 Parsing Principles

- **Extract rather than rewrite**: extract relevant content from the research report
- **Preserve sources**: all content must be source-attributed
- **Compare with learning material**: identify content that agrees or diverges from the learning material's views

**Step 6.3: Generate "Controversy Analysis" Note**

**Storage location**: `{vault}/{learning materials folder}/{Topic} - Controversy Analysis.md`

Create the `{Topic} - Controversy Analysis.md` file directly in the same folder as the learning materials (PDF/MD files).

#### 6.3.1 Note Structure

See [references/templates.md](./references/templates.md) for the complete `Controversy Analysis Template`. Contains six sections:

- Summary (200-300 words)
- Undisputed (Industry Consensus)
- Controversial (Different Views)
- Context-Dependent (No Universal Answer)
- Deep Discussion Questions for Experts
- Key Conclusions + Reference Sources + Study Suggestions

#### 6.3.2 Content Filling Guide

**Undisputed section**:
- Find views consistently recognized across multiple sources
- Explain why these views are widely accepted
- Cite authoritative sources as support

**Controversial section**:
- Identify divergence points between the learning material and other sources
- Objectively present all perspectives without bias
- Point out the core of the controversy and its roots

**Context-dependent section**:
- Identify methodology-level suggestions
- Explain applicability differences across different contexts
- Identify key determining variables

**Question list**:
- Questions should be open-ended and deep
- Avoid yes/no type questions
- Prioritize core topics frequently discussed by experts

**Step 6.4: Batch Report Results**

Present once:
- Deep research executive summary (how many sources researched, which aspects covered)
- Controversy Analysis note generated
- Reference source list

Ask the user: "📸 Generate an achievement share card? This takes about 1-2 minutes. Reply 'yes' or 'no'."

- If **no** → append `[Phase 6] Complete — Achievement card skipped by user` to progress file, workflow ends
- If **yes** → proceed to Step 6.5

**Step 6.5: Generate Achievement Share Card** (optional, user-confirmed)

After all phases complete, generate a shareable achievement image summarizing the learning results.

**Data collection** (aggregate from actual output files — never estimate from structural data):

| Stat | How to Count | Example |
|------|-------------|---------|
| Source words | Phase 1.2: count total words across all selected source files (PDF/MD). Round to nearest 0.1k. Do NOT count from generated notes — they are condensed output. | 51.5k |
| Atomic notes | Phase 3: count `.md` files in H3 subfolders. **Exclude** files with "MOC" in name. **Exclude** roadmap files. **Exclude** `Core Questions.md` and `*Deep Research.md` and `*Controversy Analysis.md`. | 45 |
| Core questions | Phase 5.2: count generated questions (always ≤5). | 5 |
| Wikilinks | Phase 4.4: count actual `[[wikilink]]` entries in `## Related Notes` sections of atomic notes. **Exclude** any link targeting a MOC file or roadmap file. Do NOT count structural candidates or estimate from folder hierarchy — scan the written files. | 18 |

**Data collection** (read from `.obsidian-learning-progress.md` — do NOT re-count):

Previous phases have already recorded these values. Read them directly:

```
vf_source_words={value}      ← Phase 1.3
vf_atomic_notes={value}      ← Phase 3.5
vf_core_questions={value}    ← Phase 5.2 (always ≤5)
vf_wikilinks={value}         ← Phase 4.4
```

**Graph View background**:

**Graph View background** (for style A):

Convert the static `scripts/graph-bg.svg` to PNG:

```
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu --no-sandbox \
  --window-size=900,900 \
  --screenshot={temp}/graph-bg.png \
  "file:///{skill dir}/scripts/graph-bg.svg"
```

Encode the PNG as base64. Replace `{{GRAPH_BG}}` in the template with:
`<img class="bg-layer" src="data:image/png;base64,...">`

**Render the card** (randomly pick style A or B):

| Style | Template | Ratio | Look |
|-------|----------|-------|------|
| A | `scripts/share-card.html` | 1:1 (900×900) | Graph view background, 2×2 frosted stat panels |
| B | `scripts/share-card-b.html` | 3:1.8 (540×900) | Portrait, topic → hero image → inline stats → slogan |

Randomly pick one, then follow the path for that style:

**Style A path:**
1. Read `scripts/share-card.html`
2. Replace `{{GRAPH_BG}}` with the graph-bg PNG base64 as `<img class="bg-layer" src="data:image/png;base64,...">`
3. Render with `--window-size=900,900`

**Style B path:**
1. Read `scripts/share-card-b.html`
2. Replace `{{HERO_IMG}}` with the achievement card PNG base64 as `data:image/png;base64,...`
3. Render with `--window-size=540,900`

**Both paths — fill these shared placeholders:**
   - `{{TOPIC}}` — learning topic name
   - `{{NOTES}}` / `{{LINKS}}` / `{{WORDS}}` / `{{QUESTIONS}}` — numeric stats
   - `{{LABEL_NOTES}}` etc. — labels in the user's selected language:
     - English: Source Words / Atomic Notes / Core Questions / Logical Links
     - 中文: XXXX字源文件阅读 / XXX篇笔记生成 / XXX核心问题思考 / XXX思维链接建立
   - `{{WORDS}}` — use k-unit format for both languages (e.g., 12.4k)
   - `{{QR_URL}}` — QR code image URL linking to the GitHub repo:
     `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://github.com/Easonnotsing/VaultForge`
   - `{{SLOGAN}}` — language-aware:
     - English: "Every read builds something that lasts."
           - 中文: "每一次阅读，都不止于阅读。"
4. Write the filled template to a temp `.html` file and render with Chrome headless using the style's window size
5. Report to the user: `📸 Achievement card generated: VaultForge Achievement - {Topic}.png`

> Historical failure cases and improvement records: see [HISTORY.md](./HISTORY.md)

## File Structure

```
skill directory/
├── SKILL.md                         # Main skill file (complete workflow)
├── README.md                        # Installation and product description
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
└── scripts/
    ├── double-link-builder.py       # Wikilink builder (3-stage funnel v2)
    ├── context-extractor.py         # Context pre-extraction (Phase 3.0b)
    ├── roadmap-editor.py            # Optional: browser-based roadmap editor
    ├── share-card.html              # Achievement card template
    └── graph-bg.svg                 # Static graph view background
```

## Flow Overview

```
Phase 0: Vault Scan & Mode Selection (auto-detect incremental vs fresh)
    ↓
Phase 1: Roadmap Generation (or incremental roadmap)
    ↓
Phase 2: File Structure Creation (add-only in incremental mode)
    ↓
Phase 3: Content Generation (parallel, with vf_ frontmatter)
    ↓
Phase 4: Wikilink Building (new-to-new links; new-to-old suggestions)
    ↓
Phase 5: Final Review + Core Question + Update Report + Pristine Refresh (if incremental)
    ↓
Phase 6: Deep Research & Controversy Analysis
```

### Client Differences (Claude Code / Codex / Cursor etc.)

- **Claude Code / Codex**: Typical trigger via slash command (e.g., `/VaultForge`, subject to local command configuration); sub-agents and "skill calling skill" depend on whether the current harness supports them.
- **Cursor**: Usually auto-matched by **Agent Skills** based on description, or the user explicitly requests execution per this SKILL in conversation; if multi-agent orchestration is unavailable, Phase 3 degrades to **sequential grouping** as described above.
- **`scripts/double-link-builder.py` (v2)**: Executes stages 1+2 of the three-stage funnel (structural affinity filtering + TF-IDF + keyword heuristics). `--mode full` (default) outputs `candidates.json` for the main agent's LLM to do stage 3 classification; `--mode strict` (degraded) directly writes deterministic links; `--mode incremental` writes links only between new notes and outputs new→old suggestions (requires `--new-notes` and `--output-suggestions`). The script is conservative by design — relationships not covered by keywords are left unlinked, to be completed by LLM stage 3 or by the user in Obsidian.
- **LLM Stage 3 Dependency**: Phase 4.2b's LLM batch classification requires the main agent to have LLM calling capability. If unsupported (e.g., purely local environment), use the `--mode strict` degraded path.

## Output Quality Standards

| Artifact | Core Requirements | Detailed Specification |
|----------|------------------|----------------------|
| Roadmap | Full version: 200+ words per knowledge point + cases + citations + source_range; Outline: strictly H2/H3/bullets only | See Phase 1.5 |
| Atomic Notes | Core concepts 200+ words + case study 150+ words + original citation + 2-3 reflection questions, no significant duplication | See [agents/atomic-note-filler.md](./agents/atomic-note-filler.md) |
| Wikilinks | Based on 5 logical relationship types (not term similarity), roadmap ↔ MOC bidirectional | See [references/obsidian-structure.md](./references/obsidian-structure.md) |
| Obsidian Format | Frontmatter includes title/date/tags, wikilinks target existing notes, format is consistent | See [references/obsidian-structure.md](./references/obsidian-structure.md) |
| Core Questions | ≤5 questions, each with background + optional sub-questions, guiding and logically structured | See Phase 5.2 + [references/templates.md](./references/templates.md) |
| Controversy Analysis | ≥3-5 valuable reference sources, consensus/controversy/context-dependent sections presented objectively | See Phase 6.3 + [references/templates.md](./references/templates.md) |
