#!/bin/bash
# OpenClaw Deployer Update Script
# Version: 1.0.0

set -e

VERSION="1.0.0"
REPO_URL="https://github.com/0x-wzw/OpenClaw_deployer_for_dummies"

echo "🦞 OpenClaw Deployer Updater v$VERSION"
echo "=================================="

# Check if we're in the right directory
if [[ ! -f "VERSION.md" ]]; then
    echo "❌ Error: Not in OpenClaw_deployer_for_dummies directory"
    echo "   Please run from the repo root"
    exit 1
fi

# Backup current version
echo "📦 Creating backup..."
cp -r ~/.openclaw ~/.openclaw.backup.$(date +%Y%m%d) 2>/dev/null || true

# Fetch updates
echo "⬇️  Fetching updates..."
git fetch origin

# Show what's new
echo ""
echo "📋 Changes since last update:"
git log HEAD..origin/main --oneline --no-decorate

echo ""
read -p "Continue with update? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Update cancelled"
    exit 0
fi

# Pull changes
echo "⬇️  Applying updates..."
git pull origin main

# Check if install.sh changed
if git diff --name-only HEAD~1 | grep -q "install.sh"; then
    echo "🔄 install.sh changed — re-running installer"
    ./install.sh --update
fi

# Update extensions
echo "🔄 Updating extensions..."
cd ~/.openclaw/workspace/skills || exit 1

for dir in */; do
    if [[ -d "$dir/.git" ]]; then
        echo "  Updating $dir..."
        cd "$dir" && git pull origin main 2>/dev/null || true
        cd ..
    fi
done

# Show new version
echo ""
echo "✅ Update complete!"
echo "New version:"
grep "Current Version" VERSION.md | head -1

echo ""
echo "📊 What's new:"
cat UPDATE.md | grep -A 20 "Week of $(date +%Y-%m-%d)" | head -25 || echo "See UPDATE.md for details"

echo ""
echo "🦞 OpenClaw is ready to use!"
