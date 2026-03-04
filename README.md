# Open Claw Deployer for Dummies

This repository contains an automatic deployment script and a custom Python implementation of an **Open Claw** autonomous AI agent. It has been built and upgraded to support the **Model Context Protocol (MCP)**, allowing the agent to dynamically load tools and connect to secure external data sources.

## Features

- **Automatic Environment Setup**: The `auto_deploy.sh` script installs Python 3.10+ (using Homebrew on macOS if needed), initializes virtual environments, and installs required Python packages.
- **Node.js Management**: Automatically installs Node.js via `nvm` if it is missing, which is required for running standard MCP servers.
- **MCP Integration**: Uses the official `mcp` Python SDK to connect the agent core dynamically to MCP servers (like `@modelcontextprotocol/server-filesystem` and `@modelcontextprotocol/server-sqlite`).
- **Interactive CLI**: Chat directly with your agent in the terminal. The agent will orchestrate tools autonomously to fulfill your requests.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/0x-wzw/OpenClaw_deployer_for_dummies.git
cd OpenClaw_deployer_for_dummies
```

### 2. Configure Your API Key

1.  Open the `config.py` file.
2.  Replace `"your-api-key-here"` with your actual OpenAI, Anthropic, or compatible API key.
3.  (Optional) You can customize the model being used by editing the `MODEL_NAME` variable.

### 3. Run the Auto-Deployer

The auto-deployer handles configuring the environment and spinning up the MCP definitions in `mcp_config.json`.

```bash
./auto_deploy.sh
```

### 4. Start the Agent

Once deployment finishes, you can start chatting with your Open Claw instance:

```bash
source venv/bin/activate
python main.py
```

## How It Works

1.  **`mcp_config.json`** acts as the blueprint for the systems the agent can access. You can add more MCP servers (e.g., GitHub, Google Drive integrations) here.
2.  **`agent/core.py`** initializes an async loop that connects to these servers, transforms their tools into a schema the LLM understands, and manages the back-and-forth conversation and tool execution.
