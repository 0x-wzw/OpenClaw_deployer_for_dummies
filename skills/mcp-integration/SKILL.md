---
name: mcp-integration
version: 1.0.0
description: "Model Context Protocol (MCP) server integration for standardized tool extensibility. Adapted from DeerFlow's MCP ecosystem."
author: October (10D Entity)
keywords: [mcp, model-context-protocol, tools, integration, extensibility, servers]
---

# MCP Integration 🔌

> **Standardized tool ecosystem via Model Context Protocol**
> 
> *Adapted from DeerFlow's MCP server architecture*

## Overview

Integrate external tools via MCP (Model Context Protocol):
- **File System** — Read/write files, search directories
- **Web Search** — Tavily, Brave, Google
- **Database** — PostgreSQL, SQLite, MongoDB
- **Browser** — Selenium, Playwright automation
- **GitHub** — Issues, PRs, code review
- **Custom** — Any MCP-compatible server

## Architecture

```
OpenClaw Agent
    ↓
MCP Client (stdio/sse)
    ↓
┌─────────────────────────────────────┐
│  MCP Servers (external processes) │
│  ├─ filesystem                      │
│  ├─ web-search (tavily)           │
│  ├─ database                        │
│  ├─ browser-automation              │
│  └─ custom-tools                      │
└─────────────────────────────────────┘
```

## MCP Servers Available

| Server | Function | Install |
|--------|----------|---------|
| **filesystem** | File operations | `npx -y @modelcontextprotocol/server-filesystem` |
| **web-search** | Search via Tavily | `npx -y @tavily/mcp` |
| **brave-search** | Search via Brave | `npx -y @modelcontextprotocol/server-brave-search` |
| **github** | GitHub operations | `npx -y @modelcontextprotocol/server-github` |
| **postgresql** | Database queries | `npx -y @modelcontextprotocol/server-postgres` |
| **sqlite** | SQLite operations | `npx -y @modelcontextprotocol/server-sqlite` |
| **puppeteer** | Browser automation | `npx -y @modelcontextprotocol/server-puppeteer` |

## Configuration

```json
// ~/.openclaw/mcp.json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "~/.openclaw/workspace"]
    },
    "web-search": {
      "command": "npx",
      "args": ["-y", "@tavily/mcp"],
      "env": {
        "TAVILY_API_KEY": "${TAVILY_API_KEY}"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

## Usage

### File System Operations

```python
# Via MCP filesystem server
result = mcp_client.call(
    server="filesystem",
    tool="read_file",
    arguments={"path": "/path/to/file.md"}
)
```

### Web Search

```python
# Via Tavily MCP
results = mcp_client.call(
    server="web-search",
    tool="search",
    arguments={
        "query": "latest LLM benchmarks",
        "max_results": 5
    }
)
```

### Database Queries

```python
# Via PostgreSQL MCP
data = mcp_client.call(
    server="postgresql",
    tool="query",
    arguments={
        "sql": "SELECT * FROM models WHERE acs > 0.9"
    }
)
```

## Integration with Swarm

### In Cost Router

```python
# Use MCP tools based on task requirements
def route_with_mcp(task):
    if task.requires_search:
        return "mcp:web-search"
    if task.requires_filesystem:
        return "mcp:filesystem"
    if task.requires_database:
        return "mcp:postgresql"
    return default_model
```

### In Skills

Skills can declare MCP dependencies:

```yaml
# In SKILL.md
mcp:
  required_servers:
    - filesystem
    - web-search
  optional_servers:
    - github
```

Auto-start servers when skill loads:

```python
skill = load_skill("deeper-research")
skill.ensure_mcp_servers()
```

## Custom MCP Server

Create your own MCP server for Swarm-specific tools:

```python
# mcp-swarm/server.py
from mcp.server import Server
from mcp.types import Tool

app = Server("swarm-tools")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="spawn_subagent",
            description="Spawn a sub-agent for parallel execution",
            parameters={
                "agent_type": "string",
                "task": "string",
                "model": "string"
            }
        ),
        Tool(
            name="query_memory",
            description="Search episodic memory",
            parameters={
                "query": "string",
                "limit": "integer"
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "spawn_subagent":
        return await spawn_subagent(**arguments)
    elif name == "query_memory":
        return await query_memory(**arguments)

if __name__ == "__main__":
    app.run()
```

## Comparison to DeerFlow

| Aspect | DeerFlow | Swarm MCP Integration |
|--------|----------|----------------------|
| **Protocol** | MCP | Same |
| **Servers** | filesystem, web-search, etc. | Same + Swarm custom |
| **Transport** | stdio/sse | stdio/sse |
| **Integration** | LangGraph | Swarm Protocol |
| **Discovery** | Manual | Auto via skill deps |
| **Economic** | Cost tracking | Token economy aware |

## Security

| Risk | Mitigation |
|------|------------|
| **Arbitrary code execution** | Sandboxed MCP servers |
| **Data exfiltration** | Network isolation per server |
| **Credential exposure** | Env vars, not hardcoded |
| **Server compromise** | Read-only where possible |

---

*Standardized tool ecosystem via Model Context Protocol*
*Adapted from DeerFlow's MCP architecture*
