#!/bin/bash
set -e

# =========================================================================
# Open Claw - Automatic Deployer
# =========================================================================

echo "🚀 Starting Open Claw Automatic Deployment..."

# 1. Ensure Python 3.10+ Virtual Environment is active or created
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    
    # Check for python3.10 or python3.11
    PYTHON_CMD=""
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
    elif command -v python3.10 &> /dev/null; then
        PYTHON_CMD="python3.10"
    else
        echo "⚠️ Python 3.10+ is required for the MCP SDK. Attempting to install via Homebrew..."
        BREW_CMD=""
        if command -v brew &> /dev/null; then BREW_CMD="brew";
        elif [ -x "/opt/homebrew/bin/brew" ]; then BREW_CMD="/opt/homebrew/bin/brew";
        elif [ -x "/usr/local/bin/brew" ]; then BREW_CMD="/usr/local/bin/brew";
        fi
        
        if [ -n "$BREW_CMD" ]; then
            $BREW_CMD install python@3.11
            PYTHON_CMD="$($BREW_CMD --prefix)/opt/python@3.11/bin/python3"
        else
            echo "❌ Error: Python 3.10+ not found and Homebrew is not installed."
            echo "   Please install Python 3.11 manually to continue."
            exit 1
        fi
    fi
    
    echo "Using python executable: $PYTHON_CMD"
    $PYTHON_CMD -m venv venv
else
    echo "✅ Python virtual environment already exists."
fi

# 2. Activate virtual environment and install dependencies
echo "⬇️ Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt --quiet
echo "✅ Python dependencies installed."

# 3. Check for Node.js (Required for standard Anthropic MCPs like filesystem/sqlite)
if ! command -v node &> /dev/null; then
    echo "⚠️ Node.js is not installed. Many standard MCP servers require Node."
    echo "   Attempting to install Node.js via nvm..."
    if [ ! -d "$HOME/.nvm" ]; then
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    fi
    source $HOME/.nvm/nvm.sh
    nvm install 20
    nvm use 20
else
    echo "✅ Node.js is installed ($(node -v))."
fi

# 4. Check API Key
if grep -q "your-api-key-here" config.py 2>/dev/null; then
    echo "⚠️  WARNING: You haven't set an OPENAI_API_KEY in config.py yet."
    echo "   Please edit config.py before running the agent."
fi

echo ""
echo "🎉 Deployment successful!"
echo "   To start your MCP-enabled Open Claw agent, run:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo "========================================================================="
