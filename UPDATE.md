# Updating

This repo is periodically updated with improvements.

## Quick Update

```bash
# 1. Navigate to the repo
cd /path/to/OpenClaw_deployer_for_dummies

# 2. Pull latest changes
git pull origin main

# 3. Review what changed
cat VERSION.md
```

That's it — review the changelog in `VERSION.md` for details on each release.

## Rollback

If an update breaks your setup:

```bash
git log --oneline          # find the commit before the update
git reset --hard <commit>  # revert
```

---

*Updates should be simple. If they're not, open an issue.*