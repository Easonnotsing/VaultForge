# Obsidian Note Structure Specification

Defines the standardized structure for the Obsidian knowledge base used in the learning material processing workflow.

## Directory Structure

```
vault/
├── 01. Category Name/                     # H2 corresponding folder (numbered + category name)
│   ├── Topic Name/                        # H3 corresponding folder (topic name)
│   │   ├── Topic Name MOC.md              # MOC note
│   │   ├── Knowledge Point 1.md           # Atomic note
│   │   ├── Knowledge Point 2.md
│   │   └── Knowledge Point 3.md
│   └── Another Topic/
│       ├── Another Topic MOC.md
│       └── ...
├── 02. Another Category/
│   └── ...
├── Learning Roadmap (Full) - Topic Name.md  # Full version roadmap
└── Learning Roadmap - Topic Name.md          # Outline version roadmap
```

## Naming Conventions

### Folder Naming

- H2 folder: `XX. Category Name` (number + period + space + category name)
- H3 folder: `Topic Name` (matches the H3 title)
- No special characters (`/`, `\`, `*`, `?`, `"`, `<`, `>`, `|`)

### File Naming

- MOC note: `Topic Name MOC.md`
- Atomic note: `Knowledge Point Name.md`
- Full version roadmap: `Learning Roadmap (Full) - Topic Name.md`
- Outline roadmap: `Learning Roadmap - Topic Name.md`

## Frontmatter Specification

### MOC Note

```yaml
---
title: Topic Name MOC
date: 2024-01-15
tags:
  - MOC
---
```

### Atomic Note

```yaml
---
title: Knowledge Point Name
date: 2024-01-15
status: draft
tags:
  - digital-transformation
aliases:
  - Knowledge Point Name
  - Alternative Name
---
```

**`status` field description**:

| Value | Meaning | Set By |
|-------|---------|--------|
| `draft` | Empty shell file, content pending | Phase 2 file structure creation |
| `filling` | Currently being filled (.tmp file written) | Phase 3 filling agent (when writing .tmp) |
| `filled` | Content filled completely (.tmp → .md rename complete) | Phase 3 filling agent (on rename, status update) |
| `reviewed` | Passed quality review | Phase 3 review agent |
| `needs_review` | Exceeded max retries, needs manual review | Phase 3 main workflow |

## Wikilink Specification

### Wikilink Standard (Important)

Wikilinks must be based on **logical relevance**, not pure term similarity.

| Relationship Type | Definition | Example |
|-------------------|------------|---------|
| Derivation | One note's conclusion is derived from another | "Network Effects" → "Platform Business Model" |
| Analogy | The principles of two notes can be analogized | "Refrigeration Principle" → "Air Conditioning Principle" |
| Contradiction | Two notes' conclusions contradict, requiring debate | "Incremental Innovation" vs "Disruptive Innovation" |
| Application | One note's application involves another's concept | "Data Analysis" applies concepts from "Data Collection" |
| Context | Two notes belong to different aspects or stages of the same domain | "Agile Development" and "Traditional Development" |

**Forbidden: establishing wikilinks based purely on term similarity.**

### MOC and Atomic Notes

Use an unordered list in the MOC note to link atomic notes:

```markdown
## Related Notes

- [[Topic Name/Knowledge Point 1]]
- [[Topic Name/Knowledge Point 2]]
```

### Roadmap and MOC Bidirectional Links

**In the outline roadmap**:

```markdown
## 02. Topic Name

[[02. Topic Name/Topic Name MOC|Topic Name]]

- Knowledge Point 1
- Knowledge Point 2
```

**In the MOC**:

```markdown
## Related Notes

- [[../../Learning Roadmap - Digital Transformation Roadmap|Learning Roadmap]]
```

### Inter-Note Atomic Note Links

Add a `## Related Notes` section at the end of the relevant note:

```markdown
## Related Notes

- [[Derivation Note]]
- [[Analogy Note]]
- [[Contradiction Note]]
```

## Atomic Note Content Structure

Each atomic note must contain the following four sections, with thorough content:

```markdown
---
title: Knowledge Point Name
date: 2024-01-15
status: filled
tags:
  - digital-transformation
aliases:
  - Knowledge Point Name
---

# Knowledge Point Name

## Core Concepts

**Background**: {Why this concept matters}

**Definition**: {Precise definition, comparing related concepts when necessary}

**Principle**: {How it works, core mechanism}

**Application**: {In what scenarios to use it}

**Relationship to Other Concepts**: {Its position in the overall knowledge system}

## Case Study

### {Case Name}

**Background**: {Who, where, why}

**Process**: {What happened, key decisions and actions}

**Outcome**: {Final outcome, success or failure}

**Insight**: {What can be learned from this case}

## Original Text

> {Core original passage, 50-150 words, retain source language}

> — Source: {Document}, Author: {Author}, pp.{Page Range}

## Reflection Questions

1. {Deep reflection question 1}
2. {Reflection question 2}
3. {Reflection question 3}
```

## Knowledge Point Division Principles

1. **Atomicity**: Each knowledge point should be independent and indivisible
2. **Relevance**: Knowledge points under the same topic should be interrelated
3. **Comprehensibility**: Each knowledge point should enable a beginner to understand it by reading the note
4. **Clear citation**: Knowledge points should have clear source citations
5. **Rich content**: Not an outline — thorough teaching material

## MOC Purpose

MOC (Map of Content) serves as a topic index:
- Aggregates all atomic notes under that topic
- Provides a topic-level overview
- Facilitates navigation and relationship discovery
- Reflects the hierarchical structure of knowledge points
- **Establishes bidirectional links with the roadmap**
