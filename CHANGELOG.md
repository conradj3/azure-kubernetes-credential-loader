# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-02

### Added
- Initial release of Azure Kubernetes Credential Loader
- Python implementation with full type hints and error handling
- Bash implementation for shell environments
- Comprehensive test suite with mocking
- Docker development environment support
- GitHub Actions CI/CD pipeline
- Security scanning with bandit
- Professional documentation and examples
- Multi-subscription and multi-cluster support
- Dry-run mode for safe testing
- Verbose logging for debugging

### Features
- Automatic discovery of AKS clusters across all subscriptions
- Credential fetching with kubelogin integration
- Filtering by subscription ID or name
- Professional emoji-enhanced output
- Complete error handling and validation
- Cross-platform compatibility (macOS, Linux, Windows)

### Security
- Input validation and sanitization
- Secure subprocess execution
- No hardcoded secrets or credentials
- Bandit security scanning integration
