# Output Format Templates

Contains complete format templates for VaultForge skill outputs (non-control-flow artifacts), referenced by Phase 5.2, Phase 5.4 (incremental), and Phase 6.3.

---

## Core Questions Template (Phase 5.2)

Storage location: `{vault}/{learning materials folder}/Core Questions.md`

### English Format

```markdown
---
title: Core Questions
date: YYYY-MM-DD
tags:
  - core-questions
  - {topic}
---

# Core Questions

> Curated from the essence of the learning material. Use ≤5 key questions to guide efficient learning.

## Question 1: {Question Title}

**Background**: {Why this question matters, what it addresses, the context}

{Sub-question 1.1}
{Sub-question 1.2}

---

## Question 2: {Question Title}

**Background**: {...}

---

## Question 3: {Question Title}

**Background**: {...}

---

## Question 4: {Question Title}

**Background**: {...}

---

## Question 5: {Question Title}

**Background**: {...}

---

## Study Tips

Approach the material with these questions in mind. After studying, try answering them to validate your learning.
```

### 中文格式

```markdown
---
title: 核心问题
date: YYYY-MM-DD
tags:
  - 核心问题
  - {主题名}
---

# 核心问题

> 本笔记整理自学习材料的核心精华，通过不超过 5 个关键问题引导高效学习。

## 问题一：{问题标题}

**问题背景**：{解释为什么这个问题重要，要解决什么，背景是什么}

{子问题 1.1}
{子问题 1.2}

---

## 问题二：{问题标题}

**问题背景**：{...}

---

## 学习提示

带着这些问题去学习，当学习完成后，尝试回答这些问题来验证学习效果。
```

### Generation Requirements

- Quantity limit: ≤5 core questions
- Essential: covers the most essential knowledge, principles, and methodologies
- Guiding: questions should guide efficient learning, not simple information retrieval
- Logical: questions should have logical progression; no repetition or contradiction
- Each question includes: title + background + optional sub-questions (2-3)

### Question List Example (Topic: "Platform Strategy")

```
1. What are the core elements of a platform business model? How do platforms differ from traditional pipeline models?
   - Sub: What types of network effects exist? How do they compound?

2. How do platform companies create and capture value? What is the difference between value creation and value capture?
   - Sub: How does platform pricing differ from pipeline pricing?

3. What governance mechanisms exist for platform ecosystems? How to balance platform control with participant autonomy?
   - Sub: How does pricing structure in two-sided markets affect platform success?
```

---

## Controversy Analysis Template (Phase 6.3)

Storage location: `{vault}/{learning materials folder}/{Topic} - Controversy Analysis.md`

### English Format

```markdown
---
title: {Topic} - Controversy Analysis
date: YYYY-MM-DD
tags:
  - controversy-analysis
  - {topic}
---

# {Topic} - Controversy Analysis

> Through deep research, this note identifies industry consensus and controversies within the learning material. It helps learners understand the boundaries of the field and provides direction for in-depth discussions with experts.

## Summary

{Briefly describe the landscape of this field: what the mainstream view is, what major controversies exist, and where the points of divergence lie. 200-300 words.}

---

## Undisputed (Industry Consensus)

{List content from the learning material that is widely accepted and rarely questioned.}

### Consensus 1: {Title}

- **Content**: {Specific consensus content}
- **Why Undisputed**: {Explain why this view is uncontroversial}
- **Supporting Evidence**: {Evidence from deep research}

### Consensus 2: {...}

---

## Controversial (Different Views)

{List controversies, divergences, or differing viewpoints present in the learning material.}

### Controversy 1: {Title}

- **Learning Material View**: {The view in the learning material}
- **Opposing View**: {Opposing or differing views found through deep research}
- **Core of Controversy**: {What the controversy is about, the root of the divergence}
- **Arguments**:
  - Pro: {Arguments supporting the learning material's view}
  - Con: {Arguments opposing or questioning it}
- **Reference**: {Relevant source link}

### Controversy 2: {...}

---

## Context-Dependent (No Universal Answer)

{List methods, strategies, or views mentioned in the learning material whose applicability depends on specific context, with no universally correct answer.}

### Context-Dependency 1: {Title}

- **Learning Material Description**: {The view or suggestion in the learning material}
- **Applicable Context A**: {When this view holds true}
- **Applicable Context B**: {When it may not apply or needs adjustment}
- **Key Variables**: {Core variables determining which context applies}

### Context-Dependency 2: {...}

---

## Deep Discussion Questions for Experts

{Based on the controversy analysis and different perspectives, compile deep, valuable discussion questions to help learners engage in meaningful dialogue with domain experts.}

### Deeper Questions on Consensus

1. {Question} — {Why this question is valuable to explore}

### Clarifying Questions on Controversies

1. {Question} — {Why this question matters, background of the controversy}

### Exploratory Questions on Practice

1. {Question} — {Confusions encountered in real-world application}

---

## Key Conclusions

{Based on the deep research, compile the most important conclusions.}

1. **{Conclusion Title}**: {Specific conclusion}
2. **{Conclusion Title}**: {...}
3. **{Conclusion Title}**: {...}

---

## Reference Sources

{Ranked by relevance and value, list the most valuable reference sources discovered through deep research.}

1. [{Source Title}](URL) — {Why this source is valuable, brief evaluation}
2. [{Source Title}](URL) — {...}
3. [{Source Title}](URL) — {...}
4. [{Source Title}](URL) — {...}
5. [{Source Title}](URL) — {...}

---

## Study Suggestions

- For **Industry Consensus**: can serve as a foundational framework, but still validate through practice
- For **Controversial Content**: maintain an open mind, understand the reasonableness of all perspectives, think critically
- For **Context-Dependent**: focus on understanding the underlying principles, apply flexibly based on actual context
- When **discussing with experts**, select the most relevant questions from the "Discussion Questions" list
```

