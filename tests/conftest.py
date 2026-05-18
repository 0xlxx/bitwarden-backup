from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest
import yaml


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory with a config.yaml."""
    with tempfile.TemporaryDirectory() as tmp:
        config_dir = Path(tmp) / "config"
        config_dir.mkdir()
        config_path = config_dir / "config.yaml"
        backup_dir = Path(tmp) / "backups"
        backup_dir.mkdir()
        yield config_path, backup_dir


@pytest.fixture
def temp_backup_dir():
    """Create a temporary backup directory."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def mock_keyring():
    """Mock keyring to store credentials in memory."""
    storage = {}
    with mock.patch("bitwarden_backup.credentials.keyring") as m:
        m.set_password = lambda service, key, value: storage.__setitem__(key, value)
        m.get_password = lambda service, key: storage.get(key)
        m.delete_password = lambda service, key: storage.pop(key, None)
        m.errors.PasswordDeleteError = Exception
        yield m


@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run for bw commands."""
    with mock.patch("subprocess.run") as m:
        yield m


@pytest.fixture
def mock_credentials(mock_keyring):
    """Set up test credentials in mock keyring."""
    from bitwarden_backup.credentials import save_api_credentials, save_encrypt_password
    save_api_credentials("test_client_id", "test_client_secret")
    save_encrypt_password("test-password-123")
    yield
    from bitwarden_backup.credentials import clear_all
    clear_all()


@pytest.fixture
def sample_config_yaml(temp_config_dir):
    """Write a sample config.yaml and return the config file path."""
    config_path, backup_dir = temp_config_dir
    cfg = {
        "output_dir": str(backup_dir),
        "retention_days": 7,
    }
    with open(config_path, "w") as f:
        yaml.safe_dump(cfg, f)
    return config_path, backup_dir
