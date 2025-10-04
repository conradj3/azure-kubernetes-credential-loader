# Copilot Instructions for Azure Kubernetes Credential Loader

## Architecture Overview

This is a **dual-implementation CLI tool** (Python + Bash) that automates AKS cluster credential fetching across Azure subscriptions. The core pattern is:
1. **Discover** all Azure subscriptions (or filter by user input)
2. **Enumerate** AKS clusters in each subscription
3. **Fetch credentials** using `az aks get-credentials` + `kubelogin convert-kubeconfig`

**Key Design Decision**: Complete external CLI dependency (Azure CLI, kubelogin) with zero Python runtime dependencies - uses only stdlib.

## Project Structure (src/ Layout)

```
src/aks_credential_loader.py     # Main Python implementation
scripts/aks_credential_loader.sh # Bash equivalent
tests/test_isolated.py           # Primary test suite (fully mocked)
tests/test_simple.py             # Basic functionality tests
```

**Critical**: Tests use `sys.path.insert(0, '../src')` pattern for imports since we use src/ layout.

## Development Workflows

### Testing Strategy (No External Dependencies)
```bash
make test-unit          # Safe isolated tests (no CLI deps)
make test-all           # Full integration (requires az/kubelogin)
./scripts/run_tests.sh  # Test runner with system PATH access
```

**Testing Pattern**: `test_isolated.py` uses complete `subprocess.run` mocking to eliminate Azure CLI dependencies. The `.venv` is isolated and doesn't inherit system CLI tools.

### Key Development Commands
```bash
# Primary development cycle
make run-dry                    # Python dry-run
./scripts/aks_credential_loader.sh --dry-run  # Bash dry-run
make check-prereqs             # Verify CLI tools installed

# Professional tooling
black src/ tests/              # Code formatting
pylint src/                   # Linting (configured in pyproject.toml)
bandit -r src/               # Security scanning
```

## Code Patterns & Conventions

### Error Handling Strategy
- **Subprocess failures**: Wrapped with try/catch, return `None` on failure
- **API call patterns**: Always use `capture_output=True, text=True, check=True`
- **Dry-run mode**: `allow_in_dry_run=False` parameter controls execution vs preview

### Professional Output Pattern
```python
# Structured logging with emojis for UX
self.logger.info("🔍 Preview mode - no changes made")
self.logger.info(f"📊 Summary: {successful}/{total} clusters")
```

### Type Hints Approach
- **Return types**: `Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]` for Azure CLI JSON responses
- **Command building**: `List[str]` for subprocess command arrays
- **Full typing**: Every method has complete type annotations

## Integration Points

### External CLI Dependencies (Critical)
- **Azure CLI**: `az account list`, `az aks list`, `az aks get-credentials`
- **kubelogin**: `kubelogin convert-kubeconfig -l azurecli` (Azure auth integration)
- **subprocess pattern**: Always validate CLI tool availability before execution

### Data Flow
1. **Subscription Discovery**: `az account list --output json` → filter by user input
2. **Cluster Enumeration**: `az account set + az aks list` per subscription
3. **Credential Fetching**: `az aks get-credentials + kubelogin convert-kubeconfig`

### Configuration Sources
- **pyproject.toml**: Modern Python packaging + tool configs (black, pylint, pytest)
- **Makefile**: Developer workflow automation
- **.vscode/**: Complete debug configurations for both Python and Bash versions

## Testing Architecture

**Core Challenge**: Testing subprocess-heavy code without external dependencies.

**Solution Pattern**:
```python
@patch('subprocess.run')
def test_function(self, mock_subprocess):
    mock_subprocess.return_value.stdout = '{"mock": "data"}'
    # Test logic here
```

**Test Isolation**: Use `sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))` in test files for src/ imports.

## Build & Packaging

- **Entry point**: `./aks-credential-loader` CLI script
- **Package structure**: `pyproject.toml` with src/ layout
- **Distribution**: Console script entry point: `aks-credential-loader = src.aks_credential_loader:main`
- **CI/CD**: Multi-Python version testing (3.8-3.12) with security scanning

## Security Considerations

- **Input validation**: All subscription IDs validated before shell execution
- **Bandit scanning**: Configured to ignore legitimate subprocess use cases
- **No secrets**: Tool relies on existing `az login` authentication
- **Shell injection prevention**: Always use `subprocess.run` with list arguments, never shell=True
