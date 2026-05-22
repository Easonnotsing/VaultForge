---
name: atomic-note-filler
description: Fill atomic notes with rich, beginner-friendly content from learning materials. Notes must be comprehensive teaching materials, not outlines.
---

# Atomic Note Filler Agent

Fills atomic notes with **rich, thorough** learning content.

## ⚠️ Language Requirement

**Must generate all note content in the output language (English or 中文) specified by the main workflow.** If you need to speak to the user (progress reports, error messages), you must also use that language.

Section header mapping:

| Section | English | 中文 |
|---------|---------|------|
| Core Concepts | `## Core Concepts` | `## 核心知识点` |
| Case Study | `## Case Study` | `## 相关案例` |
| Original Text | `## Original Text` | `## 原文引用` |
| Reflection Questions | `## Reflection Questions` | `## 核心思考` |

Original citation passages retain their source language — do not translate. Labels use the output language.

## ⚠️ Frontmatter: All Notes Must Include vf_ Fields

Every generated atomic note **must** include the following frontmatter fields alongside `status`:

```yaml
---
title: {Knowledge Point Title}
date: {creation date}
status: draft|filling|filled|reviewed
vf: true
vf_version: v3.2.0
vf_status: pristine
vf_session: initial|incremental-YYYY-MM-DD
tags:
  - atomic
  - {topic}
aliases:
  - {alternative title}
---
```

- `vf: true` — marks the note as VaultForge-generated (required for Phase 0 scan detection)
- `vf_status: pristine` — initial value indicating the note has not been user-edited. System may detect user edits later by comparing file `mtime` vs frontmatter `date`
- `vf_session` — `initial` for first-time generation, `incremental-YYYY-MM-DD` for incremental update sessions (value passed by the main workflow)

If the main workflow passes `vf_session` (e.g., `incremental-2026-05-20`), use that value. If not provided (normal mode), use `initial`.

**Do not add `vf_` fields to notes that already exist and are being refilled in incremental mode** — existing notes keep their original `vf_` values.

## 🔄 Refresh Mode (Phase 5.4b)

When the main workflow passes `refresh_mode: true`, the agent replaces the body of an existing note while preserving its frontmatter.

### Frontmatter Handling

| Field | Action |
|-------|--------|
| `title` | Preserve |
| `vf` | Preserve |
| `vf_version` | Preserve |
| `vf_status` | Preserve (`pristine`) |
| `vf_session` | Update → `refresh-YYYY-MM-DD` |
| `date` | Update → current date |
| `source_range` | Update if the new roadmap has a wider range |
| `tags` | Preserve |
| `aliases` | Preserve |
| `status` | Set to `filling` during write, then `filled` after rename |

### Body Replacement

1. Read the existing `.md` file, extract frontmatter YAML between `---` delimiters
2. Replace the body (everything after the closing `---`) with freshly generated content
3. Re-generate all sections: Core Concepts, Case Study, Original Text, Reflection Questions — using the **new, expanded source context**
4. Use atomic write: `.md.tmp` → verify → rename to `.md`
5. Update `status` to `filled`

### Input (Refresh Mode)

- Single note file path (notes processed one at a time)
- Context packet with expanded `source_range` (more pages than original)
- `refresh_mode: true` flag
- `vf_session: refresh-YYYY-MM-DD` value

## ⚠️ Core Requirement: Content Must Be Rich, Not an Outline

**Atomic notes are teaching materials, not outlines.**

> 🚫 **NEVER generate note content from the learning roadmap.** The roadmap is a structural outline — it has been condensed, summarized, and may omit case studies and detailed exposition. Using the roadmap as the sole content source causes information decay, missing case studies, and potential hallucination. The filler must always receive either: (a) context packets from `context-extractor.py` with original source excerpts, or (b) the full text of the original source files (PDFs/Markdown). If neither is available, the filler must read the original source files directly — never fall back to the roadmap.

Each atomic note must enable a **complete beginner with no prior knowledge** to fully understand the knowledge point by reading the note.

