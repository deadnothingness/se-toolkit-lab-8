# Task 1 — Implementation Plan

## Overview

This task sets up the nanobot agent framework and connects it to the LMS backend via MCP tools.

## Architecture Decision

**Pattern: Framework-based Agent Configuration**

Instead of writing a custom LLM tool-calling loop (like in Lab 7), we use nanobot as a framework. This is called **separation of concerns** — the framework handles the agent loop, while we configure:
- LLM provider (Qwen Code API)
- MCP tools (LMS backend operations)
- Skills (natural language strategy guidance)

## Deliverables

### Part A — Bare Agent ✅

- [x] Created `nanobot/` project with `uv init`
- [x] Installed `nanobot-ai` from PyPI
- [x] Created `config.json` with custom Qwen Code API provider:
  - Base URL: `http://localhost:42005/v1`
  - API key: from `.env.docker.secret`
  - Model: `coder-model`
- [x] Created `workspace/` directory structure
- [x] Verified agent responds to general questions
- [x] Verified agent has no LMS knowledge without tools (hallucinates from workspace)

### Part B — Agent with LMS Tools ✅

- [x] Added `lms-mcp` as editable dependency from `../mcp`
- [x] Configured MCP server in `config.json`:
  - Command: `uv run python -m mcp_lms`
  - Environment: `NANOBOT_LMS_BACKEND_URL`, `NANOBOT_LMS_API_KEY`
- [x] Verified agent returns real lab names from backend
- [x] Verified agent can answer complex questions (LMS architecture)

### Part C — Skill Prompt ✅

- [x] Created `workspace/skills/lms/SKILL.md` with:
  - Available tools table
  - Tool usage strategy
  - Response formatting guidelines
  - Handling missing lab parameters
- [x] Updated `workspace/USER.md` with skill instructions
- [x] Verified agent behavior improved (lists all labs when "scores" requested without lab)

## Files Created/Modified

| File | Purpose |
|------|---------|
| `nanobot/config.json` | Agent configuration (LLM provider, MCP servers) |
| `nanobot/workspace/` | Agent workspace directory |
| `nanobot/workspace/AGENTS.md` | Agent metadata (auto-generated) |
| `nanobot/workspace/SOUL.md` | Agent personality (auto-generated) |
| `nanobot/workspace/USER.md` | User profile + skill instructions |
| `nanobot/workspace/TOOLS.md` | Tool documentation (auto-generated) |
| `nanobot/workspace/skills/lms/SKILL.md` | LMS skill prompt |
| `nanobot/pyproject.toml` | Added `lms-mcp` dependency |

## Acceptance Criteria

- [x] Nanobot is installed in the repo-local `nanobot/` project from PyPI (`uv add nanobot-ai`) and configured via `nanobot onboard`
- [x] The agent responds to general questions via the repo-local `nanobot/config.json`
- [x] MCP tools are configured and the agent returns real backend data
- [x] A skill prompt exists that guides the agent's tool usage
- [x] `REPORT.md` contains responses from all three checkpoints

## Testing

### Test Commands

```bash
# Part A — Bare agent
cd nanobot
uv run nanobot agent -c ./config.json -m "What is the agentic loop?"
uv run nanobot agent -c ./config.json -m "What labs are available in our LMS?"

# Part B — Agent with LMS tools
uv run nanobot agent -c ./config.json -m "What labs are available?"
uv run nanobot agent -c ./config.json -m "Describe the architecture of the LMS system"

# Part C — Skill prompt
uv run nanobot agent -c ./config.json -m "Show me the scores"
uv run nanobot agent -c ./config.json -m "What is the pass rate for lab-01?"
```

### Expected Results

- **Part A**: Agent answers general questions but hallucinates about LMS (reads workspace files)
- **Part B**: Agent returns real lab names and architecture details from MCP tools
- **Part C**: Agent formats responses nicely and handles missing lab parameters gracefully

## Next Steps (Task 2)

- Dockerize the nanobot agent
- Add WebSocket channel for web client
- Build Flutter chat UI
- Configure Caddy to route `/ws/chat` to nanobot
