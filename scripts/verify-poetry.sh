#!/bin/bash
# This script verifies Poetry installation and PATH configuration

# Print environment information
echo "Verifying development environment..."
echo "-----------------------------------"
echo "PATH = $PATH"
echo "USER = $(whoami)"
echo "PWD = $(pwd)"
echo

# Check if basic commands are available
echo "Testing basic commands:"
command -v ls && echo "✅ ls found" || echo "❌ ls not found"
command -v make && echo "✅ make found" || echo "❌ make not found"
command -v python3 && echo "✅ python3 found" || echo "❌ python3 not found"
command -v pip && echo "✅ pip found" || echo "❌ pip not found"
echo

# Check Python version
echo "Python version:"
python3 --version
echo

# Check Poetry installation
echo "Checking Poetry installation:"
if command -v poetry &>/dev/null; then
    echo "✅ Poetry is installed:"
    poetry --version
    echo "Poetry location: $(which poetry)"
else
    echo "❌ Poetry not found in PATH"
    echo "Attempting emergency installation..."
    python3 -m pip install --user poetry
    export PATH="$HOME/.local/bin:$PATH"
    if command -v poetry &>/dev/null; then
        echo "✅ Emergency installation successful:"
        poetry --version
        echo "Adding Poetry to PATH permanently..."
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.profile
    else
        echo "❌ Emergency installation failed"
        echo "Please install Poetry manually"
    fi
fi
echo

# Check project installation
echo "Checking project installation:"
if [ -f "pyproject.toml" ]; then
    echo "✅ pyproject.toml found"
    if poetry show &>/dev/null; then
        echo "✅ Dependencies are installed"
    else
        echo "⚠️ Dependencies not installed. Running installation..."
        poetry install
    fi
else
    echo "❌ pyproject.toml not found. Are you in the right directory?"
fi
echo

echo "Verification complete."
