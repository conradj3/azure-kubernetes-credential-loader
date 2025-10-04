# Security Policy

## Supported Versions

We actively support the latest version of Azure Kubernetes Credential Loader with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Security Considerations

### Subprocess Usage
This tool legitimately uses Python's `subprocess` module to execute:
- Azure CLI (`az`) commands
- `kubectl` commands
- `kubelogin` commands

**Security Measures:**
- ✅ All commands use controlled argument arrays (no shell injection)
- ✅ No `shell=True` parameter used
- ✅ No user input directly passed to subprocess calls
- ✅ All command arguments are validated internally
- ✅ Commands are hardcoded (az, kubectl, kubelogin)

### Authentication
- Uses existing Azure CLI authentication (`az login`)
- No credentials are stored or handled by this tool
- All authentication is delegated to Azure CLI and kubelogin

### Network Security
- Only communicates with official Azure APIs through Azure CLI
- No direct network connections made by this tool
- All requests go through authenticated Azure CLI sessions

## Reporting a Vulnerability

If you discover a security vulnerability, please:

1. **DO NOT** open a public issue
2. Email the maintainers with details
3. Allow reasonable time for response and patching
4. Provide clear reproduction steps if possible

### What to Include
- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested mitigation (if known)

### Response Timeline
- Initial response: Within 48 hours
- Status update: Within 1 week
- Resolution timeline: Communicated after assessment

## Security Scanning

This project uses:
- **Bandit** for Python security analysis
- **GitHub Security Advisories** for dependency scanning
- **Manual security reviews** for all pull requests

### Running Security Scans Locally

```bash
# Install bandit
pip install bandit

# Run security scan
bandit -r src/ -c pyproject.toml

# Check dependencies (if any)
pip install safety
safety check
```

## Best Practices for Users

### Before Running
1. Always use `--dry-run` first to preview actions
2. Ensure you're logged into the correct Azure account
3. Review the list of subscriptions that will be processed
4. Backup your existing `~/.kube/config` if important

### Safe Usage
```bash
# Safe workflow
az login                                             # Authenticate first
./aks-credential-loader --dry-run                  # Preview actions
./aks-credential-loader --verbose                  # Run with logging
kubectl config get-contexts                         # Verify results
```

### What This Tool Does NOT Do
- ❌ Store or transmit credentials
- ❌ Modify Azure resources
- ❌ Execute arbitrary commands
- ❌ Access sensitive data beyond cluster names/locations
- ❌ Make network connections outside of Azure CLI

### What This Tool DOES Do
- ✅ Discovers AKS clusters via Azure CLI
- ✅ Downloads cluster access configurations
- ✅ Updates local kubectl configuration
- ✅ Configures Azure CLI authentication for clusters

## License
This security policy is provided under the same license as the project.
