# Compatibility

This skill is designed to be portable across agent clients. Each client has different support for subagents, file access, and research tools. `SKILL.md` is the source of truth — use the notes below as an execution guide.

## Common Setup

1. Clone the repository to your skills directory
2. Install PDF dependency: `pip install pypdf`
3. Trigger the skill in your client (see below)
4. For Phase 6 deep research: install `firecrawl-mcp` and/or `exa-mcp` MCP servers, configure API keys in the client's MCP settings. **Start a new session** after enabling MCP — tools are only injected on session creation, not resume.

## OpenCode / Claude Code / Codex

- Use the full repository as a skill directory.
- Subagent files in `agents/` are platform-neutral task specs; the harness maps them to its own agent/task system.
- If parallel subagents are unavailable or timeout after 5 minutes, Phase 3 falls back to sequential execution in batches of ≤ 10 notes.
- MCP servers (Firecrawl, Exa) are configured in `~/.config/opencode/opencode.json` — see README for examples.

## Cursor

- Place the whole repository in the Agent Skills location, or reference `SKILL.md` explicitly.
- Cursor may not honor `agents/` as executable subagents → treat each agent file as a prompt/spec and execute in the main agent.
- Use the default conversational folder/file selection flow.

## Other Clients

- Any client that supports loading a skill directory should work.
- Reference `SKILL.md` explicitly in the conversation if auto-detection fails.
- The core flow requires no browser; all scripts are CLI-based.

## Scripts

| Script | Purpose | Dependencies |
|--------|---------|-------------|
| `context-extractor.py` | Extract source text per knowledge point (Phase 3.0b) | Python 3, pypdf (recommended for PDF) |
| `double-link-builder.py` | Three-stage funnel: structural → TF-IDF → candidate generation (Phase 4) | Python 3 |

### double-link-builder.py Modes

```bash
# Default: generate candidates.json for main agent LLM review (stage 3)
python3 scripts/double-link-builder.py <learning_folder> <roadmap_name> --output candidates.json

# Strict: deterministic links only (no LLM needed, ~40-50% coverage)
python3 scripts/double-link-builder.py <learning_folder> <roadmap_name> --mode strict

# Incremental: links between new notes only, suggestions for new→old
python3 scripts/double-link-builder.py <learning_folder> <roadmap_name> --mode incremental --new-notes new.json --output-suggestions suggestions.json
```

### context-extractor.py Usage

```bash
# Extract source excerpts based on roadmap source_range annotations
python3 scripts/context-extractor.py <vault_path> <roadmap_path> -o context_packets.json

# Filter to specific notes (for incremental refresh)
python3 scripts/context-extractor.py <vault_path> <roadmap_path> -o packets.json --note-filter note1.md,note2.md
```

## Testing

```bash
pip install pytest
python3 -m pytest tests/
```
