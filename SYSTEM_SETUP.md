# Ubuntu System Setup Guide

> **Prepare your Ubuntu Linux environment for Ollama and OpenClaw**

## Supported Versions

- Ubuntu 20.04 LTS (Focal Fossa)
- Ubuntu 22.04 LTS (Jammy Jellyfish)
- Ubuntu 24.04 LTS (Noble Numbat)

---

## Quick Setup (One Command)

```bash
# Download and run the system setup script
curl -fsSL https://raw.githubusercontent.com/0x-wzw/OpenClaw_deployer_for_dummies/main/scripts/ubuntu-setup.sh | bash
```

---

## Manual Step-by-Step Setup

### Step 1: Update System

```bash
# Update package lists
sudo apt update

# Upgrade existing packages
sudo apt upgrade -y

# Install essential build tools
sudo apt install -y build-essential curl wget git jq
```

### Step 2: Install Node.js 18+

OpenClaw requires Node.js 18 or higher.

```bash
# Install Node.js via NodeSource
 curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version  # Should show v18.x.x or higher
npm --version
```

**Alternative: Using NVM (Node Version Manager)**

```bash
# Install NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Reload shell
source ~/.bashrc

# Install Node.js 18
nvm install 18
nvm use 18

# Verify
node --version
```

### Step 3: Install Python 3 and pip

```bash
# Install Python
sudo apt install -y python3 python3-pip python3-venv

# Verify
python3 --version  # Should show 3.8+
```

### Step 4: Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Add Ollama to PATH (if not already)
export PATH="$PATH:/usr/local/bin"

# Start Ollama service
ollama serve

# Verify (in another terminal)
curl http://localhost:11434/api/tags
```

**Systemd Service (Optional)**

```bash
# Create systemd service for Ollama
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

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama

# Check status
sudo systemctl status ollama
```

### Step 5: Pull Required Models

```bash
# Pull Qwen 2.5 3B (general purpose, 32K context)
ollama pull qwen2.5:3b

# Pull Phi-3 (fast, 4K context)
ollama pull phi3

# Verify models
ollama list
```

### Step 6: Configure Ollama for Remote Access (Optional)

If you want to access Ollama from other machines:

```bash
# Set environment variable
export OLLAMA_HOST=0.0.0.0

# Or modify systemd service
sudo systemctl edit ollama.service

# Add to [Service] section:
# [Service]
# Environment="OLLAMA_HOST=0.0.0.0"

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### Step 7: Install OpenClaw

```bash
# Install OpenClaw globally
sudo npm install -g openclaw

# Verify installation
openclaw --version
```

### Step 8: Create Workspace Directory

```bash
# Create OpenClaw workspace
mkdir -p ~/.openclaw/workspace
mkdir -p ~/.openclaw/workspace/skills
mkdir -p ~/.openclaw/workspace/memory

# Set permissions
chmod -R u+rw ~/.openclaw
```

### Step 9: Configure OpenClaw for Ollama

Create `~/.openclaw/openclaw.json`:

```bash
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
```

### Step 10: Install Additional Tools (Optional)

```bash
# Install GitHub CLI (for repo management)
sudo apt install -y gh

# Install Docker (for containerized deployments)
sudo apt install -y docker.io
sudo usermod -aG docker $USER

# Install tmux (for session management)
sudo apt install -y tmux

# Install htop (system monitoring)
sudo apt install -y htop
```

---

## Firewall Configuration

If using UFW (Uncomplicated Firewall):

```bash
# Allow Ollama port
sudo ufw allow 11434/tcp

# Allow OpenClaw gateway port (if needed)
sudo ufw allow 18790/tcp

# Check status
sudo ufw status
```

---

## GPU Acceleration (Optional)

If you have an NVIDIA GPU:

```bash
# Install NVIDIA drivers (if not already installed)
sudo apt install -y nvidia-driver-535

# Install CUDA toolkit (for GPU acceleration)
sudo apt install -y nvidia-cuda-toolkit

# Verify
nvidia-smi

# Ollama will automatically use GPU if available
```

---

## Verification

Run the verification script:

```bash
# Check all components
echo "=== System Verification ==="
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"
echo "Python3: $(python3 --version)"
echo "Ollama: $(ollama --version 2>&1 || echo 'Not found')"
echo "OpenClaw: $(openclaw --version 2>&1 || echo 'Not found')"
echo "Git: $(git --version)"
echo "jq: $(jq --version)"

# Check Ollama API
 curl -s http://localhost:11434/api/tags >/dev/null && echo "Ollama API: OK" || echo "Ollama API: Not responding"

# Check disk space
df -h ~/.openclaw
```

---

## Troubleshooting

### Issue: Node.js installation fails

```bash
# Alternative: Install via snap
sudo snap install node --classic

# Or download binary
curl -fsSL https://nodejs.org/dist/v18.17.0/node-v18.17.0-linux-x64.tar.xz | tar -xJf -
sudo cp -r node-v18.17.0-linux-x64/{bin,lib,share} /usr/local/
```

### Issue: Ollama permission denied

```bash
# Fix permissions
sudo chown -R $USER:$USER /usr/local/bin/ollama
sudo chmod +x /usr/local/bin/ollama
```

### Issue: Port 11434 already in use

```bash
# Find and kill process
sudo lsof -i :11434
sudo kill -9 <PID>

# Or use different port
export OLLAMA_PORT=11435
ollama serve
```

### Issue: Out of disk space

```bash
# Clean up
sudo apt clean
sudo apt autoremove

# Check large files
du -sh ~/.openclaw/*
du -sh /usr/share/ollama
```

---

## Next Steps

After system setup:

1. **Run the OpenClaw installer:**
   ```bash
   git clone https://github.com/0x-wzw/OpenClaw_deployer_for_dummies.git
   cd OpenClaw_deployer_for_dummies
   ./install.sh
   ```

2. **Start using OpenClaw:**
   ```bash
   openclaw --version
   openclaw status
   ```

3. **See main README for usage:**
   [README.md](README.md)

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 4 GB | 8+ GB |
| **Disk** | 10 GB free | 50+ GB free |
| **GPU** | Optional | NVIDIA with 8GB+ VRAM |
| **OS** | Ubuntu 20.04 | Ubuntu 22.04+ |

---

*System setup guide for Ubuntu Linux*  
*Part of OpenClaw Deployer for Dummies*  
*Version: 1.0.0*
