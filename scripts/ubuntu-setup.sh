#!/bin/bash
# Ubuntu System Setup Script for OpenClaw + Ollama
# Version: 1.0.0

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Header
echo "========================================"
echo "  Ubuntu System Setup for OpenClaw"
echo "  Version: 1.0.0"
echo "========================================"
echo ""

# Check Ubuntu version
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    log_info "Detected OS: $NAME $VERSION_ID"
    
    # Check if supported version
    if [[ "$VERSION_ID" != "20.04" && "$VERSION_ID" != "22.04" && "$VERSION_ID" != "24.04" ]]; then
        log_warn "Untested version: $VERSION_ID. Proceeding anyway..."
    fi
else
    log_error "Cannot detect OS version"
    exit 1
fi

# Step 1: Update system
log_info "Step 1: Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Step 2: Install dependencies
log_info "Step 2: Installing dependencies..."
sudo apt install -y \
    build-essential \
    curl \
    wget \
    git \
    jq \
    python3 \
    python3-pip \
    python3-venv \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Step 3: Install Node.js 18
log_info "Step 3: Installing Node.js 18..."
if ! command -v node &> /dev/null || [[ $(node -v | cut -d'v' -f2 | cut -d'.' -f1) -lt 18 ]]; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
fi

log_info "  ✓ Node.js: $(node --version)"

# Step 4: Install Ollama
log_info "Step 4: Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
    log_info "  ✓ Ollama installed"
else
    log_info "  ✓ Ollama already installed: $(ollama --version 2>&1 | head -1)"
fi

# Step 5: Create systemd service for Ollama
log_info "Step 5: Creating Ollama systemd service..."
if [[ ! -f /etc/systemd/system/ollama.service ]]; then
    sudo tee /etc/systemd/system/ollama.service > /dev/null <<EOF
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=10
Environment="PATH=/usr/local/bin:$PATH"

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable ollama
fi

# Start Ollama
log_info "  Starting Ollama service..."
sudo systemctl start ollama || log_warn "Failed to start Ollama (may need manual start)"
sleep 2

# Step 6: Pull required models
log_info "Step 6: Pulling Ollama models..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    log_info "  Pulling qwen2.5:3b..."
    ollama pull qwen2.5:3b || log_warn "Failed to pull qwen2.5:3b"
    
    log_info "  Pulling phi3..."
    ollama pull phi3 || log_warn "Failed to pull phi3"
    
    log_info "  ✓ Models ready:"
    ollama list 2>&1 | grep -E "qwen2.5|phi3" || log_warn "Models not showing in list"
else
    log_warn "Ollama not responding. Start manually: 'ollama serve'"
fi

# Step 7: Install OpenClaw
log_info "Step 7: Installing OpenClaw..."
if ! command -v openclaw &> /dev/null; then
    sudo npm install -g openclaw
    log_info "  ✓ OpenClaw installed"
else
    log_info "  ✓ OpenClaw already installed: $(openclaw --version 2>&1 | head -1)"
fi

# Step 8: Create workspace
log_info "Step 8: Creating workspace..."
mkdir -p ~/.openclaw/workspace
mkdir -p ~/.openclaw/workspace/skills
mkdir -p ~/.openclaw/workspace/memory
chmod -R u+rw ~/.openclaw

# Step 9: Configure OpenClaw
log_info "Step 9: Configuring OpenClaw..."
if [[ ! -f ~/.openclaw/openclaw.json ]]; then
    mkdir -p ~/.openclaw
    cat > ~/.openclaw/openclaw.json << 'EOF'
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
    log_info "  ✓ Configuration created"
fi

# Step 10: Verification
echo ""
echo "========================================"
echo "  Verification"
echo "========================================"

verify_component() {
    local name=$1
    local cmd=$2
    if eval "$cmd" > /dev/null 2>&1; then
        log_info "  ✓ $name: $(eval "$cmd" 2>&1 | head -1)"
        return 0
    else
        log_error "  ✗ $name: Not found or not working"
        return 1
    fi
}

verify_component "Node.js" "node --version"
verify_component "npm" "npm --version"
verify_component "Python3" "python3 --version"
verify_component "Git" "git --version"
verify_component "jq" "jq --version"
verify_component "OpenClaw" "openclaw --version"

# Check Ollama API
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    log_info "  ✓ Ollama API: Responding"
else
    log_warn "  ⚠ Ollama API: Not responding (start with: ollama serve)"
fi

# Summary
echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Clone OpenClaw Deployer:"
echo "     git clone https://github.com/0x-wzw/OpenClaw_deployer_for_dummies.git"
echo ""
echo "  2. Run the installer:"
echo "     cd OpenClaw_deployer_for_dummies"
echo "     ./install.sh"
echo ""
echo "  3. Start using OpenClaw:"
echo "     openclaw --version"
echo ""
echo "Workspace: ~/.openclaw/workspace"
echo "Config: ~/.openclaw/openclaw.json"
echo ""
log_info "System ready for OpenClaw!"
