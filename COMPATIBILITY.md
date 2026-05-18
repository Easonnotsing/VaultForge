# Compatibility

This skill is designed to be portable across agent clients, but each client has
different support for subagents, file access, browser automation, and research
tools. Treat `SKILL.md` as the source of truth and use the notes below as an
execution guide.

## Claude Code

- Can use this repository as a skill directory.
- Subagent files in `agents/` are written as generic task specs; the current
  harness may map them to its own agent/task system.
- If true parallel subagents are unavailable, run Phase 3 sequentially in
  batches of no more than 5 atomic notes.
- Optional browser scripts require Playwright to be installed beforehand.

## Cursor

- Place the whole repository in the Agent Skills location or reference
  `SKILL.md` explicitly in the conversation/rules.
- Cursor may not honor `agents/` as executable subagents. In that case, treat
  each agent file as a prompt/spec and execute the work in the main agent.
- Use the default conversational folder/file selection flow if local browser
  automation is unavailable.

## Codex

- Use the full repository as the working skill package.
- The subagent markdown files are platform-neutral task instructions; they do
  not require Claude-specific `model` or `tools` fields.
- Prefer normal filesystem edits and local scripts for deterministic steps.
- `scripts/double-link-builder.py` defaults to candidate generation; the main
  agent should review `link-candidates.md` before applying links.

## Optional Scripts

- `scripts/run-picker.py`: optional local browser picker for vault folders.
- `scripts/roadmap-editor.py`: optional local browser editor; writes back the
  roadmap file and creates a `.bak` backup after saving.
- `scripts/double-link-builder.py`: generates `link-candidates.md` by default;
  use `--apply` only after main-agent review.

Install optional browser dependencies only if you plan to use picker/editor:

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
```

The scripts do not auto-install dependencies. This keeps behavior predictable
in restricted or offline agent environments.
