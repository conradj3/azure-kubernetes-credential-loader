"""Simple functionality tests for AKS Credential Loader."""

# type: ignore
# pylint: disable=import-error,unused-import

import pytest

try:
    from aks_credential_loader import AKSCredentialLoader  # type: ignore
except ImportError:
    # Skip tests if module can't be imported
    AKSCredentialLoader = None  # type: ignore
    pytest.skip("aks_credential_loader module not found", allow_module_level=True)


def test_create_loader() -> None:
    """Test that we can create an AKSCredentialLoader instance"""
    if AKSCredentialLoader is None:
        pytest.skip("AKSCredentialLoader not available")

    loader = AKSCredentialLoader(dry_run=True)  # type: ignore
    assert loader is not None
    assert loader.dry_run is True  # type: ignore


def test_create_production_loader() -> None:
    """Test that we can create a production AKSCredentialLoader instance"""
    if AKSCredentialLoader is None:
        pytest.skip("AKSCredentialLoader not available")

    loader = AKSCredentialLoader(dry_run=False)  # type: ignore
    assert loader is not None
    assert loader.dry_run is False  # type: ignore


if __name__ == "__main__":
    pytest.main([__file__])
