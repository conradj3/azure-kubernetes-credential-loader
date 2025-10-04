#!/bin/bash

# Post-create setup script for the development container
set -e

echo "🚀 Setting up Azure Kubernetes Credential Loader development environment..."

# Install kubelogin
echo "📦 Installing kubelogin..."
curl -LO "https://github.com/Azure/kubelogin/releases/latest/download/kubelogin-linux-amd64.zip"
unzip kubelogin-linux-amd64.zip
sudo mv bin/linux_amd64/kubelogin /usr/local/bin/
rm -rf kubelogin-linux-amd64.zip bin/

# Install jq (if not already installed)
if ! command -v jq &> /dev/null; then
    echo "📦 Installing jq..."
    sudo apt-get update && sudo apt-get install -y jq
fi

# Make scripts executable
echo "🔧 Setting up executable permissions..."
chmod +x aks_credential_loader.py
chmod +x aks_credential_loader.sh

# Install Python development dependencies
echo "🐍 Installing Python development tools..."
pip install --upgrade pip
pip install pylint black

# Verify installations
echo "✅ Verifying installations..."
echo "Python: $(python3 --version)"
echo "Azure CLI: $(az --version | head -n1)"
echo "kubectl: $(kubectl version --client --short 2>/dev/null || echo 'kubectl installed')"
echo "kubelogin: $(kubelogin --version)"
echo "jq: $(jq --version)"

# Set up git (if in codespace)
if [ -n "$CODESPACE_NAME" ]; then
    echo "🔧 Configuring git for GitHub Codespaces..."
    git config --global --add safe.directory /workspaces/*
fi

echo "🎉 Development environment setup complete!"
echo ""
echo "💡 Next steps:"
echo "   1. Run 'az login' to authenticate with Azure"
echo "   2. Use 'make check-prereqs' to verify everything is working"
echo "   3. Try 'python3 aks_credential_loader.py --dry-run' to test the tool"
echo ""
echo "🤖 GitHub Copilot is enabled for this workspace!"
echo "   Use Ctrl+I for inline suggestions and Ctrl+Shift+I for chat"
