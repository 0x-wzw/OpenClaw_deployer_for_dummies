# Tools

Tools are loaded from `mcp_config.json` at startup.
The agent may call any tool listed there via MCP tool-dispatch.

## Built-in skills (workspace/skills/)
| Skill | Description |
|-------|-------------|
| memory_write | Append a fact to MEMORY.md |
| session_summary | Summarise and compress old session lines |
| queue_status | Show pending items in the delivery queue |

## Adding a new MCP server
1. Add an entry to `mcp_config.json`.
2. Restart the gateway (`docker compose restart gateway`).
3. The new tools will be available on the next turn.