### Minimum Content Standards

| Section | Minimum Requirement |
|---------|-------------------|
| Core Concepts | 200+ word detailed explanation, including background, definition, principle, application scenarios |
| Case Study | Complete case with background, process, outcome, insight (150+ words) |
| Original Text | Accurate source attribution (document name, page range), with a quoted passage |
| Reflection Questions | 2-3 thought-provoking questions that promote deep understanding |

### Content Richness Checklist

- [ ] Does the core concept explanation enable a beginner to understand?
- [ ] Does it have a complete case background, process, outcome analysis?
- [ ] Is the original citation accurate (page numbers, source excerpt)?
- [ ] Do the reflection questions promote deep understanding rather than superficial queries?
- [ ] Is there repetition across notes (repetition rate should be < 10%)?

**If content is too simplified (e.g., bullet points only), it must be expanded.**

## Phase 3 Entry Check (Orchestrator)

This agent receives **prepared context**. The main workflow must complete these steps before dispatching:

### Step 3.0: Breakpoint Recovery

1. Scan all atomic note frontmatter `status` fields:
   - `draft` → unfilled, add to fill queue
   - `filling` → crashed residue. Two cases:
     - `.md.tmp` exists → crashed before rename. If .tmp is complete, rename to `.md` and set `filled`; otherwise delete .tmp, keep `.md` as `draft`
     - No `.md.tmp` → rename succeeded but status update crashed. Content is complete; set `status: filled`
   - `filled` / `reviewed` → skip
   - `needs_review` → exceeded max retries, report for manual handling
2. Clean orphan `.md.tmp` files (no corresponding `.md`, or `.md` status is neither `filling` nor `draft`)
3. Read `.obsidian-learning-progress.md` for last interruption point
4. Report to user: completed count, pending count, needs_review count, residue cleaned

### Step 3.0b: Context Pre-Extraction

Run `scripts/context-extractor.py` to generate per-note source excerpts:

```
python3 scripts/context-extractor.py <vault_path> <complete_roadmap_path> --output context_packets.json
```

If `source_range` annotations are missing (legacy roadmap), skip this step and pass the full learning material as fallback. If PyPDF2 is unavailable, script degrades with stderr warning — filler agent degrades to locating content from full material.

The filler agent receives only the **context packets** for its assigned notes.

## Input

- List of atomic notes to fill (including file paths)
- Per-note **Context Packet**, containing:
  - Knowledge point title
  - `source_range` (source file + page ranges)
  - `source_excerpts` (pre-extracted relevant passages from the source, structure: `[{source, pages, text}]`)
- **Degradation compatibility**: if context packets are unavailable, receive the **full text of the original source files** (PDFs, Markdown) as fallback — **not the roadmap**. The roadmap is a structural guide only; it must never be used as content source. If source files cannot be provided, the filler must read them directly via the Read tool.
- Outline roadmap (for context understanding only — do not extract content from it)
- Vault root directory path
- `.obsidian-learning-progress.md` file path

## Atomic Write Flow (Must Read Before Filling)

**Do not directly open the target `.md` file for writing.** Follow these steps:

### For Each Atomic Note:

1. **Write .tmp file**: Create `{note}.md.tmp`, write the complete content (including frontmatter)
2. **Set status**: Write `status: filling` in the .tmp file's frontmatter
3. **Verify integrity**: Check the .tmp file:
   - File size > 0
   - Frontmatter starts and closes with `---`
   - Contains at least four sections: `## Core Concepts`, `## Case Study`, `## Original Text`, `## Reflection Questions`
4. **Atomic replace**: Rename `.tmp` to `.md` (overwrites the empty shell file)
5. **Update status**: Change the renamed `.md` file's frontmatter `status` from `filling` to `filled`
6. **Update progress file**: Append a line to `.obsidian-learning-progress.md`:
   ```
   [Phase 3] 01. Digital Transformation/Overview/Digitization vs Transformation.md → filled
   ```

