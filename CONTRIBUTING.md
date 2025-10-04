# Contributing to Azure Kubernetes Credential Loader

Thank you for your interest in contributing! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### 1. Development Setup

#### Using GitHub Codespaces (Recommended)
1. Click "Code" → "Codespaces" → "Create codespace on main"
2. Wait for automatic setup to complete
3. Start coding immediately with all tools pre-installed!

#### Local Development
1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Open in VS Code: `code azure-kubernetes-crdential-loader`
4. Install prerequisites: `make install`

#### Dev Container
1. Open in VS Code
2. Command Palette → "Dev Containers: Reopen in Container"
3. Wait for container to build and setup to complete

### 2. Making Changes

1. **Create a branch:** `git checkout -b feature/your-feature-name`
2. **Make your changes** using the development environment
3. **Test your changes:** `make test`
4. **Check code quality:** `make check-prereqs`
5. **Commit your changes:** `git commit -m "Add: description of changes"`
6. **Push to your fork:** `git push origin feature/your-feature-name`
7. **Create a Pull Request**

## 🛠️ Development Guidelines

### Code Style
- **Python:** Follow PEP 8, use type hints, include docstrings
- **Shell:** Follow shellcheck recommendations
- **Documentation:** Use clear, concise language with examples

### Testing
- Always test with `--dry-run` first
- Test on multiple Python versions (3.8+)
- Validate shell scripts with shellcheck
- Test in both local and Codespace environments

### GitHub Copilot Usage
- Use descriptive comments to guide Copilot suggestions
- Leverage Copilot Chat for complex implementations
- Ask Copilot to help with documentation and tests
- See [.github/copilot-instructions.md](.github/copilot-instructions.md) for detailed guidance

## 📋 Pull Request Process

1. **Ensure CI passes** - All GitHub Actions must be green
2. **Update documentation** - README, EXAMPLES, etc.
3. **Add tests** - If adding new functionality
4. **Follow conventional commits** - Use clear, descriptive commit messages
5. **Request review** - Tag maintainers for review

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] Tested with `--dry-run`
- [ ] Tested with real Azure subscriptions
- [ ] Added/updated tests
- [ ] Documentation updated

## Screenshots/Logs
Include relevant output or screenshots
```

## 🐛 Bug Reports

Use the following template for bug reports:

```markdown
## Bug Description
Clear description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS, Ubuntu]
- Python version: [e.g., 3.11]
- Azure CLI version: [e.g., 2.50.0]
- kubelogin version: [e.g., 0.0.28]

## Additional Context
Any other relevant information
```

## 💡 Feature Requests

For feature requests, please:
1. Check existing issues to avoid duplicates
2. Clearly describe the use case
3. Explain why it would be valuable
4. Consider implementation complexity
5. Be open to discussion and iteration

## 🎯 Areas for Contribution

### High Priority
- [ ] Support for additional cloud providers
- [ ] Enhanced error handling and recovery
- [ ] Performance optimizations
- [ ] Additional output formats (JSON, YAML)
- [ ] Configuration file support

### Documentation
- [ ] More usage examples
- [ ] Video tutorials
- [ ] Troubleshooting guides
- [ ] Integration examples

### Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance benchmarks
- [ ] Cross-platform testing

## 🔧 Development Environment Details

### Available Tools
- **Python 3.11** with all required packages
- **Azure CLI** latest version
- **kubectl** for Kubernetes operations
- **kubelogin** for Azure authentication
- **jq** for JSON processing
- **shellcheck** for shell script validation
- **GitHub Copilot** enabled for AI assistance

### VS Code Configuration
- Pre-configured launch configurations for debugging
- Tasks for common operations
- Extensions for Python, Azure, Kubernetes
- Code formatting on save
- Lint on save

### Makefile Targets
```bash
make help           # Show available commands
make install        # Install prerequisites
make test           # Run all tests
make check-prereqs  # Verify environment
make clean          # Clean up temporary files
```

## 📜 Code of Conduct

Please note that this project is released with a [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## 📞 Getting Help

- **GitHub Issues:** For bugs and feature requests
- **GitHub Discussions:** For questions and general discussion
- **Copilot Chat:** For development help (if you have access)

## 🏆 Recognition

Contributors will be:
- Listed in the README
- Mentioned in release notes
- Given credit in commit messages
- Invited to be maintainers for significant contributions

Thank you for contributing to making Azure Kubernetes credential management easier for everyone! 🚀
