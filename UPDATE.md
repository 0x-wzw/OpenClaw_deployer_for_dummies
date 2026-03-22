# Weekly Update Process

## Overview

This repository is updated **weekly** with improvements, new features, and optimizations.

**Update Day:** Every Sunday  
**Update Time:** 04:00 UTC (aligned with HEARTBEAT)

---

## Quick Update

```bash
# 1. Navigate to repo
cd /path/to/OpenClaw_deployer_for_dummies

# 2. Pull latest changes
git pull origin main

# 3. Run update script
./update.sh

# 4. Verify
openclaw --version
```

---

## Detailed Update Process

### Step 1: Check for Updates

```bash
# Fetch latest changes without applying
git fetch origin

# See what's new
git log HEAD..origin/main --oneline
```

### Step 2: Review Changes

**Before updating, review:**
- [VERSION.md](VERSION.md) — What's changed
- [CHANGELOG](#changelog) below — Detailed changes
- [BREAKING_CHANGES.md](#breaking-changes) — If applicable

### Step 3: Backup Current Setup

```bash
# Backup OpenClaw config
cp -r ~/.openclaw ~/.openclaw.backup.$(date +%Y%m%d)

# Backup this repo
cd /path/to/OpenClaw_deployer_for_dummies
git stash
```

### Step 4: Apply Update

```bash
# Pull changes
git pull origin main

# Run update script
./update.sh

# Or manual update
./install.sh --update
```

### Step 5: Verify

```bash
# Check version
cat VERSION.md | grep "Current Version"

# Test OpenClaw
openclaw --version
openclaw status

# Check Ollama
curl http://localhost:11434/api/tags
```

### Step 6: Review Insights

After updating, review the weekly insights:

```bash
# View insights
cat insights/$(date +%Y-%m-%d).md
```

---

## Changelog

### Week of 2026-03-22 (v1.0.0)

#### Added
- Initial release
- Ollama-first setup guide
- Automated installation script
- Local model configuration
- Extension integration system
- Version tracking
- Weekly update process

#### Changed
- N/A (initial release)

#### Fixed
- N/A (initial release)

---

## Breaking Changes

**None yet** — This section will document any breaking changes in future updates.

When a breaking change occurs:
1. Major version bump (e.g., 1.x.x → 2.0.0)
2. Migration guide provided
3. Backward compatibility maintained for 1 version

---

## Gathering Insights

Each week, we gather insights from:

### 1. User Feedback
- GitHub issues
- Pull requests
- Community discussions

### 2. Performance Metrics
- Setup success rate
- Common errors
- Time to completion

### 3. Extension Updates
- SentientForge releases
- SovereignStack updates
- Swarm Agent Kit changes

### 4. Ollama Updates
- New models
- Performance improvements
- Bug fixes

### 5. OpenClaw Updates
- New features
- API changes
- Deprecations

---

## Insight Reports

Weekly insight reports are stored in `insights/`:

```
insights/
├── 2026-03-22.md
├── 2026-03-29.md
└── ...
```

Each report includes:
- Setup success metrics
- Common issues encountered
- Performance benchmarks
- Recommended improvements
- Next week's focus

---

## Pruning Unnecessary Steps

We actively prune unnecessary complexity:

### Pruning Criteria
- Steps that fail >20% of the time
- Redundant configuration options
- Outdated workarounds
- Unused features

### Pruning Process
1. Identify problematic steps (via feedback)
2. Propose simplification
3. Test with 5+ users
4. Update guide
5. Document in changelog

---

## Contributing Updates

### For Users

**Report issues:**
```bash
# Create issue on GitHub
gh issue create --title "Update: [description]" \
  --body "Current version: X.X.X\nIssue: [description]"
```

**Suggest improvements:**
- Open a pull request
- Include change description
- Update VERSION.md
- Update this CHANGELOG

### For Maintainers

**Weekly update checklist:**
- [ ] Review GitHub issues
- [ ] Check extension updates
- [ ] Test installation on fresh VM
- [ ] Update VERSION.md
- [ ] Update CHANGELOG
- [ ] Create insight report
- [ ] Tag release
- [ ] Announce update

---

## Update Notifications

**Get notified of updates:**

1. **Watch this repo** on GitHub
2. **Enable notifications** for releases
3. **Join the community** (link TBD)

---

## Rollback

**If update breaks something:**

```bash
# Restore from backup
cp -r ~/.openclaw.backup.YYYYMMDD ~/.openclaw

# Or revert git changes
cd /path/to/OpenClaw_deployer_for_dummies
git reset --hard HEAD~1

# Reinstall previous version
./install.sh --version X.X.X
```

---

## Questions?

- **Update failed?** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Breaking change?** Check [BREAKING_CHANGES.md](#breaking-changes)
- **Need help?** Open a GitHub issue

---

*Weekly updates keep OpenClaw Deployer for Dummies fresh and reliable.*  
*Last updated: 2026-03-22*
