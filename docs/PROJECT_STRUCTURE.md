# Azure Kubernetes Credential Loader

Expert-level Python project structure for automated AKS credential management.

## 📁 Project Structure

```
azure-kubernetes-credential-loader/
├── src/                                 # 🐍 Source code
│   ├── __init__.py                     # Package initialization
│   └── aks_credential_loader.py        # Main Python implementation
├── tests/                               # 🧪 Test suite
│   ├── __init__.py                     # Test package initialization
│   ├── conftest.py                     # Pytest configuration and fixtures
│   ├── test_simple.py                  # Basic functionality tests
│   ├── test_isolated.py                # Comprehensive isolated tests
│   └── test_aks_credential_loader.py   # Full integration tests
├── scripts/                             # 📜 Shell scripts and utilities
│   ├── aks_credential_loader.sh        # Bash implementation
│   └── run_tests.sh                    # Test runner with system access
├── docs/                                # 📚 Documentation
│   ├── EXAMPLES.md                     # Usage examples
│   └── PROJECT_STRUCTURE.md            # This file
├── .devcontainer/                       # 🐳 Development container setup
├── .github/                             # 🤖 GitHub Actions CI/CD
│   └── copilot-instructions.md         # GitHub Copilot development guide
├── .vscode/                             # 🎯 VS Code configuration
├── aks-credential-loader                # 🚀 CLI entry point script
├── pyproject.toml                       # 📦 Modern Python packaging
├── pyrightconfig.json                   # 🔍 Type checking configuration
├── requirements.txt                     # 📋 Runtime dependencies (none)
├── requirements-test.txt                # 🧪 Test dependencies
├── pytest.ini                          # ⚙️ pytest configuration
├── .bandit                              # 🔒 Security scanning configuration
├── Makefile                             # 🔧 Development commands
├── CHANGELOG.md                         # 📝 Version history
├── CONTRIBUTING.md                      # 🤝 Contribution guidelines
├── SECURITY.md                          # 🔐 Security policy
├── LICENSE                              # ⚖️ MIT License
├── .gitignore                          # 🚫 Git ignore rules
└── README.md                           # 📖 Project documentation
```

## 🎯 Key Features

- **Modern Python Structure**: Follows Python packaging best practices
- **Complete Test Isolation**: Tests work without external CLI dependencies
- **Professional Packaging**: Uses pyproject.toml for modern Python packaging
- **Development Environment**: Full VS Code + devcontainer support
- **CI/CD Pipeline**: GitHub Actions with security scanning
- **Cross-Platform**: Works on macOS, Linux, and Windows
- **Expert-Level Code**: Type hints, comprehensive error handling, security validation

## 🚀 Quick Start

```bash
# Install development environment
make install

# Run safe tests (no CLI dependencies)
make test-unit

# Run with system CLI access
make test-all

# Execute the tool
python src/aks_credential_loader.py --dry-run --verbose
./scripts/aks_credential_loader.sh --dry-run --verbose
./aks-credential-loader --dry-run --verbose
```

## 🔧 Development

```bash
# Format code
black src/ tests/

# Lint code
pylint src/

# Type checking
mypy src/

# Security scan
bandit -r src/

# Coverage report
make test-coverage
```

This structure represents expert-level Python project organization with complete separation of concerns, proper testing infrastructure, and modern packaging standards.
