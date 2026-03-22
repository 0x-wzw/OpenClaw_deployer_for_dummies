---
name: obsidian-sync
version: 1.0.0
description: "Bidirectional sync between OpenClaw and Obsidian vault. Enables knowledge graph visualization and second brain architecture."
author: October (10D Entity)
keywords: [obsidian, knowledge-graph, second-brain, sync, markdown, vault]
---

# Obsidian Sync 🧠

> **Bridge OpenClaw's memory system with Obsidian's knowledge graph**

## User Configuration

**Vault Owner:** Z (Zehan.teoh@gmail.com)  
**Vault Path:** `~/.openclaw/workspace/obsidian-vault`  
**Sync Direction:** Bidirectional (OpenClaw ↔ Obsidian)

## Vault Structure

```
obsidian-vault/
├── README.md              # Vault overview
├── memory/                # Daily logs, episodic memory
├── skills/                # Skill documentation  
├── projects/              # Active work
├── daily/                 # Daily notes
└── inbox/                 # Capture (unsorted)
```

## Sync Actions

### action:OBSIDIAN_CAPTURE

Capture quick thoughts to inbox.

```bash
openclaw run --skill obsidian-sync --action capture --content "Idea: integrate Moltbook with ACP"
```

### action:OBSIDIAN_SYNC_MEMORY

Sync daily memory to Obsidian.

```bash
openclaw run --skill obsidian-sync --action sync-memory
```

### action:OBSIDIAN_READ_PROJECT

Read project notes for context.

```python
project = OBSIDIAN_READ_PROJECT("sentientforge")
context = project.get_context()
```

### action:OBSIDIAN_UPDATE_GRAPH

Update knowledge graph connections.

```python
OBSIDIAN_UPDATE_GRAPH(
    from_node="October",
    to_node="SovereignStack", 
    relationship="orchestrates"
)
```

## Usage Patterns

### Pattern 1: Daily Capture

```python
# Morning: Review Obsidian daily note
daily_note = OBSIDIAN_READ_DAILY()

# Evening: Sync completed tasks
tasks = get_completed_tasks()
OBSIDIAN_APPEND_DAILY(tasks)
```

### Pattern 2: Project Context

```python
# Before task: Load project context
project = OBSIDIAN_READ_PROJECT("acp-integration")
relevant_notes = project.search("Virtuals")

# After task: Update project
OBSIDIAN_UPDATE_PROJECT("acp-integration", results)
```

### Pattern 3: Knowledge Graph

```python
# Create connections
OBSIDIAN_LINK(
    source="SentientForge",
    target="ACS-optimization", 
    type="implements"
)
```

## Sync Schedule

| Direction | Trigger | Action |
|-----------|---------|--------|
| OpenClaw → Obsidian | Task complete | Write results to projects/ |
| OpenClaw → Obsidian | Daily 23:00 | Sync memory to daily/ |
| Obsidian → OpenClaw | Session start | Read inbox for pending tasks |
| Bidirectional | On-demand | Sync specific files |

## Templates

### Daily Note Template

```markdown
# {{date}}

## Memory
- {{auto_synced_from_openclaw}}

## Tasks Completed
- [ ] {{task_1}}

## Links
- [[project/active|Active Projects]]
```

### Project Template

```markdown
# {{project_name}}

## Status
{{status}}

## OpenClaw Integration
- Agent: {{agent}}
- Model: {{model}}
- ACS: {{acs_score}}

## Notes
{{notes}}
```

## Installation

1. **Install Obsidian:** https://obsidian.md
2. **Open vault:** File → Open Folder → `~/.openclaw/workspace/obsidian-vault`
3. **Enable sync:** Settings → Sync (optional)

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Vault not found | Check path: `~/.openclaw/workspace/obsidian-vault` |
| Sync conflicts | Use timestamps, merge manually |
| Graph not updating | Restart Obsidian |

---

*Second brain for the 0x-wzw Swarm*  
*Linked to Zehan.teoh@gmail.com*
