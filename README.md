# Azure Kubernetes Credential Loader

A CLI tool that automatically discovers all AKS clusters across your Azure subscriptions and fetches their credentials for kubectl access.

## Features

- Automatically discovers all Azure subscriptions you have access to
- Finds all AKS clusters in each subscription
- Fetches credentials for each cluster using `az aks get-credentials`
- Converts kubeconfig to use Azure CLI authentication with `kubelogin`
- Supports dry-run mode to preview actions
- Comprehensive logging and error handling

## Prerequisites

- Azure CLI (`az`) installed and authenticated
- `kubelogin` installed for Azure authentication
- Python 3.6+ (if using the Python version)

## Installation

### Install kubelogin
```bash
# macOS
brew install Azure/kubelogin/kubelogin

# Or download from https://github.com/Azure/kubelogin/releases
```

### Install Azure CLI
```bash
# macOS
brew install azure-cli
```

## Usage

### Basic usage - fetch credentials for all clusters
```bash
./aks-credential-loader
```

### Dry run - preview what would be executed
```bash
./aks-credential-loader --dry-run
```

### Target specific subscription(s)
```bash
./aks-credential-loader --subscription 12345678-1234-1234-1234-123456789abc
```

### Verbose output
```bash
./aks-credential-loader --verbose
```

## What it does

For each AKS cluster found, the tool executes:
1. `az account set --subscription <subscription-id>`
2. `az aks get-credentials --resource-group <rg-name> --name <cluster-name> --overwrite-existing`
3. `kubelogin convert-kubeconfig -l azurecli`

## Output

The tool will update your `~/.kube/config` file with contexts for all discovered AKS clusters, ready for use with `kubectl`.

## 🚀 Quick Start

### 1. Install Prerequisites

```bash
# macOS with Homebrew
brew install azure-cli
brew install Azure/kubelogin/kubelogin
brew install jq

# Login to Azure
az login
```

### 2. Clone and Use

```bash
git clone <repo-url>
cd azure-kubernetes-crdential-loader

# Test with dry-run first (recommended)
./aks-credential-loader --dry-run --verbose

# Run for real
./aks-credential-loader --verbose
```

## 📖 Usage

### Bash Version (Recommended)

```bash
# Preview what would be executed (always run this first!)
./aks-credential-loader --dry-run --verbose

# Fetch credentials for all clusters
./aks-credential-loader

# Target specific subscription(s)
./aks-credential-loader --subscription 12345678-1234-1234-1234-123456789abc

# Multiple subscriptions
./aks-credential-loader -s sub1 -s sub2

# Verbose output
./aks-credential-loader --verbose
```

### Python Version

```bash
# Preview what would be executed
./aks-credential-loader --dry-run --verbose

# Fetch credentials for all clusters
./aks-credential-loader

# Target specific subscription
./aks-credential-loader --subscription 12345678-1234-1234-1234-123456789abc
```

## ⚙️ What It Does

For each AKS cluster discovered, the tool executes these three commands:

1. **Set subscription context:**
   ```bash
   az account set --subscription <subscription-id>
   ```

2. **Fetch AKS credentials:**
   ```bash
   az aks get-credentials --resource-group <rg-name> --name <cluster-name> --overwrite-existing
   ```

3. **Convert to Azure CLI authentication:**
   ```bash
   kubelogin convert-kubeconfig -l azurecli
   ```

## 📊 Example Output

```
🔧 Checking prerequisites...
✅ Azure CLI found
✅ kubelogin found
✨ Ready to go!

======================================================================
🚀 Azure Kubernetes Credential Loader
======================================================================

🚀 Starting Azure Kubernetes Credential Loader
🔍 Finding your Azure subscriptions...
📋 Found 26 subscription(s)
   • mock-subscription-01
   • prod-sub

============================================================
🏢 mock-subscription-01
============================================================
🔎 Looking for AKS clusters...
🎯 Found 2 cluster(s):
     mock-aks-cluster-01
     e-n-shr-aks-01

🔑 Getting credentials for: mock-aks-cluster-01
✅ Ready: mock-aks-cluster-01

============================================================
📊 Summary
============================================================
Subscriptions: 26
Clusters found: 22
Configured: 22/22
🎉 All clusters ready to use!
```

## 🏃 Results

- ✅ Updates your `~/.kube/config` file with contexts for all discovered AKS clusters
- ✅ All clusters ready for use with `kubectl`
- ✅ Switch between clusters: `kubectl config use-context <cluster-name>`
- ✅ List all contexts: `kubectl config get-contexts`

## 🛠️ Available Commands

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview actions without executing them |
| `--verbose`, `-v` | Enable detailed logging |
| `--subscription`, `-s` | Process specific subscription(s) only |
| `--help`, `-h` | Show help message |

## 🔧 Makefile Commands

```bash
make help           # Show available commands
make install        # Install prerequisites via Homebrew
make check-prereqs  # Verify all tools are installed
make test           # Test both versions with dry-run
make dry-run        # Run Python version in dry-run mode
make run            # Run Python version
make clean          # Clean up temporary files
```

## 🐛 Troubleshooting

### Common Issues

**"Not logged in to Azure CLI"**
```bash
az login
```

**"kubelogin not found"**
```bash
brew install Azure/kubelogin/kubelogin
```

**"jq not found" (Bash version)**
```bash
brew install jq
```

**"Failed to set subscription context"**
- You may not have access to all listed subscriptions
- Use `--subscription` to target specific subscriptions you have access to

### Debug Mode

Always test with dry-run first:
```bash
./aks-credential-loader --dry-run --verbose
```

## 📁 Project Structure

```
├── README.md                           # This documentation
├── aks-credential-loader               # Main CLI entry point
├── src/
│   └── aks_credential_loader.py        # Core Python implementation
├── scripts/
│   ├── aks_credential_loader.sh        # Bash implementation
│   └── run_tests.sh                    # Test runner
├── tests/                              # Comprehensive test suite
├── docs/
│   ├── EXAMPLES.md                     # Usage examples
│   └── PROJECT_STRUCTURE.md            # Detailed project structure
├── CONTRIBUTING.md                     # Contribution guidelines
├── SECURITY.md                         # Security policy
├── CHANGELOG.md                        # Version history
├── pyproject.toml                      # Modern Python packaging
├── Makefile                            # Development commands
├── .vscode/                            # VS Code configuration
├── .devcontainer/                      # Development container setup
└── .github/                            # GitHub Actions and templates
```

## 👩‍💻 Development

### GitHub Codespaces (Recommended)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/YOUR_USERNAME/azure-kubernetes-crdential-loader)

1. Click the badge above or "Code" → "Codespaces" → "Create codespace"
2. Wait for automatic setup (Azure CLI, kubectl, kubelogin pre-installed)
3. Start coding with GitHub Copilot enabled!

### Local Development
```bash
git clone <repo-url>
cd azure-kubernetes-crdential-loader
code .  # Opens with full VS Code configuration
make install  # Install prerequisites
```

### Dev Container
Open in VS Code and use "Dev Containers: Reopen in Container" for a consistent development environment.

## 🤖 GitHub Copilot

This project is optimized for GitHub Copilot development! See [.github/copilot-instructions.md](.github/copilot-instructions.md) for:
- AI-powered development workflows
- Copilot best practices for this project
- Prompt examples for common tasks
- Advanced techniques and tips

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup instructions
- Code style guidelines
- Pull request process
- GitHub Copilot usage tips

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
