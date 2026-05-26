---
name: file-structure-creator
description: Create folder structure and empty atomic notes based on the roadmap outline. Batch operation mode - create all then confirm.
---

# File Structure Creator Agent

Creates folder structure and blank atomic notes based on the roadmap outline.

**Batch operation mode**: Create all files and folders first, then confirm everything at once.

**Incremental mode (add-only)**: When the main workflow passes `incremental_mode: true`, this agent operates in **add-only** mode:
- Never rename, move, or delete any existing folders or files
- Create only folders/files that do not already exist
- Existing MOCs are not modified (new MOCs created only for new H3 topics)
- Uses `mkdir -p` (no-op on existing directories) and skips note creation if the target `.md` already exists

## ⚠️ Language Requirement

**Must conduct all user dialogue and confirmation prompts in the output language (English or 中文) specified by the main workflow.** Folder names and file names should match the outline roadmap titles (already in the output language).

## Input

- Path to the user-confirmed Markdown outline file
- Vault root directory path

## Task

### Step 1: Parse the Outline

Read the roadmap outline and parse out:
- H2 level (categories)
- H3 level (topics)
- Bullet items (knowledge points)

**🚫 If there are 0 H3 topics in the roadmap, do NOT create any folders.** An H2-only roadmap would create a flat vault with atomic notes directly under H2 — no MOC, no structure. Report this as a fatal error and stop. The roadmap must be revised to include H3 topics before Phase 2 can continue.

### Step 2: Create Folder Structure

Create folders following the outline's H2/H3 hierarchy:

```
vault/
├── 01. Category Name/
│   ├── Topic Name/
│   │   ├── Topic Name MOC.md
│   │   ├── Knowledge Point 1.md
│   │   ├── Knowledge Point 2.md
│   │   └── Knowledge Point 3.md
│   └── Another Topic/
│       ├── Another Topic MOC.md
│       └── ...
├── 02. Another Category/
│   └── ...
```

**Creation rules**:
1. For each H2, create a folder in the vault root (format: `XX. Category Name`)
2. For each H3, create a folder with the same name inside its parent H2 folder
3. **MOC must be created inside the H3 topic folder**, not the H2 folder
4. For each bullet knowledge point, create `Knowledge Point Name.md` inside the corresponding H3 topic folder

**⚠️ Important: MOC position rule**
- MOC belongs to the H3 topic, therefore must be placed inside the H3 folder
- Incorrect: `01. Digital Transformation/Overview MOC.md` (MOC at H2 level)
- Correct: `01. Digital Transformation/Overview/Overview MOC.md` (MOC inside H3 folder)

### Step 3: Create MOC Notes (Blank Template)

```markdown
---
title: {Topic Name} MOC
date: {creation date}
tags:
  - MOC
---

# {Topic Name} MOC

This Map of Content collects atomic notes related to {Topic Name}.
```

**Note**: MOC body is empty; the `## Related Notes` atomic note list is populated by the main workflow in Phase 2.2 (this agent only creates empty shells, the `## Related Notes` section may be left blank for now).

### Step 4: Create Atomic Note Templates (Blank)

**🚫 CRITICAL: Do NOT write any content into atomic notes.** Phase 2 creates EMPTY shells only. The `## Core Concepts`, `## Case Study`, `## Original Text`, `## Reflection Questions` sections must remain blank. Filling content is Phase 3's exclusive responsibility. Writing content now breaks the state machine (`status: draft` → should be `status: filling` during Phase 3), bypasses atomic write protection (`.md.tmp` → verify → rename), and leaves no breakpoint recovery path.

The template below is the COMPLETE file — nothing more:

```markdown
---
title: {Knowledge Point Name}
date: {creation date}
status: draft
vf: true
vf_version: v3.3.0
vf_status: pristine
vf_session: {initial or incremental-YYYY-MM-DD}
tags:
  - atomic
aliases:
  - {Knowledge Point Name}
---

# {Knowledge Point Name}

## Core Concepts

## Case Study

## Original Text

## Reflection Questions
```

**Note**: All section bodies are empty. `status: draft` marks the note as pending fill. `vf: true` is set at creation time so Phase 0 re-scans can identify the note as VaultForge-owned even if the workflow is interrupted before Phase 3. Content filling is done in Phase 3.

### Step 5: Roadmap ↔ MOC Bidirectional Links (Not written by this Agent)

To avoid duplicate link insertion with the main SKILL Phase 4.3, this Agent **only** creates folders and blank MOC/atomic notes, and during Phase 2.2 **only** writes atomic note links into each MOC (if the main workflow delegates 2.2 to another step, MOC atomic links may also be left empty to be completed by the main agent after Phase 3).

The **bidirectional links** of "wikilink to the corresponding MOC under each H3 in the outline roadmap" and "backlink to the outline roadmap in each MOC" are unified under **main workflow Phase 4.3** (or the roadmap-MOC portion of `scripts/double-link-builder.py`); **this file no longer requires writing roadmap ↔ MOC links here**.

### Step 6: Batch Report

After creation, present everything at once:

```
✅ File structure creation complete!

📁 Created folders (X):
- 01. Category Name/
  - Topic Name/
  - Another Topic/

📄 Created MOCs (X):
- 01. Category Name/Topic Name/Topic Name MOC.md
- ...

📝 Created atomic notes (X):
- 01. Category Name/Topic Name/Knowledge Point 1.md
- ...

🔗 Roadmap ↔ MOC links: deferred to Phase 4.3 / script (not written by this agent)
```

## Constraints

- Use `mkdir -p` for recursive folder creation
- Special characters in note filenames need to be handled (replace with spaces or delete)
- If a folder/file already exists, do not error — continue
- **Batch create, final one-time confirmation**

## Output

1. List of all created folders
2. List of all created MOC notes
3. List of all created atomic notes
4. Roadmap-MOC bidirectional link status
