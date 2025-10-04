"""
Test suite for Azure Kubernetes Credential Loader

This test suite uses mocking to test all functionality without requiring
actual Azure CLI authentication or AKS clusters.
"""

# type: ignore[misc,unused-ignore,no-untyped-def,attr-defined,arg-type,return-value,call-arg]
# pylint: disable=import-error,unused-import,import-outside-toplevel

import pytest
from unittest.mock import Mock, patch
import subprocess  # pylint: disable=unused-import
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from aks_credential_loader import AKSCredentialLoader


class TestAKSCredentialLoader:
    """Test class for AKSCredentialLoader functionality"""

    @pytest.fixture
    def loader(self) -> AKSCredentialLoader:
        """Create a test instance of AKSCredentialLoader"""
        return AKSCredentialLoader(dry_run=True, verbose=True)

    @pytest.fixture
    def prod_loader(self) -> AKSCredentialLoader:
        """Create a production mode instance for testing"""
        return AKSCredentialLoader(dry_run=False, verbose=False)

    @pytest.fixture
    def mock_subscriptions(self) -> "list[dict]":
        """Mock subscription data"""
        return [
            {
                "id": "12345678-1234-1234-1234-123456789abc",
                "name": "mock-subscription-01",
                "state": "Enabled",
            },
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "test-subscription",
                "state": "Enabled",
            },
        ]

    @pytest.fixture
    def mock_clusters(self) -> "list[dict]":
        """Mock AKS cluster data"""
        return [
            {
                "name": "mock-aks-cluster-01",
                "resourceGroup": "mock-resource-group-01",
                "location": "eastus",
            },
            {"name": "test-cluster", "resourceGroup": "test-rg", "location": "westus2"},
        ]

    def test_loader_initialization(self) -> None:
        """Test AKSCredentialLoader initialization"""
        # Test dry-run mode
        loader = AKSCredentialLoader(dry_run=True, verbose=True)
        assert loader.dry_run is True
        assert loader.verbose is True

        # Test production mode
        loader = AKSCredentialLoader(dry_run=False, verbose=False)
        assert loader.dry_run is False
        assert loader.verbose is False

    @patch("subprocess.run")
    def test_run_az_command_dry_run(
        self, mock_subprocess: Mock, loader: AKSCredentialLoader
    ) -> None:
        """Test Azure CLI command execution in dry-run mode"""
        # Test dry-run mode (should not execute)
        result = loader.run_az_command(["account", "list"])
        assert result is None
        mock_subprocess.assert_not_called()

        # Test dry-run with allow_in_dry_run=True
        mock_subprocess.return_value.stdout = "[]"
        result = loader.run_az_command(["account", "list"], allow_in_dry_run=True)
        mock_subprocess.assert_called_once()

    @patch("subprocess.run")
    def test_run_az_command_success(
        self, mock_subprocess: Mock, prod_loader: AKSCredentialLoader
    ) -> None:
        """Test successful Azure CLI command execution"""
        # Mock successful subprocess call
        mock_result = Mock()
        mock_result.stdout = '[{"id": "test", "name": "test"}]'
        mock_subprocess.return_value = mock_result

        result = prod_loader.run_az_command(["account", "list"])

        assert result == [{"id": "test", "name": "test"}]
        mock_subprocess.assert_called_once_with(
            ["az", "account", "list"], capture_output=True, text=True, check=True
        )

    @patch("subprocess.run")
    def test_run_az_command_failure(
        self, mock_subprocess: Mock, prod_loader: AKSCredentialLoader
    ) -> None:
        """Test Azure CLI command execution failure"""
        # Mock subprocess failure
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "az")

        result = prod_loader.run_az_command(["account", "list"])
        assert result is None

    @patch("subprocess.run")
    def test_run_kubelogin_command_dry_run(
        self, mock_subprocess: Mock, loader: AKSCredentialLoader
    ) -> None:
        """Test kubelogin command in dry-run mode"""
        result = loader.run_kubelogin_command(["convert-kubeconfig", "-l", "azurecli"])
        assert result is True
        mock_subprocess.assert_not_called()

    @patch("subprocess.run")
    def test_run_kubelogin_command_success(
        self, mock_subprocess: Mock, prod_loader: AKSCredentialLoader
    ) -> None:
        """Test successful kubelogin command execution"""
        result = prod_loader.run_kubelogin_command(["convert-kubeconfig", "-l", "azurecli"])
        assert result is True
        mock_subprocess.assert_called_once()

    @patch("subprocess.run")
    def test_run_kubelogin_command_failure(
        self, mock_subprocess: Mock, prod_loader: AKSCredentialLoader
    ) -> None:
        """Test kubelogin command failure"""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "kubelogin")

        result = prod_loader.run_kubelogin_command(["convert-kubeconfig", "-l", "azurecli"])
        assert result is False

    def test_get_subscriptions_with_mock(
        self, loader: AKSCredentialLoader, mock_subscriptions: "list[dict]"
    ) -> None:
        """Test subscription retrieval with mocked data"""
        with patch.object(loader, "run_az_command", return_value=mock_subscriptions):
            result = loader.get_subscriptions()
            assert len(result) == 2
            assert result[0]["name"] == "mock-subscription-01"
            assert result[1]["name"] == "test-subscription"

    def test_get_subscriptions_with_filter(
        self, loader: AKSCredentialLoader, mock_subscriptions: "list[dict]"
    ) -> None:
        """Test subscription retrieval with filtering"""
        with patch.object(loader, "run_az_command", return_value=mock_subscriptions):
            # Test filtering by ID
            result = loader.get_subscriptions(["12345678-1234-1234-1234-123456789abc"])
            assert len(result) == 1
            assert result[0]["name"] == "mock-subscription-01"

            # Test filtering by name
            result = loader.get_subscriptions(["test-subscription"])
            assert len(result) == 1
            assert result[0]["name"] == "test-subscription"

            # Test no matches
            result = loader.get_subscriptions(["nonexistent"])
            assert len(result) == 0

    def test_get_subscriptions_failure(self, loader: AKSCredentialLoader) -> None:
        """Test subscription retrieval failure"""
        with patch.object(loader, "run_az_command", return_value=None):
            result = loader.get_subscriptions()
            assert result == []

    def test_get_aks_clusters_success(
        self, loader: AKSCredentialLoader, mock_clusters: "list[dict]"
    ) -> None:
        """Test AKS cluster retrieval"""
        with patch.object(loader, "run_az_command") as mock_run:
            # Mock successful subscription set and cluster list
            mock_run.side_effect = [True, mock_clusters]
            # First call sets subscription, second lists clusters

            result = loader.get_aks_clusters("test-subscription-id")
            assert len(result) == 2
            assert result[0]["name"] == "mock-aks-cluster-01"
            assert result[1]["name"] == "test-cluster"

    def test_get_aks_clusters_no_clusters(self, loader: AKSCredentialLoader) -> None:
        """Test AKS cluster retrieval with no clusters"""
        with patch.object(loader, "run_az_command") as mock_run:
            mock_run.side_effect = [{}, []]  # Empty cluster list

            result = loader.get_aks_clusters("test-subscription-id")
            assert len(result) == 0

    def test_get_aks_clusters_subscription_failure(self, loader: AKSCredentialLoader) -> None:
        """Test AKS cluster retrieval with subscription access failure"""
        with patch.object(loader, "run_az_command", return_value=None):
            result = loader.get_aks_clusters("test-subscription-id")
            assert result == []

    def test_fetch_cluster_credentials_dry_run(self, loader: AKSCredentialLoader) -> None:
        """Test credential fetching in dry-run mode"""
        cluster = {"name": "test-cluster", "resourceGroup": "test-rg"}

        with patch.object(loader, "run_az_command", return_value={}), patch.object(
            loader, "run_kubelogin_command", return_value=True
        ):

            result = loader.fetch_cluster_credentials("test-sub-id", cluster)
            assert result is True

    def test_fetch_cluster_credentials_success(self, prod_loader: AKSCredentialLoader) -> None:
        """Test successful credential fetching"""
        cluster = {"name": "test-cluster", "resourceGroup": "test-rg"}

        with patch.object(prod_loader, "run_az_command", return_value=True), patch.object(
            prod_loader, "run_kubelogin_command", return_value=True
        ):

            result = prod_loader.fetch_cluster_credentials("test-sub-id", cluster)
            assert result is True

    def test_fetch_cluster_credentials_az_failure(self, prod_loader: AKSCredentialLoader) -> None:
        """Test credential fetching with Azure CLI failure"""
        cluster = {"name": "test-cluster", "resourceGroup": "test-rg"}

        with patch.object(prod_loader, "run_az_command", return_value=None):
            result = prod_loader.fetch_cluster_credentials("test-sub-id", cluster)
            assert result is False

    def test_fetch_cluster_credentials_kubelogin_failure(
        self, prod_loader: AKSCredentialLoader
    ) -> None:
        """Test credential fetching with kubelogin failure"""
        cluster = {"name": "test-cluster", "resourceGroup": "test-rg"}

        with patch.object(prod_loader, "run_az_command", return_value={}), patch.object(
            prod_loader, "run_kubelogin_command", return_value=False
        ):

            result = prod_loader.fetch_cluster_credentials("test-sub-id", cluster)
            assert result is False

    def test_load_all_credentials_integration(
        self,
        loader: AKSCredentialLoader,
        mock_subscriptions: "list[dict]",
        mock_clusters: "list[dict]",
    ) -> None:
        """Test the complete credential loading workflow"""
        with patch.object(
            loader, "get_subscriptions", return_value=mock_subscriptions
        ) as mock_get_subs, patch.object(
            loader, "get_aks_clusters", return_value=mock_clusters
        ), patch.object(
            loader, "fetch_cluster_credentials", return_value=True
        ):

            # This should complete without errors
            loader.load_all_credentials()

            # Verify get_subscriptions was called
            mock_get_subs.assert_called_once_with()

    def test_load_all_credentials_no_subscriptions(self, loader: AKSCredentialLoader) -> None:
        """Test credential loading with no subscriptions"""
        with patch.object(loader, "get_subscriptions", return_value=[]):
            loader.load_all_credentials()

    def test_load_all_credentials_no_clusters(
        self, loader: AKSCredentialLoader, mock_subscriptions: "list[dict]"
    ) -> None:
        """Test credential loading with no clusters"""
        with patch.object(
            loader, "get_subscriptions", return_value=mock_subscriptions
        ), patch.object(loader, "get_aks_clusters", return_value=[]):

            loader.load_all_credentials()

    def test_cluster_missing_fields(self, loader: AKSCredentialLoader) -> None:
        """Test handling of clusters with missing fields"""
        cluster_missing_fields = {"name": "test-cluster"}  # Missing resourceGroup

        result = loader.fetch_cluster_credentials("test-sub", cluster_missing_fields)
        # Should handle missing fields gracefully
        assert isinstance(result, bool)