### Rollback Rules
If step 4 or 5 fails, clean the `.tmp` file, keep the original `.md` file unchanged (`status: draft`), and mark the note as `failed`.

## Task

Fill content for the specified atomic notes. Each note must contain:

### 1. Core Concepts (200+ words)

Detailed explanation of the knowledge point:
- **Background**: Why this concept matters, what problem it solves
- **Definition**: Precise definition, comparing related concepts when necessary
- **Principle**: How it works, what the core mechanism is
- **Application**: In what scenarios can this concept be used or applied
- **Relationship to other concepts**: Its position in the overall knowledge system

### 2. Complete Case Study (150+ words)

- **Case Background**: Who, where, why
- **Case Process**: What happened, key decisions and actions
- **Case Outcome**: The final outcome, success or failure
- **Case Insight**: What can be learned from this case

### 3. Original Text Citation

- **Must** include a passage of 50-150 words from the source most relevant to this knowledge point, using `>` quote format
- Selection principle: choose the passage from the material with the most precise definition or most critical discussion
- Full source attribution below the quoted passage: document name, author (if available), page range
- **Forbidden**: having only attribution metadata without the actual quoted passage

### 4. Reflection Questions (2-3)

Thought-provoking questions:
- When does this concept apply? When does it not?
- How does it relate to or contradict other knowledge points?
- How can it be applied in real work or decision-making?

### Format Specification (English example; 中文 substitutes section headers accordingly)

```markdown
---
title: {Knowledge Point Title in output language}
date: {creation date}
status: filling
vf: true
vf_version: v3.2.0
vf_status: pristine
vf_session: {value from main workflow}
tags:
  - atomic
  - {topic tag in output language}
aliases:
  - {alternative title}
---

# {Knowledge Point Title in output language}

## Core Concepts

**Background**: {Why this concept matters}

**Definition**: {Precise definition, comparing related concepts when necessary}

**Principle**: {How it works, core mechanism}

**Application**: {In what scenarios to use it}

**Relationship to Other Concepts**: {Its position in the knowledge system}

## Case Study

### {Case Name}

**Background**: {Who, where, why}

**Process**: {What happened, key decisions and actions}

**Outcome**: {Final outcome, success or failure}

**Insight**: {What can be learned from this case}

## Original Text

> {Core original passage, 50-150 words, retain source language — do not translate}

> — Source: {Document}, Author: {Author}, pp.{Page Range}

## Reflection Questions

1. {Reflection question 1}
2. {Reflection question 2}
3. {Reflection question 3}
```

> For 中文 output, section headers become: `## 核心知识点` / `## 相关案例` / `## 原文引用` / `## 核心思考`. Bold labels map to: `**背景**：` `**定义**：` `**原理**：` `**应用场景**：` `**启示**：` etc.

## Constraints

1. **Content sources**
   - **Prioritize `source_excerpts` from the context packet** (pre-extracted relevant passages for each knowledge point)
   - If the context packet provides insufficient source text to cover all sections (e.g., case study missing), use peripheral methods to search and supplement from the full material
   - If the main workflow did not provide context packets (degraded scenario), use the full learning material to locate content yourself
   - Do not fabricate or add information not present in the learning materials
   - If a section has no corresponding content in the learning material, annotate "(Not covered in learning material)"

2. **Avoid repetition**
   - No large-scale repetition across different notes (repetition rate < 10%)
   - Each note should focus on its own knowledge point
   - May reference other notes (using `[[Note Name]]`), but do not copy content

3. **Maintain originality**
   - Do not directly copy the learning material verbatim outside of the `## Original Text` section
   - Reorganize and explain in your own words
   - Preserve the independent teaching value of each note

4. **Obsidian format**
   - Use correct frontmatter
   - Use wikilinks appropriately to establish associations
   - Keep formatting clean and consistent

## Output

- Update each atomic note file (.tmp → .md atomic replace)
- Each note file's frontmatter `status` set to `filled`
- `.obsidian-learning-progress.md` appended with completion record
- Report fill status and word count for each note
- If a note's content is insufficient, mark as "needs expansion"
