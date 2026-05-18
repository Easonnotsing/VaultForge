# Compatibility

This skill is designed to be portable across agent clients. Each client has different support for subagents, file access, and research tools. `SKILL.md` is the source of truth — use the notes below as an execution guide.

## Common Setup

1. Clone the repository to your skills directory
2. Install optional PDF dependency: `pip install pypdf` (or `PyPDF2`)
3. Trigger the skill in your client (see below)

## Claude Code / Codex

- Use the full repository as a skill directory.
- Subagent files in `agents/` are platform-neutral task specs; the harness maps them to its own agent/task system.
- If parallel subagents are unavailable, run Phase 3 sequentially in batches of ≤ 5 notes.
- The optional `roadmap-editor.py` requires Playwright: `pip install playwright && playwright install chromium`.

## Cursor

- Place the whole repository in the Agent Skills location, or reference `SKILL.md` explicitly.
- Cursor may not honor `agents/` as executable subagents → treat each agent file as a prompt/spec and execute in the main agent.
- Use the default conversational folder/file selection flow (no browser automation needed).

## Other Clients

- Any client that supports loading a skill directory should work.
- Reference `SKILL.md` explicitly in the conversation if auto-detection fails.
- The core flow requires no browser; all scripts are CLI-based.

## Scripts

| Script | Purpose | Dependencies |
|--------|---------|-------------|
| `context-extractor.py` | Extract source text per knowledge point (Phase 3.0b) | Python 3, pypdf (optional, for PDF) |
| `double-link-builder.py` | Three-stage funnel: structural → TF-IDF → candidate generation (Phase 4) | Python 3 |
| `roadmap-editor.py` | Optional browser-based roadmap editor | Python 3, Playwright |

### double-link-builder.py Modes

```bash
# Default: generate candidates.json for main agent LLM review (stage 3)
python3 scripts/double-link-builder.py <vault_path> <roadmap_name> --output candidates.json

# Strict: deterministic links only (no LLM needed, ~40-50% coverage)
python3 scripts/double-link-builder.py <vault_path> <roadmap_name> --mode strict

# Adjust thresholds
python3 scripts/double-link-builder.py <vault_path> <roadmap_name> --output c.json --tfidf-threshold 0.2
```

### context-extractor.py Usage

```bash
# Extract source excerpts based on roadmap source_range annotations
python3 scripts/context-extractor.py <vault_path> <roadmap_path> -o context_packets.json

# Adjust page buffer (±N pages)
python3 scripts/context-extractor.py <vault_path> <roadmap_path> -o packets.json --buffer 2
```

## Testing

```bash
python3 -m unittest discover -s tests
```