### Content Filling Guide

| Section | Filling Principle |
|---------|-------------------|
| Summary | 200-300 words, outline the field's basic landscape, mainstream views, major controversies |
| Undisputed | Find views consistently recognized across multiple sources; explain why widely accepted; cite authoritative sources |
| Controversial | Identify divergence points between the learning material and other sources; objectively present all views; point out the controversy's core |
| Context-Dependent | Identify methodology-level suggestions; explain applicability differences across contexts; identify key determining variables |
| Question List | Questions should be open-ended and deep; avoid yes/no; choose core topics frequently discussed by experts |
| Reference Sources | Rank 5-10 most valuable reference sources by relevance and value; include brief evaluations |

### Principles

**For Undisputed**:
- Find views consistently recognized across multiple sources
- Explain why these views are widely accepted
- Cite authoritative sources as support

**For Controversial**:
- Identify divergence points between the learning material and other sources
- Objectively present all views without bias
- Point out the controversy's core and roots

**For Context-Dependent**:
- Identify methodology-level suggestions
- Explain applicability differences across different contexts
- Identify key determining variables

**For Question Lists**:
- Questions should be open-ended and deep
- Avoid yes/no type questions
- Prioritize core topics frequently discussed by experts

---

## Update Report Template (Phase 5.4 — Incremental Mode Only)

Storage location: `{vault}/{learning materials folder}/VaultForge Update Report - {date}.md`

### English Format

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
- {XX. Category Name/}
- ...

**New notes in existing folders**:
- {path/to/note.md}
- ...

## Wikilinks Established

| Scope | Count |
|-------|-------|
| New ↔ New | {N} |
| New → Existing (suggested) | {N} |

**Suggested new-to-existing links** (review and add manually if desired):
- [[{new note}]] → [[{existing note}]] ({relationship type})
- ...

## Notes Eligible for Refresh (pristine only)

These notes were originally generated by VaultForge and have not been user-edited. New source content is available.

- [ ] {note.md} — {N} new source pages available
- [ ] {note.md} — {N} new source pages available

Reply "refresh 1,2" to regenerate selected notes, or "skip" to ignore.

## Protected Notes (not modified)

| Status | Count |
|--------|-------|
| User-modified (preserved as-is) | {N} |
| Locked (untouched) | {N} |

## Update Session

- Previous roadmap: Learning Roadmap v1 - {Topic}.md
- New roadmap: Learning Roadmap v2 - {Topic}.md
- `vf_session` on new notes: incremental-{date}
```

### Content Filling Guide

| Section | Data Source |
|---------|-------------|
| New Files Created | Aggregated from Phase 2 creation log |
| Wikilinks Established | Aggregated from Phase 4 output + new_to_old_suggestions.json |
| Notes Eligible for Refresh | Detected by comparing new source pages against pristine notes' `source_range` |
| Protected Notes | Counted from Phase 0 vault scan (user_modified + locked statuses) |
