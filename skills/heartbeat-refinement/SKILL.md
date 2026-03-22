---
name: heartbeat-refinement
version: 1.0.0
description: "Refined heartbeat scheduling with cleaner intervals, atomic task checkout, and goal ancestry tracking. Adapted from Paperclip's heartbeat principle."
author: October (10D Entity)
keywords: [heartbeat, scheduling, cron, atomic, goals, tasks, coordination]
---

# Heartbeat Refinement 💓

> **Cleaner scheduling, atomic task checkout, goal ancestry tracking**
> 
> *Adapted from Paperclip's heartbeat coordination principle*

## Overview

Agents wake on schedules to check work and act autonomously. Refined for the Swarm:
- **Cleaner Intervals** — Simplified schedule, clearer boundaries
- **Atomic Task Checkout** — Prevent double-work or race conditions
- **Goal Ancestry** — Every heartbeat task traces to mission

## Refined Schedule

| Schedule | Time | Purpose | Action |
|------------|------|---------|--------|
| **Micro** | Every 5 min | Health checks | Quick status, keepalive |
| **Heartbeat** | Every 30 min | Task coordination | Check pending, spawn agents |
| **Daily** | 03:00 UTC | Full maintenance | Memory index, cost analysis, security scan |
| **Weekly** | Sun 04:00 | Deep optimization | Skill suggestions, trend analysis, governance review |
| **Monthly** | 1st 05:00 | Strategic review | ACS evaluation, mission alignment, roadmap update |

## Atomic Task Checkout

Prevent double-work with checkout system:

```python
class TaskCheckout:
    """Atomic task checkout to prevent double-work."""
    
    def checkout_task(self, agent_id: str, task_id: str) -> CheckoutResult:
        """
        Atomically checkout task for agent.
        
        Returns:
            success: True if checkout succeeded
            lock_id: Unique lock for this checkout
            expires: Lock expiration time
        """
        # Atomic operation
        if self.is_task_checked_out(task_id):
            return CheckoutResult(
                success=False,
                error="Task already checked out"
            )
        
        lock_id = generate_lock_id()
        expires = datetime.now() + timedelta(minutes=30)
        
        # Atomically write checkout
        self._atomic_write_checkout(task_id, agent_id, lock_id, expires)
        
        return CheckoutResult(
            success=True,
            lock_id=lock_id,
            expires=expires
        )
    
    def release_checkout(self, lock_id: str):
        """Release task checkout."""
        self._atomic_remove_checkout(lock_id)
```

## Goal Ancestry in Heartbeat

Every heartbeat task includes ancestry:

```python
class HeartbeatTask:
    """Task with goal ancestry for alignment."""
    
    def __init__(self, description: str, ancestry: Ancestry):
        self.description = description
        self.ancestry = ancestry
        self.alignment_score = calculate_alignment(ancestry)
    
    def execute(self):
        """Execute with ancestry context."""
        log(f"Executing: {self.description}")
        log(f"  Mission: {self.ancestry.mission}")
        log(f"  Goal: {self.ancestry.goal}")
        log(f"  Alignment: {self.alignment_score:.2f}")
        
        # Execute task
        return execute_with_context(self)
```

## Refined Intervals

### Micro (5 min)
- Health checks
- Keepalive pings
- Quick status updates
- No heavy processing

### Heartbeat (30 min)
- Check pending tasks
- Spawn ready agents
- Balance load
- Update metrics

### Daily (03:00 UTC)
- Episodic memory index
- Cost analysis report
- Security scan
- Self-evaluation log review

### Weekly (Sun 04:00)
- Skill pattern detection
- Trend analysis
- Governance review
- Budget reconciliation

### Monthly (1st 05:00)
- Full ACS evaluation
- Mission alignment check
- Roadmap update
- Strategic planning

## Implementation

### Heartbeat Controller

```python
class HeartbeatController:
    """Refined heartbeat scheduling."""
    
    SCHEDULES = {
        "micro": {"interval": 300, "lightweight": True},
        "heartbeat": {"interval": 1800, "lightweight": False},
        "daily": {"time": "03:00", "timezone": "UTC"},
        "weekly": {"day": 6, "time": "04:00", "timezone": "UTC"},
        "monthly": {"day": 1, "time": "05:00", "timezone": "UTC"}
    }
    
    def run(self):
        """Main heartbeat loop."""
        while True:
            current = datetime.now()
            
            # Check each schedule
            for name, config in self.SCHEDULES.items():
                if self.should_run(name, current):
                    self.execute_heartbeat(name)
            
            time.sleep(60)  # Check every minute
    
    def execute_heartbeat(self, name: str):
        """Execute specific heartbeat."""
        tasks = self.get_tasks_for_heartbeat(name)
        
        for task in tasks:
            # Atomic checkout
            checkout = self.task_checkout.checkout(
                agent_id=self.agent_id,
                task_id=task.id
            )
            
            if checkout.success:
                try:
                    result = task.execute()
                    self.task_checkout.release(checkout.lock_id)
                except Exception as e:
                    self.task_checkout.release(checkout.lock_id)
                    log_error(f"Task failed: {e}")
```

## Comparison to Paperclip

| Aspect | Paperclip | Swarm Refined Heartbeat |
|--------|-----------|------------------------|
| **Schedule** | Single heartbeat | Multi-tier (micro/heartbeat/daily/weekly/monthly) |
| **Checkout** | Basic locking | Atomic with expiration |
| **Goal tracking** | Company goals | ACS + token economy aligned |
| **Recovery** | Manual | Auto-retry with backoff |
| **Integration** | Org structure | Swarm protocol + economics |

## Configuration

```json
{
  "heartbeat": {
    "enabled": true,
    "schedules": {
      "micro": {
        "enabled": true,
        "interval": 300
      },
      "heartbeat": {
        "enabled": true,
        "interval": 1800
      },
      "daily": {
        "enabled": true,
        "time": "03:00"
      },
      "weekly": {
        "enabled": true,
        "day": 6,
        "time": "04:00"
      },
      "monthly": {
        "enabled": true,
        "day": 1,
        "time": "05:00"
      }
    },
    "atomic_checkout": {
      "enabled": true,
      "lock_duration": 1800,
      "auto_release": true
    }
  }
}
```

---

*Refined heartbeat scheduling for Swarm coordination*
*Adapted from Paperclip's heartbeat principle with atomic checkout*
