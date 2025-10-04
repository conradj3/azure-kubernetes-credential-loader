# Usage Examples

This document provides detailed examples of how to use the Azure Kubernetes Credential Loader.

## 🚀 Quick Start Examples

### Basic Usage

```bash
# Fetch credentials for all AKS clusters (recommended)
./aks-credential-loader

# Alternative: Direct Python execution
python3 src/aks_credential_loader.py
```

### Dry Run (Recommended First Step)

```bash
# Preview what would be executed (recommended)
./aks-credential-loader --dry-run --verbose

# Alternative: Direct Python execution
python3 src/aks_credential_loader.py --dry-run --verbose
```

## 🎯 Targeting Specific Subscriptions

### Single Subscription by ID

```bash
# Target a specific subscription by ID
./aks-credential-loader --subscription 12345678-1234-1234-1234-123456789abc

# Alternative: Direct Python execution
python3 src/aks_credential_loader.py --subscription 12345678-1234-1234-1234-123456789abc
```

### Single Subscription by Name

```bash
# Target subscription by name
./aks-credential-loader --subscription "mock-subscription-01"
```

### Multiple Subscriptions

```bash
# Target multiple subscriptions
./aks-credential-loader -s sub1 -s sub2 -s sub3

# Alternative: Direct Python execution
python3 src/aks_credential_loader.py --subscription sub1 sub2 sub3
```

## 📝 Verbose Logging

```bash
# Enable detailed logging
./aks-credential-loader --verbose

# Alternative: Direct Python execution
python3 src/aks_credential_loader.py --verbose
```

## 🔍 Combining Options

```bash
# Dry run with verbose logging for specific subscription
./aks-credential-loader --dry-run --verbose --subscription 12345678-1234-1234-1234-123456789abc

# Multiple subscriptions with verbose logging
./aks-credential-loader --verbose -s production-sub -s development-sub
```

## 🛠️ Using Makefile Commands

```bash
# Install prerequisites
make install

# Check if all tools are installed
make check-prereqs

# Test both versions
make test

# Run Python version in dry-run mode
make dry-run

# Run Bash version in dry-run mode
make dry-run-bash

# Run Python version
make run

# Run Bash version (recommended)
make run-bash
```

## 📊 Expected Output

### Successful Run Example

```
[INFO] 2025-10-02 17:13:51 - Starting Azure Kubernetes Credential Loader
[INFO] 2025-10-02 17:13:52 - Checking prerequisites...
[INFO] 2025-10-02 17:13:52 - Prerequisites check passed
[INFO] 2025-10-02 17:13:52 - Discovering Azure subscriptions...
[INFO] 2025-10-02 17:13:52 - Found 26 subscription(s) to process
WARNING: Merged "mock-aks-cluster-01" as current context in /Users/user/.kube/config
WARNING: Merged "e-n-shr-aks-01" as current context in /Users/user/.kube/config
...
[INFO] 2025-10-02 17:15:44 - ============================================================
[INFO] 2025-10-02 17:15:44 - FINAL SUMMARY
[INFO] 2025-10-02 17:15:44 - ============================================================
[INFO] 2025-10-02 17:15:44 - Total subscriptions processed: 26
[INFO] 2025-10-02 17:15:44 - Total AKS clusters found: 22
[INFO] 2025-10-02 17:15:44 - Successfully configured: 22/22 clusters
```

### Dry Run Example

```
[INFO] 2025-10-02 17:13:34 - Starting Azure Kubernetes Credential Loader
[INFO] 2025-10-02 17:13:34 - Running in DRY RUN mode - no actual changes will be made
[INFO] 2025-10-02 17:13:34 - [DRY RUN] Would execute: az account list --output json
[INFO] 2025-10-02 17:13:34 - [DRY RUN] Would execute: az account set --subscription 'sub-id'
[INFO] 2025-10-02 17:13:34 - [DRY RUN] Would execute: az aks get-credentials --resource-group 'rg' --name 'cluster' --overwrite-existing
[INFO] 2025-10-02 17:13:34 - [DRY RUN] Would execute: kubelogin convert-kubeconfig -l azurecli
[INFO] 2025-10-02 17:13:35 - DRY RUN completed - no actual changes were made
```

## 🎯 What Each Command Does

The tool executes these three commands for each AKS cluster:

1. **Set subscription context:**
   ```bash
   az account set --subscription 12345678-1234-1234-1234-123456789abc
   ```

2. **Get AKS credentials:**
   ```bash
   az aks get-credentials --resource-group mock-resource-group-01 --name mock-aks-cluster-01 --overwrite-existing
   ```

3. **Convert to Azure CLI authentication:**
   ```bash
   kubelogin convert-kubeconfig -l azurecli
   ```

## 🔧 After Running

Once the tool has run successfully:

```bash
# List all available contexts
kubectl config get-contexts

# Switch to a specific cluster
kubectl config use-context mock-aks-cluster-01

# Test connectivity
kubectl get nodes
```

## 🚨 Troubleshooting Examples

### Permission Issues

```bash
# If you get permission errors, try targeting specific subscriptions
./aks-credential-loader --subscription "your-accessible-subscription"

# Or test with dry-run first
./aks-credential-loader --dry-run --verbose
```

### Prerequisites Not Found

```bash
# Check what's missing
make check-prereqs

# Install missing tools (macOS)
make install
```
