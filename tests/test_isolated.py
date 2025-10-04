"""Isolated tests for Azure Kubernetes Credential Loader.

This test suite focuses on core functionality with complete mocking
to avoid any dependency on host system CLI tools.
"""

# type: ignore
# pylint: disable=import-error,unused-import,pointless-string-statement,missing-function-docstring
# mypy: ignore-errors

import pytest
from unittest.mock import Mock, patch
from typing import Any, Dict, List, Optional

try:
    from aks_credential_loader import AKSCredentialLoader  # type: ignore
except ImportError:
    # Skip tests if module can't be imported
    AKSCredentialLoader = None  # type: ignore
    pytest.skip("aks_credential_loader module not found", allow_module_level=True)


class TestAKSCredentialLoaderCore:
    """Test core AKSCredentialLoader functionality with complete isolation"""

    @pytest.fixture  # type: ignore
    def loader(self) -> Any:
        if AKSCredentialLoader is None:
            pytest.skip("AKSCredentialLoader not available")
        return AKSCredentialLoader(dry_run=True, verbose=True)

    @pytest.fixture  # type: ignore
    def prod_loader(self) -> Any:
        if AKSCredentialLoader is None:
            pytest.skip("AKSCredentialLoader not available")
        return AKSCredentialLoader(dry_run=False, verbose=False)

    @pytest.fixture  # type: ignore
    def mock_subscriptions(self) -> List[Dict[str, str]]:
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

    @pytest.fixture  # type: ignore
    def mock_clusters(self) -> List[Dict[str, str]]:
        return [
            {
                "name": "mock-aks-cluster-01",
                "resourceGroup": "mock-resource-group-01",
                "location": "eastus",
            },
            {"name": "test-cluster", "resourceGroup": "test-rg", "location": "westus2"},
        ]

    def test_loader_initialization(self) -> None:  # type: ignore
        if AKSCredentialLoader is None:
            pytest.skip("AKSCredentialLoader not available")

        # Test dry-run mode
        loader = AKSCredentialLoader(dry_run=True, verbose=True)
        assert loader.dry_run is True
        assert loader.verbose is True

        # Test production mode
        loader = AKSCredentialLoader(dry_run=False, verbose=False)
        assert loader.dry_run is False
        assert loader.verbose is False

    @patch("subprocess.run")
    def test_run_az_command_dry_run(self, mock_subprocess: Any) -> None:  # type: ignore
        if AKSCredentialLoader is None:
            pytest.skip("AKSCredentialLoader not available")
        loader = AKSCredentialLoader(
            dry_run=True, verbose=True
        )  # Test dry-run mode (should not execute)
        result = loader.run_az_command(["account", "list"])
        assert result is None
        mock_subprocess.assert_not_called()

        # Test dry-run with allow_in_dry_run=True
        mock_result = Mock()
        mock_result.stdout = "[]"
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        result = loader.run_az_command(["account", "list"], allow_in_dry_run=True)
        mock_subprocess.assert_called_once()
        assert result == []

    @patch("subprocess.run")
    def test_run_az_command_success(self, mock_subprocess: Any) -> None:  # type: ignore
        if AKSCredentialLoader is None:
            pytest.skip("AKSCredentialLoader not available")
        prod_loader = AKSCredentialLoader(dry_run=False, verbose=False)

        # Mock successful subprocess call
        mock_result = Mock()
        mock_result.stdout = '[{"id": "test", "name": "test"}]'
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        result = prod_loader.run_az_command(["account", "list"])

        assert result == [{"id": "test", "name": "test"}]
        mock_subprocess.assert_called_once()

    @patch("subprocess.run")
    def test_run_kubelogin_command_success(self, mock_subprocess: Any) -> None:  # type: ignore
        if AKSCredentialLoader is None:
            pytest.skip("AKSCredentialLoader not available")
        prod_loader = AKSCredentialLoader(dry_run=False, verbose=False)

        # Mock successful subprocess call
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        result = prod_loader.run_kubelogin_command(["convert-kubeconfig", "-l", "azurecli"])

        assert result is True
        mock_subprocess.assert_called_once()

    def test_get_subscriptions_with_mock(self, loader: Any, mock_subscriptions: Any) -> None:  # type: ignore
        with patch.object(loader, "run_az_command", return_value=mock_subscriptions):
            result = loader.get_subscriptions()
            assert len(result) == 2
            assert result[0]["name"] == "mock-subscription-01"
            assert result[1]["name"] == "test-subscription"

    def test_get_subscriptions_with_filter(self, loader: Any, mock_subscriptions: Any) -> None:  # type: ignore
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

    def test_get_aks_clusters_success(self, loader: Any, mock_clusters: Any) -> None:
        """Test AKS cluster retrieval"""
        with patch.object(loader, "run_az_command") as mock_run:
            # Mock successful subscription set and cluster list
            mock_run.side_effect = [
                True,
                mock_clusters,
            ]  # First call sets subscription, second lists clusters

            result = loader.get_aks_clusters("test-subscription-id")
            assert len(result) == 2
            assert result[0]["name"] == "mock-aks-cluster-01"
            assert result[1]["name"] == "test-cluster"

    def test_get_aks_clusters_no_clusters(self, loader: Any) -> None:
        """Test AKS cluster retrieval with no clusters"""
        with patch.object(loader, "run_az_command") as mock_run:
            mock_run.side_effect = [True, []]  # Empty cluster list

            result = loader.get_aks_clusters("test-subscription-id")
            assert len(result) == 0

    def test_fetch_cluster_credentials_dry_run(self, loader: Any) -> None:
        """Test credential fetching in dry-run mode"""
        cluster = {"name": "test-cluster", "resourceGroup": "test-rg"}

        with patch.object(loader, "run_az_command", return_value=True), patch.object(
            loader, "run_kubelogin_command", return_value=True
        ):

            result = loader.fetch_cluster_credentials("test-sub-id", cluster)
            assert result is True

    def test_fetch_cluster_credentials_success(self, prod_loader: Any) -> None:
        """Test successful credential fetching"""
        cluster = {"name": "test-cluster", "resourceGroup": "test-rg"}

        with patch.object(prod_loader, "run_az_command", return_value=True), patch.object(
            prod_loader, "run_kubelogin_command", return_value=True
        ):

            result = prod_loader.fetch_cluster_credentials("test-sub-id", cluster)
            assert result is True

    def test_load_all_credentials_integration(
        self, loader: Any, mock_subscriptions: Any, mock_clusters: Any
    ) -> None:
        """Test the full workflow integration"""
        with patch.object(
            loader, "get_subscriptions", return_value=mock_subscriptions
        ), patch.object(loader, "get_aks_clusters", return_value=mock_clusters), patch.object(
            loader, "fetch_cluster_credentials", return_value=True
        ):

            # This should run without errors
            loader.load_all_credentials()
            # No assertions needed - just verify it doesn't crash


if __name__ == "__main__":
    pytest.main([__file__])
