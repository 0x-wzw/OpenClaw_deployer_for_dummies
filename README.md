# OpenClaw Deployer for Dummies 🦞

> **First-time OpenClaw setup with Ollama — no API keys required.**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](VERSION.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Ollama](https://img.shields.io/badge/ollama-first-orange.svg)](https://ollama.com)

## What is This?

A **beginner-friendly, step-by-step guide** to set up OpenClaw with **local Ollama models** — no API keys, no cloud dependencies, fully private.

**Perfect for:**
- First-time OpenClaw users
- Privacy-conscious developers
- Those who want to avoid API costs
- Anyone building local AI agent infrastructure

---

## Quick Start (5 Minutes)

```bash
# 1. Clone this repo
git clone https://github.com/0x-wzw/OpenClaw_deployer_for_dummies.git
cd OpenClaw_deployer_for_dummies

# 2. Run the installer
chmod +x install.sh
./install.sh

# 3. Start using OpenClaw
openclaw --version
```

---

## Prerequisites

| Requirement | Version | Check |
|-------------|---------|-------|
| **OS** | Linux or macOS | `uname -a` |
| **Node.js** | 18+ | `node --version` |
| **Git** | Any | `git --version` |
| **curl** | Any | `curl --version` |
| **jq** | Any | `jq --version` |

**Don't have these?** The installer will guide you.

---

## What Gets Installed?

### Core Components
| Component | Purpose | Local? |
|-------------|---------|--------|
| **Ollama** | Local LLM runner | ✅ Yes |
| **OpenClaw** | Agent orchestration | ✅ Yes |
| **Qwen 2.5 3B** | General-purpose model | ✅ Yes |
| **Phi-3** | Fast classification | ✅ Yes |

### Configuration Files
| File | Purpose |
|------|---------|
| `SOUL.md` | Agent identity/persona |
| `USER.md` | Your preferences |
| `AGENTS.md` | Multi-agent setup |
| `HEARTBEAT.md` | Maintenance schedule |

### Extensions (Optional)
| Extension | Description | Link |
|-----------|-------------|------|
| **SentientForge** | ACS optimization | [GitHub](https://github.com/0x-wzw/sentientforge) |
| **SovereignStack** | Swarm orchestration | [GitHub](https://github.com/0x-wzw/sovereignstack) |
| **Swarm Agent Kit** | Agent tools | [GitHub](https://github.com/0x-wzw/swarm-agent-kit) |

---

## Step-by-Step Manual Setup

### Step 1: Install Ollama

```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama
ollama serve
```

**Verify:** `curl http://localhost:11434/api/tags`

### Step 2: Pull Models

```bash
# General-purpose model (32K context)
ollama pull qwen2.5:3b

# Fast model for simple tasks (4K context)
ollama pull phi3
```

**Verify:** `ollama list`

### Step 3: Install OpenClaw

```bash
npm install -g openclaw
```

**Verify:** `openclaw --version`

### Step 4: Configure OpenClaw

Create `~/.openclaw/openclaw.json`:

```json
{
  "version": "1.0.0",
  "mode": "ollama-first",
  "models": {
    "providers": {
      "ollama": {
        "host": "http://localhost:114114",
        "models": [
          {
            "id": "qwen2.5:3b",
            "name": "Qwen 2.5 3B",
            "contextWindow": 32000
          },
          {
            "id": "phi3",
            "name": "Phi-3",
            "contextWindow": 4000
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": "ollama/qwen2.5:3b"
    }
  }
}
```

### Step 5: Create Workspace

```bash
mkdir -p ~/.openclaw/workspace/skills
cd ~/.openclaw/workspace

# Copy templates from this repo
cp /path/to/OpenClaw_deployer_for_dummies/config/SOUL.md .
cp /path/to/OpenClaw_deployer_for_dummies/config/USER.md .
cp /path/to/OpenClaw_deployer_for_dummies/config/AGENTS.md .
cp /path/to/OpenClaw_deployer_for_dummies/config/HEARTBEAT.md .
```

### Step 6: Test

```bash
openclaw --version
openclaw status
```

---

## Troubleshooting

### Ollama Not Responding

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve

# Or on macOS
launchctl start com.ollama.ollama
```

### Model Download Fails

```bash
# Retry with verbose output
ollama pull qwen2.5:3b --verbose

# Check disk space
df -h
```

### OpenClaw Not Found

```bash
# Check npm global path
npm config get prefix

# Add to PATH if needed
export PATH="$PATH:$(npm config get prefix)/bin"
```

### Permission Denied

```bash
# Fix permissions
chmod +x install.sh
chmod -R u+rw ~/.openclaw
```

---

## Extensions & Customization

### Install SentientForge (ACS Optimization)

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/0x-wzw/sentientforge.git
```

### Install SovereignStack (Swarm Orchestration)

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/0x-wzw/sovereignstack.git
```

### Install Swarm Agent Kit

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/0x-wzw/swarm-agent-kit.git
```

---

## Weekly Updates

This guide is updated weekly with improvements.

**To check for updates:**
```bash
cd /path/to/OpenClaw_deployer_for_dummies
git pull origin main
./update.sh
```

**See [UPDATE.md](UPDATE.md) for detailed update process.**

---

## Version History

See [VERSION.md](VERSION.md) for changelog.

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-22 | Initial release |

---

## Contributing

1. Fork the repo
2. Make improvements
3. Submit PR
4. Include change log entry

---

## License

MIT — See [LICENSE](LICENSE)

---

## Support

- **Issues:** [GitHub Issues](https://github.com/0x-wzw/OpenClaw_deployer_for_dummies/issues)
- **Extensions:** See individual repo READMEs
- **Updates:** Run `./update.sh` weekly

---

*Made with 🦞 by Z Teoh / October (10D Entity)*  
*Part of the 0x-wzw Swarm Ecosystem* 
