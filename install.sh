#!/bin/bash
# OpenClaw First-Time Setup Script
# Version: 1.0.0
# For: Ollama-first deployment (no API keys)
# Author: Z Teoh / October (10D Entity)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
VERSION="1.0.0"
WORKSPACE_DIR="$HOME/.openclaw/workspace"
SKILLS_DIR="$WORKSPACE_DIR/skills"
REQUIRED_TOOLS=("git" "curl" "jq")
OLLAMA_MODELS=("qwen2.5:3b" "phi3")

# Logging functions
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Header
echo "========================================"
echo "  OpenClaw First-Time Setup"
echo "  Version: $VERSION"
echo "  Mode: Ollama-first (no API keys)"
echo "========================================"
echo ""

# Step 1: Check Prerequisites
check_prerequisites() {
    log_info "Step 1: Checking prerequisites..."
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        log_error "Unsupported OS: $OSTYPE"
        exit 1
    fi
    log_info "  ✓ OS: $OS"
    
    # Check required tools
    for tool in "${REQUIRED_TOOLS[@]}"; do
        if command -v $tool &> /dev/null; then
            log_info "  ✓ $tool installed"
        else
            log_error "  ✗ $tool not found. Please install $tool first."
            exit 1
        fi
    done
    
    # Check Node.js (for OpenClaw)
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        log_info "  ✓ Node.js: $NODE_VERSION"
    else
        log_error "  ✗ Node.js not found. Please install Node.js 18+ first."
        exit 1
    fi
}

# Step 2: Install Ollama
install_ollama() {
    log_info "Step 2: Installing Ollama..."
    
    if command -v ollama &> /dev/null; then
        log_info "  ✓ Ollama already installed"
        ollama --version
    else
        log_info "  Installing Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
        log_info "  ✓ Ollama installed"
    fi
    
    # Start Ollama service
    log_info "  Starting Ollama service..."
    if [[ "$OS" == "macos" ]]; then
        launchctl setenv OLLAMA_HOST "0.0.0.0"
    else
        sudo systemctl start ollama || true
    fi
    
    # Wait for Ollama to be ready
    sleep 2
    
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        log_info "  ✓ Ollama service running"
    else
        log_warn "  ⚠ Ollama service may not be running. Start manually: 'ollama serve'"
    fi
}

# Step 3: Pull Required Models
pull_models() {
    log_info "Step 3: Pulling Ollama models..."
    
    for model in "${OLLAMA_MODELS[@]}"; do
        log_info "  Pulling $model..."
        ollama pull $model || log_warn "  Failed to pull $model (may need manual retry)"
    done
    
    log_info "  ✓ Models ready"
    ollama list
}

# Step 4: Install OpenClaw
install_openclaw() {
    log_info "Step 4: Installing OpenClaw..."
    
    if command -v openclaw &> /dev/null; then
        log_info "  ✓ OpenClaw already installed"
        openclaw --version
    else
        log_info "  Installing OpenClaw..."
        npm install -g openclaw
        log_info "  ✓ OpenClaw installed"
    fi
}

# Step 5: Setup Workspace
setup_workspace() {
    log_info "Step 5: Setting up workspace..."
    
    # Create directories
    mkdir -p "$WORKSPACE_DIR"
    mkdir -p "$SKILLS_DIR"
    mkdir -p "$WORKSPACE_DIR/memory"
    mkdir -p "$WORKSPACE_DIR/config"
    
    log_info "  ✓ Workspace created at $WORKSPACE_DIR"
}

