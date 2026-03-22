# Version History

## Current Version: 1.0.0

**Release Date:** 2026-03-22

### What's New in 1.0.0

- ✅ Initial release
- ✅ Ollama-first setup (no API keys)
- ✅ Automated installation script (`install.sh`)
- ✅ Local model support (qwen2.5:3b, phi3)
- ✅ Extension integration (SentientForge, SovereignStack, Swarm Agent Kit)
- ✅ Version-controlled updates
- ✅ Weekly update process

---

## Changelog

### 1.0.0 (2026-03-22)

#### Added
- Complete first-time setup guide
- Automated installation script
- Ollama integration
- Local model configuration
- Extension linking system
- Version tracking
- Update mechanism

#### Changed
- N/A (initial release)

#### Deprecated
- N/A (initial release)

#### Removed
- N/A (initial release)

#### Fixed
- N/A (initial release)

---

## Update Instructions

### Automatic Update

```bash
# Pull latest changes
git pull origin main

# Run update script
./update.sh
```

### Manual Update

1. Check [VERSION.md](VERSION.md) for latest version
2. Review [UPDATE.md](UPDATE.md) for changes
3. Backup your config: `cp -r ~/.openclaw ~/.openclaw.backup`
4. Apply updates per instructions in UPDATE.md
5. Verify: `openclaw --version`

---

## Versioning Scheme

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backwards compatible
- **PATCH** (0.0.X): Bug fixes, backwards compatible

---

## Roadmap

### 1.1.0 (Planned)
- [ ] Additional Ollama models (llama3, mistral)
- [ ] GPU acceleration guide
- [ ] Docker deployment option
- [ ] Windows support

### 1.2.0 (Planned)
- [ ] Web UI for configuration
- [ ] Plugin marketplace
- [ ] Community skill sharing
- [ ] Automated testing suite

### 2.0.0 (Future)
- [ ] Multi-instance federation
- [ ] Cloud-native deployment
- [ ] Enterprise features

---

## Contributing to Versions

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/1.1.0-my-feature`
3. Update VERSION.md with your changes
4. Update CHANGELOG in UPDATE.md
5. Submit a pull request

---

*Version tracking for OpenClaw Deployer for Dummies*  
*Updated weekly — see UPDATE.md for process*
