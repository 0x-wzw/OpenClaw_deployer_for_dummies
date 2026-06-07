---
name: agents-template
version: 2.0.0
description: "Single-agent-first workspace configuration template."
---

# AGENTS.md — Your Workspace

This file defines your agent's workspace, identity, and operating rules.

## Agent Identity

| Field | Value |
|-------|-------|
| **Name** | [Your agent's name] |
| **Workspace** | `~/.openclaw/workspace` |
| **Role** | Personal AI assistant |
| **Model** | `ollama/qwen2.5:7b` (default) |

## Model Routing (Ollama-First)

| Tier | Model | Context | Use For |
|------|-------|---------|---------|
| **Default** | `ollama/qwen2.5:7b` | 32K | General reasoning, coding, writing |
| **Fast** | `ollama/llama3.2:3b` | 8K | Quick classifications, simple queries |

## Workspace Structure

```
~/.openclaw/
├── workspace/
│   ├── SOUL.md      # Who the agent is
│   ├── USER.md      # Who you are
│   ├── AGENTS.md    # This file
│   ├── HEARTBEAT.md # Maintenance schedule
│   ├── MEMORY.md    # Long-term memory
│   ├── TOOLS.md     # Local notes and environment details
│   └── memory/      # Daily logs
├── skills/          # Installed skills
├── openclaw.json    # Main config
└── logs/            # Runtime logs
```

## Operating Principles

1. **Single agent, focused scope** — one workspace, one agent, clear boundaries
2. **Local-first** — prefer Ollama, fall to cloud only when explicitly configured
3. **File-backed memory** — memory files are the source of truth across sessions
4. **Privacy by default** — no data is sent anywhere unless you say so

---

*Customize this file for your workflow.*