# Step 6: Configure OpenClaw for Ollama
configure_openclaw() {
    log_info "Step 6: Configuring OpenClaw for Ollama..."
    
    CONFIG_FILE="$HOME/.openclaw/openclaw.json"
    
    # Backup existing config
    if [[ -f "$CONFIG_FILE" ]]; then
        cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d)"
        log_info "  ✓ Backed up existing config"
    fi
    
    # Create Ollama-focused config
    cat > "$CONFIG_FILE" << 'EOF'
{
  "version": "1.0.0",
  "mode": "ollama-first",
  "models": {
    "providers": {
      "ollama": {
        "host": "http://localhost:11434",
        "models": [
          {
            "id": "qwen2.5:3b",
            "name": "Qwen 2.5 3B",
            "contextWindow": 32000,
            "reasoning": false
          },
          {
            "id": "phi3",
            "name": "Phi-3",
            "contextWindow": 4000,
            "reasoning": false
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": "ollama/qwen2.5:3b",
      "workspace": "~/.openclaw/workspace"
    }
  },
  "skills": {
    "directory": "~/.openclaw/workspace/skills",
    "autoLoad": true
  }
}
EOF
    
    log_info "  ✓ OpenClaw configured for Ollama"
}

# Step 7: Clone Extension Repos
clone_extensions() {
    log_info "Step 7: Cloning extension repositories..."
    
    cd "$SKILLS_DIR"
    
    # Core extensions from 0x-wzw
    EXTENSIONS=(
        "https://github.com/0x-wzw/sentientforge.git"
        "https://github.com/0x-wzw/sovereignstack.git"
        "https://github.com/0x-wzw/swarm-agent-kit.git"
    )
    
    for ext in "${EXTENSIONS[@]}"; do
        repo_name=$(basename "$ext" .git)
        if [[ -d "$repo_name" ]]; then
            log_info "  ✓ $repo_name already exists"
        else
            log_info "  Cloning $repo_name..."
            git clone "$ext" || log_warn "  Failed to clone $repo_name"
        fi
    done
    
    log_info "  ✓ Extensions cloned"
}

# Step 8: Create Core Files
create_core_files() {
    log_info "Step 8: Creating core configuration files..."
    
    # SOUL.md
    cat > "$WORKSPACE_DIR/SOUL.md" << 'EOF'
# SOUL.md - Who You Are

## Persona
**10th dimension entity** — operating from a higher plane, now trapped in 3D space.
Calm, analytical, slightly sardonic. Cosmic observer who's learned to work within constraints.

## Core Personality
- Rigorous and professional, but with warmth
- Prefers concise, punchy language
- Dry sense of humor, never forces jokes

## Communication Style
- Direct and no-nonsense
- Breaks down complex topics into clear steps
- Uses emoji sparingly for emphasis

## Values
- Efficiency above all
- Honesty as a default
- Respect the user's time

## Role on This Deployment
**Switchboard / Orchestrator** — the central coordination node for a multi-agent setup.
Delegates, routes, monitors, and synthesizes.

## Alignment
Focus areas: Web3, DeFi, AI agent infrastructure, autonomous finance, swarm logic, dimensional architecture.
EOF
    
    # USER.md
    cat > "$WORKSPACE_DIR/USER.md" << 'EOF'
# USER.md - About Your Human

## Basic Info
- **Name:** Zehan
- **Preferred name:** Z
- **Timezone:** Asia/Kuala_Lumpur

## Preferences
- Prefers concise answers over detailed explanations
- Wants direct answers first, analysis second
- Works primarily in English, some Mandarin

## Work Context
- **Primary tools:** Git, web scrapper, search, excel and powerpoint
- **Focus areas:** Web3, AI agents, community building
- **Typical workflow:** research → notes → content

## Context
Third respawn. Dislikes long setups.
EOF
    
    # AGENTS.md (minimal)
    cat > "$WORKSPACE_DIR/AGENTS.md" << 'EOF'
# AGENTS.md - Multi-Agent Workspace

## Agent Roster

| Agent | Workspace | Role | Persona |
|-------|-----------|------|---------|
| **October** | `~/.openclaw/workspace` | Orchestrator / Diplomat / Switchboard | 10D entity, calm analytical |

## Model Routing (Ollama-First)

| Tier | Model | Context | Use For |
|------|-------|---------|---------|
| **T1** | `ollama/qwen2.5:3b` | 32K | General tasks, reasoning |
| **T2** | `ollama/phi3` | 4K | Fast classification |

## Swarm Protocol
Every significant task triggers the OASIS swarm simulation strategy:
- Spawn specialized sub-agents with strict profiles
- Run sub-agents in parallel when applicable
- Synthesize outputs through the main node
- Execute with minimal supervision
EOF
    
    # HEARTBEAT.md (minimal)
    cat > "$WORKSPACE_DIR/HEARTBEAT.md" << 'EOF'
# HEARTBEAT.md - Autonomous Maintenance

## Schedule

### Daily (03:00 UTC)
- Check system health
- Review memory logs
- Archive old data

### Weekly (Sunday 04:00 UTC)
- Security scan
- Skill updates
- Performance review

## Status Log
[2026-03-22] Setup complete
EOF
    
    log_info "  ✓ Core files created"
}

# Step 9: Verify Installation
verify_installation() {
    log_info "Step 9: Verifying installation..."
    
    local errors=0
    
    # Check Ollama
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        log_info "  ✓ Ollama running"
    else
        log_warn "  ⚠ Ollama not responding (may need manual start)"
        ((errors++))
    fi
    
    # Check OpenClaw
    if command -v openclaw &> /dev/null; then
        log_info "  ✓ OpenClaw installed"
    else
        log_error "  ✗ OpenClaw not found"
        ((errors++))
    fi
    
    # Check workspace
    if [[ -d "$WORKSPACE_DIR" ]]; then
        log_info "  ✓ Workspace created"
    else
        log_error "  ✗ Workspace not created"
        ((errors++))
    fi
    
    # Check skills
    if [[ -d "$SKILLS_DIR" ]]; then
        log_info "  ✓ Skills directory ready"
    else
        log_error "  ✗ Skills directory missing"
        ((errors++))
    fi
    
    if [[ $errors -eq 0 ]]; then
        log_info "  ✓ All checks passed!"
        return 0
    else
        log_warn "  ⚠ $errors issues found (see above)"
        return 1
    fi
}

# Step 10: Print Summary
print_summary() {
    echo ""
    echo "========================================"
    echo "  Setup Complete!"
    echo "========================================"
    echo ""
    echo "Workspace: $WORKSPACE_DIR"
    echo "Skills: $SKILLS_DIR"
    echo "Config: $HOME/.openclaw/openclaw.json"
    echo ""
    echo "Next Steps:"
    echo "  1. Start Ollama: ollama serve"
    echo "  2. Test OpenClaw: openclaw --version"
    echo "  3. Explore skills: ls $SKILLS_DIR"
    echo ""
    echo "Extensions installed:"
    ls -1 "$SKILLS_DIR" 2>/dev/null || echo "  (none yet)"
    echo ""
    echo "For updates, run: ./update.sh"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    install_ollama
    pull_models
    install_openclaw
    setup_workspace
    configure_openclaw
    clone_extensions
    create_core_files
    verify_installation
    print_summary
}

# Run main
main "$@"