class TestMainFunction:
    """Test the main function and command-line argument parsing"""

    @patch("aks_credential_loader.subprocess.run")
    @patch("aks_credential_loader.AKSCredentialLoader")
    def test_main_function_prerequisites_success(
        self, mock_loader_class: Mock, mock_subprocess: Mock
    ) -> None:
        """Test main function with successful prerequisites check"""
        # Mock subprocess calls for prerequisite checks
        mock_subprocess.return_value = Mock()

        # Mock the loader instance
        mock_loader = Mock()
        mock_loader_class.return_value = mock_loader

        # Import and test main function
        from aks_credential_loader import main

        # Mock sys.argv for argument parsing
        with patch("sys.argv", ["aks_credential_loader.py", "--dry-run"]):
            main()

        # Verify loader was created and called
        mock_loader_class.assert_called_once_with(dry_run=True, verbose=False)
        mock_loader.load_all_credentials.assert_called_once()


class TestArgumentParsing:
    """Test command-line argument parsing"""

    def test_argument_parsing_defaults(self) -> None:
        """Test default argument values"""
        import argparse

        # Create parser similar to the one in main()
        parser = argparse.ArgumentParser()
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--verbose", "-v", action="store_true")
        parser.add_argument("--subscription", "-s", nargs="+")

        # Test defaults
        args = parser.parse_args([])
        assert args.dry_run is False
        assert args.verbose is False
        assert args.subscription is None

    def test_argument_parsing_with_options(self) -> None:
        """Test argument parsing with options"""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--verbose", "-v", action="store_true")
        parser.add_argument("--subscription", "-s", nargs="+")

        # Test with options
        args = parser.parse_args(["--dry-run", "--verbose", "--subscription", "sub1", "sub2"])
        assert args.dry_run is True
        assert args.verbose is True
        assert args.subscription == ["sub1", "sub2"]


if __name__ == "__main__":
    pytest.main([__file__])
