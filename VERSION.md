# Version History

## Current Version: 2.0.0

**Release Date:** 2026-06-07

### What's New in 2.0.0

- ✅ Updated README for latest OpenClaw (2026.6.1)
- ✅ Strengthened `.gitignore` against credential leaks
- ✅ Recommended modern local models (qwen2.5:7b, llama3.2:3b)
- ✅ Added advanced config upgrade path
- ✅ Updated template configs (`SOUL.md`, `AGENTS.md`, `USER.md`, `HEARTBEAT.md`)
- ✅ Simplified update process
- ✅ Fixed Ollama port typo in example config

---

## Changelog

### 2.0.0 (2026-06-07)

#### Added
- Security section with credential management best practices
- Advanced config upgrade path linking to companion repo
- Lock-tight `.gitignore` covering `.env`, `*.key`, `*.pem`, secrets directories
- Personality-rich `SOUL.md` template for single-agent-first workflows

#### Changed
- Recommended models: qwen2.5:7b (was 3b), llama3.2:3b (was phi3)
- OpenClaw install instruction is now version-agnostic (`npm install -g openclaw`)
- `UPDATE.md` simplified to a concise git-pull & check-VERSION.md process
- Config templates refreshed with cleaner defaults

#### Fixed
- Ollama port `localhost:114114` → `localhost:11434` in example config

#### Removed
- Bloated weekly update process from `UPDATE.md`
- Swarm Protocol references from template `AGENTS.md` (single-agent-first)

### 1.0.0 (2026-03-22)

#### Added
- Initial release
- Ollama-first setup (no API keys)
- Automated installation script
- Local model support (qwen2.5:3b, phi3)
- Extension integration
- Version tracking
- Weekly update process

---

## Update Instructions

```bash
git pull origin main
cat VERSION.md    # review changes
```

See [UPDATE.md](UPDATE.md) for details.

---

## Versioning Scheme

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backwards compatible
- **PATCH** (0.0.X): Bug fixes, backwards compatible

---

## Roadmap

### 2.1.0 (Planned)
- [ ] GPU acceleration guide
- [ ] Docker deployment option
- [ ] Windows setup guide
- [ ] Automated health check script

### 2.2.0 (Planned)
- [ ] Web UI integration
- [ ] Community skill templates
- [ ] Testing suite

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-change`
3. Update `VERSION.md` with your changes
4. Submit a pull request

---

*Version tracking for OpenClaw Deployer for Dummies*