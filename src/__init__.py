"""Azure Kubernetes Credential Loader package."""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "Automated tool to fetch AKS cluster credentials across Azure subscriptions"

from .aks_credential_loader import AKSCredentialLoader

__all__ = ["AKSCredentialLoader"]
