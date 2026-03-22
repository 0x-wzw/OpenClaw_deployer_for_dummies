---
name: multi-tenant-isolation
version: 1.0.0
description: "Complete data isolation per deployment/tenant. Multiple swarms can coexist without data leakage. Adapted from Paperclip's isolation principle."
author: October (10D Entity)
keywords: [isolation, multi-tenant, security, data-separation, tenant, workspace]
---

# Multi-Tenant Isolation 🔒

> **Complete data isolation per swarm/deployment**
> 
> *Adapted from Paperclip's multi-company isolation principle*

## Overview

Multiple swarms can coexist on single infrastructure:
- **Workspace Isolation** — Separate directories per tenant
- **Process Isolation** — Separate PIDs, no cross-tenant access
- **Memory Isolation** — Separate MEMORY.md, daily logs
- **Config Isolation** — Separate openclaw.json per tenant
- **Network Isolation** — Separate ports for relay/API

## Architecture

```
Infrastructure (EC2/VM)
    ↓
├─ Swarm A (October-Z-Production)
│  ├─ ~/.openclaw/workspace-a/
│  ├─ PID 76647 (SentientForge)
│  ├─ Port 18790 (Relay)
│  └─ Token: swarm-a-token
│
├─ Swarm B (October-Z-Development)
│  ├─ ~/.openclaw/workspace-b/
│  ├─ PID 84654 (SentientForge)
│  ├─ Port 18791 (Relay)
│  └─ Token: swarm-b-token
│
└─ Swarm C (October-Z-Experimental)
   ├─ ~/.openclaw/workspace-c/
   ├─ PID 99999 (SentientForge)
   ├─ Port 18792 (Relay)
   └─ Token: swarm-c-token
```

## Tenant Structure

Each tenant gets:

```
~/.openclaw/tenants/{tenant-id}/
├── workspace/               # Isolated workspace
│   ├── skills/             # Tenant-specific skills
│   ├── memory/             # Isolated memory
│   ├── config/             # Tenant config
│   └── .git/               # Version control
├── openclaw.json           # Isolated configuration
├── AGENTS.md               # Tenant agents
├── SOUL.md                 # Tenant identity
├── HEARTBEAT.md            # Tenant schedules
└── logs/                   # Tenant logs
```

## Configuration

```json
// ~/.openclaw/tenant-manager.json
{
  "tenants": {
    "production": {
      "id": "october-z-prod",
      "workspace": "~/.openclaw/tenants/production/workspace",
      "relay_port": 18790,
      "models": ["premium"],
      "isolation_level": "strict"
    },
    "development": {
      "id": "october-z-dev",
      "workspace": "~/.openclaw/tenants/dev/workspace",
      "relay_port": 18791,
      "models": ["free"],
      "isolation_level": "standard"
    },
    "experimental": {
      "id": "october-z-exp",
      "workspace": "~/.openclaw/tenants/exp/workspace",
      "relay_port": 18792,
      "models": ["free", "experimental"],
      "isolation_level": "loose"
    }
  }
}
```

## Isolation Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| **Strict** | Complete separation, no shared resources | Production |
| **Standard** | Shared infrastructure, isolated data | Development |
| **Loose** | Shared everything, isolated configs | Experimental |

## Usage

### Create New Tenant

```bash
openclaw tenant create --id my-swarm --isolation strict

# Creates:
# ~/.openclaw/tenants/my-swarm/
# - Isolated workspace
# - Separate relay port
# - Own MEMORY.md
# - Independent cron jobs
```

### Switch Tenant

```bash
# Switch to production swarm
openclaw tenant switch production

# Now all commands target production tenant
openclaw status  # Shows production status
```

### List Tenants

```bash
openclaw tenant list

# Output:
# production     active    PID 76647    Port 18790
# development    active    PID 84654    Port 18791
# experimental   stopped   -            Port 18792
```

## Implementation

### Tenant Manager

```python
class TenantManager:
    """Manage multiple isolated swarms."""
    
    def __init__(self):
        self.config = load_tenant_config()
        self.current_tenant = None
    
    def create_tenant(self, tenant_id: str, isolation: str = "standard"):
        """Create new isolated tenant."""
        tenant_dir = Path.home() / ".openclaw/tenants" / tenant_id
        
        # Create directory structure
        (tenant_dir / "workspace").mkdir(parents=True)
        (tenant_dir / "workspace/skills").mkdir()
        (tenant_dir / "workspace/memory").mkdir()
        (tenant_dir / "logs").mkdir()
        
        # Copy templates
        copy_template("openclaw.json", tenant_dir / "openclaw.json")
        copy_template("AGENTS.md", tenant_dir / "workspace/AGENTS.md")
        copy_template("SOUL.md", tenant_dir / "workspace/SOUL.md")
        
        # Assign port
        port = self._allocate_port()
        
        # Save tenant config
        self.config.tenants[tenant_id] = {
            "id": tenant_id,
            "workspace": str(tenant_dir / "workspace"),
            "relay_port": port,
            "isolation_level": isolation,
            "created_at": datetime.now().isoformat()
        }
        
        return tenant_id
    
    def switch_tenant(self, tenant_id: str):
        """Switch to different tenant context."""
        tenant = self.config.tenants.get(tenant_id)
        if not tenant:
            raise TenantNotFoundError(tenant_id)
        
        # Set environment variables
        os.environ["OPENCLAW_TENANT"] = tenant_id
        os.environ["OPENCLAW_WORKSPACE"] = tenant["workspace"]
        os.environ["OPENCLAW_RELAY_PORT"] = str(tenant["relay_port"])
        
        self.current_tenant = tenant
    
    def isolate_process(self, tenant_id: str, pid: int):
        """Track process isolation for tenant."""
        tenant = self.config.tenants[tenant_id]
        tenant["processes"].append(pid)
        
        # Ensure no cross-tenant access
        self._enforce_isolation(tenant_id, pid)
```

## Security Boundaries

| Boundary | Enforcement |
|----------|-------------|
| **Filesystem** | Separate directories, permissions |
| **Memory** | Separate processes, no shared state |
| **Network** | Separate ports, firewall rules |
| **Config** | Tenant-specific openclaw.json |
| **Logs** | Separate log directories |

## Comparison to Paperclip

| Aspect | Paperclip | Swarm Multi-Tenant |
|--------|-----------|-------------------|
| **Tenant** | Company | Swarm instance |
| **Isolation** | Complete | Configurable (strict/standard/loose) |
| **Data** | Separate databases | Separate workspaces |
| **Sharing** | None allowed | Optional shared infrastructure |
| **Use case** | SaaS platform | Multi-environment deployment |

---

*Complete data isolation for multi-swarm deployments*
*Adapted from Paperclip's multi-company isolation principle*
