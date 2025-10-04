# Makefile for Azure Kubernetes Credential Loader

.PHONY: help install test dry-run run clean

help: ## Show this help message
	@echo "Azure Kubernetes Credential Loader"
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install prerequisites (Azure CLI and kubelogin)
	@echo "Installing prerequisites..."
	@if command -v brew >/dev/null 2>&1; then \
		echo "Installing Azure CLI..."; \
		brew install azure-cli; \
		echo "Installing kubelogin..."; \
		brew install Azure/kubelogin/kubelogin; \
	else \
		echo "Homebrew not found. Please install Azure CLI and kubelogin manually:"; \
		echo "  Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"; \
		echo "  kubelogin: https://github.com/Azure/kubelogin"; \
	fi

test: ## Run all tests (unit tests + integration tests)
	@echo "Running unit tests..."
	pytest test_aks_credential_loader.py -v
	@echo ""
	@echo "Testing Python version integration..."
	python3 aks_credential_loader.py --dry-run --verbose || echo "Expected: requires Azure CLI"
	@echo ""
	@echo "Testing Bash version integration..."
	./aks_credential_loader.sh --dry-run --verbose || echo "Expected: requires Azure CLI"

run-dry: ## Run the Python version with dry-run
	python3 src/aks_credential_loader.py --dry-run --verbose

dry-run-bash: ## Run dry-run mode to preview actions (Bash version)
	./aks_credential_loader.sh --dry-run --verbose

run: ## Run the credential loader (Python version)
	python3 aks_credential_loader.py --verbose

run-bash: ## Run the Bash version
	./scripts/aks_credential_loader.sh

check-prereqs: ## Check if prerequisites are installed
	@echo "Checking prerequisites..."
	@command -v az >/dev/null 2>&1 || { echo "❌ Azure CLI not found"; exit 1; }
	@echo "✅ Azure CLI found: $$(az --version | head -n1)"
	@command -v kubelogin >/dev/null 2>&1 || { echo "❌ kubelogin not found"; exit 1; }
	@echo "✅ kubelogin found: $$(kubelogin --version)"
	@command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 not found"; exit 1; }
	@echo "✅ Python 3 found: $$(python3 --version)"
	@command -v jq >/dev/null 2>&1 || { echo "❌ jq not found (needed for bash version)"; exit 1; }
	@echo "✅ jq found: $$(jq --version)"
	@echo "✅ All prerequisites are installed"

test-unit: ## Run safe unit tests (no CLI dependencies) in isolated environment
	@echo "🔧 Creating isolated test environment..."
	@rm -rf .test-venv 2>/dev/null || true
	@python3 -m venv .test-venv
	@.test-venv/bin/pip install --quiet pytest pytest-mock pytest-cov
	@echo "🧪 Running isolated unit tests..."
	@.test-venv/bin/python -m pytest tests/test_simple.py tests/test_isolated.py -v
	@echo "🧹 Cleaning up test environment..."
	@rm -rf .test-venv
	@echo "✅ Unit tests completed successfully"

test-unit-dev: ## Run unit tests using existing .venv (for development)
	.venv/bin/python -m pytest tests/test_simple.py tests/test_isolated.py -v

test-all: ## Run all tests (requires system CLI tools)
	./scripts/run_tests.sh tests/test_aks_credential_loader.py -v

test-coverage: ## Run tests with coverage report
	./run_tests.sh --cov=aks_credential_loader --cov-report=term-missing

install-test: ## Install test dependencies
	pip install -r requirements-test.txt

clean: ## Clean up any temporary files
	@echo "Cleaning up..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".coverage" -delete 2>/dev/null || true
	@find . -name "coverage.xml" -delete 2>/dev/null || true
	@rm -rf .test-venv 2>/dev/null || true
	@echo "✅ Cleanup complete"

login: ## Login to Azure CLI
	az login

logout: ## Logout from Azure CLI
	az logout

status: ## Show current Azure CLI status
	@echo "Azure CLI Status:"
	@az account show --output table 2>/dev/null || echo "Not logged in to Azure CLI"
