---
name: agents-template
version: 1.0.0
description: "Multi-agent workspace configuration template."
---

# AGENTS.md - Multi-Agent Workspace

## Agent Roster

| Agent | Workspace | Role | Persona |
|-------|-----------|------|---------|
| **[Agent 1]** | `~/.openclaw/workspace` | [Role] | [Persona] |
| **[Agent 2]** | `~/.openclaw/workspace-[name]` | [Role] | [Persona] |

## Model Routing (Ollama-First)

| Tier | Model | Context | Use For |
|------|-------|---------|---------|
| **T1** | `ollama/qwen2.5:3b` | 32K | General tasks |
| **T2** | `ollama/phi3` | 4K | Fast tasks |

## Swarm Protocol
Every significant task triggers swarm simulation:
- Spawn specialized sub-agents
- Run sub-agents in parallel
- Synthesize outputs
- Execute with minimal supervision
