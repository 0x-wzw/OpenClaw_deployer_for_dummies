# OpenClaw Deployer for Dummies 🦞

> **Get OpenClaw running with local Ollama in minutes — no API keys, no cloud, fully private.**

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](VERSION.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Ollama](https://img.shields.io/badge/ollama-first-orange.svg)](https://ollama.com)

---

## What Is This?

A **beginner-friendly, step-by-step guide** to installing and running **OpenClaw** with **local Ollama models**. Zero API keys. Zero cloud dependencies. Fully private, fully local AI agents.

**Perfect for:**
- First-time OpenClaw users
- Privacy-conscious developers
- Anyone avoiding API costs
- Building local AI agent infrastructure on your own machine

---

## Quick Start (5 Minutes)

```bash
# 1. Clone this repo
git clone https://github.com/0x-wzw/OpenClaw_deployer_for_dummies.git
cd OpenClaw_deployer_for_dummies

# 2. Run the installer
chmod +x install.sh && ./install.sh

# 3. Verify it works
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

*Missing something? The installer will walk you through it.*

---

## What You Get

### Components

| Component | Purpose | Runs Locally? |
|-----------|---------|:------:|
| **Ollama** | Local LLM runner | ✅ |
| **OpenClaw** | Agent orchestration framework | ✅ |
| **Qwen 2.5 7B** | General-purpose model (strong reasoning) | ✅ |
| **Llama 3.2 3B** | Lightweight fast model | ✅ |

### Configuration Files

| File | Purpose |
|------|---------|
| `config/SOUL.md` | Agent identity and persona |
| `config/USER.md` | Your preferences (fill it in!) |
| `config/AGENTS.md` | Workspace and agent setup |
| `config/HEARTBEAT.md` | Autonomous maintenance schedule |

---

## Step-by-Step Manual Setup

### 1. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
```

**Verify:** `curl http://localhost:11434/api/tags`

### 2. Pull Models

```bash
# Recommended general-purpose (strong reasoning, 32K context)
ollama pull qwen2.5:7b

# Lightweight fast model
ollama pull llama3.2:3b
```

**Verify:** `ollama list`

### 3. Install OpenClaw

```bash
npm install -g openclaw
```

**Verify:** `openclaw --version`

### 4. Configure OpenClaw

Create `~/.openclaw/openclaw.json`:

```json
{
  "version": "2.0.0",
  "mode": "ollama-first",
  "models": {
    "providers": {
      "ollama": {
        "host": "http://localhost:11434",
        "models": [
          {
            "id": "qwen2.5:7b",
            "name": "Qwen 2.5 7B",
            "contextWindow": 32768
          },
          {
            "id": "llama3.2:3b",
            "name": "Llama 3.2 3B",
            "contextWindow": 8192
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": "ollama/qwen2.5:7b"
    }
  }
}
```

> **Note:** The example above had a typo (`localhost:114114`) in v1.0.0. The correct Ollama port is **11434**.

### 5. Create Your Workspace

```bash
mkdir -p ~/.openclaw/workspace/skills
cd ~/.openclaw/workspace
cp /path/to/OpenClaw_deployer_for_dummies/config/*.md .
```

### 6. Test the Setup

```bash
openclaw --version
openclaw status
```

---

## Security

### 🔐 Credential Management

For production setups, DO NOT hardcode API keys in config files.
Use `.env` (chmod 600) loaded via `EnvironmentFile=-` in systemd,
or use the vault management pattern documented in the 
[advanced-config repo](<https://github.com/0x-wzw/openclaw-advanced-config>).

### Credential Safety

This guide is built around **zero external API keys**. Everything runs locally. That said:

- **Never commit `.env` files, `*.pem`, `*.key`, or credential files** — the `.gitignore` in this repo explicitly blocks them.
- **Verify before every push:** run `git status` and check no `.env` or key files appear.
- **Use environment variables** for any tokens you do add later (e.g., `$OPENAI_API_KEY` set in your shell profile, not in a tracked file).
- **Keep your Ollama server local** — do not expose port 11434 to the public internet.

### File Permissions

```bash
# Sensible defaults for your OpenClaw workspace
chmod 700 ~/.openclaw
chmod 600 ~/.openclaw/openclaw.json
```

---

## Troubleshooting

### Ollama Not Responding

```bash
curl http://localhost:11434/api/tags
# Not working? Start it:
ollama serve
# macOS:
launchctl start com.ollama.ollama
```

### Model Download Fails

```bash
ollama pull qwen2.5:7b --verbose
df -h   # check disk space (models are several GB)
```

### OpenClaw Not Found

```bash
npm config get prefix
export PATH="$PATH:$(npm config get prefix)/bin"
# Then add that line to your ~/.bashrc or ~/.zshrc
```

---

## 🚀 Ready for More? Check Out the Advanced Config

Set up with this guide and want to take it further?

The **[OpenClaw Advanced Config](https://github.com/0x-wzw/openclaw-advanced-config)** repo gives you:

- Multi-model routing (Ollama + cloud providers)
- Production-grade `AGENTS.md` and `SOUL.md`
- Pre-configured skills and MCP servers
- Security hardening and observability
- Ready-to-use `openclaw.json` with best practices

> **Note:** This is a **private companion repo** — clone it into `~/.openclaw` after you've completed the basic setup here.

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| **2.0.0** | 2026-06-07 | Updated models, tighter security, advanced upgrade path |
| **1.0.0** | 2026-03-22 | Initial release |

See [VERSION.md](VERSION.md) for the full changelog.

---

## Contributing

1. Fork the repo
2. Make your improvements
3. Submit a pull request
4. Update `VERSION.md` with your changes

---

## License

MIT — see [LICENSE](LICENSE)

---

## Support

- **Issues:** [GitHub Issues](https://github.com/0x-wzw/OpenClaw_deployer_for_dummies/issues)
- **Updates:** `git pull origin main`

---

*Made with 🦞 by Z Teoh / October (10D Entity)*  
*Part of the 0x-wzw open-source ecosystem*