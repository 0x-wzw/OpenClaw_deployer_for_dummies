#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# OpenClaw Deployment UI — startup script
# Installs dependencies and launches the wizard at http://localhost:5000
# ─────────────────────────────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/venv"

echo ""
echo "  🦞  OpenClaw Cloud Deployer"
echo "  ─────────────────────────────"

# ── 1. Python check ─────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "  ❌  Python 3 is required but not found."
  echo "      Install it from https://python.org/downloads/ and try again."
  exit 1
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "  ✓  Python $PY_VER found"

# ── 2. Virtual environment ──────────────────────────────────────
if [ ! -d "$VENV" ]; then
  echo "  Creating virtual environment…"
  python3 -m venv "$VENV"
fi

# shellcheck source=/dev/null
source "$VENV/bin/activate"

# ── 3. Install / upgrade dependencies ───────────────────────────
echo "  Installing dependencies…"
pip install --quiet --upgrade pip
pip install --quiet -r "$SCRIPT_DIR/requirements.txt"

echo "  ✓  All dependencies installed"

# ── 4. Optional: boto3 for AWS support ─────────────────────────
if ! python3 -c "import boto3" 2>/dev/null; then
  echo ""
  echo "  ℹ️   boto3 (AWS SDK) not installed."
  echo "      To deploy on AWS, run:  pip install boto3"
  echo ""
fi

# ── 5. Launch the UI ────────────────────────────────────────────
echo ""
echo "  🚀  Starting the deployment wizard…"
echo "  ─────────────────────────────────────"
echo "  Open your browser at:  http://localhost:5000"
echo "  Press Ctrl+C to stop."
echo ""

cd "$SCRIPT_DIR"
python3 -m ui.app
