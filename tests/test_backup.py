import json
import os
from pathlib import Path
from unittest import mock

import pytest

from bitwarden_backup.backup import run_backup, BackupError
from bitwarden_backup.config import save_config


def _make_subprocess_fn():
    """Create a mock subprocess.run that returns realistic bw responses."""
    def bw_run(args, **kwargs):
        result = mock.MagicMock()
        result.returncode = 0
        cmd = " ".join(args) if isinstance(args, list) else args

        if "login --apikey" in cmd:
            result.stdout = "test_session_key_abc123\n"
        elif "sync" in cmd:
            result.stdout = ""
        elif "export" in cmd:
            vault = {"encrypted": False, "items": [{"name": "test login"}]}
            result.stdout = json.dumps(vault)
        elif "logout" in cmd:
            result.stdout = ""
        else:
            result.stdout = ""
        result.stderr = ""
        return result
    return bw_run


def test_run_backup_success(temp_config_dir, mock_keyring, mock_subprocess, mock_credentials):
    config_path, backup_dir = temp_config_dir
    save_config({"output_dir": str(backup_dir), "retention_days": 7})

    # Override config_path to use temp dir
    import bitwarden_backup.config as cfg_mod
    import bitwarden_backup.backup as backup_mod
    orig_config_path = cfg_mod.config_path
    orig_output_dir = backup_mod.output_dir

    cfg_mod.config_path = lambda: config_path
    backup_mod.output_dir = lambda cfg=None: backup_dir.resolve()

    mock_subprocess.side_effect = _make_subprocess_fn()

    try:
        path = run_backup()
        assert path.exists()
        assert path.name.endswith(".json.enc")
        assert path.suffix == ".enc"
    finally:
        cfg_mod.config_path = orig_config_path
        backup_mod.output_dir = orig_output_dir


def test_run_backup_no_credentials(mock_keyring):
    from bitwarden_backup.credentials import clear_all
    clear_all()
    with pytest.raises(BackupError, match="API credentials not found"):
        run_backup()


def test_run_backup_bw_login_fails(temp_config_dir, mock_keyring, mock_subprocess, mock_credentials):
    config_path, backup_dir = temp_config_dir
    save_config({"output_dir": str(backup_dir), "retention_days": 7})

    import bitwarden_backup.config as cfg_mod
    import bitwarden_backup.backup as backup_mod
    orig_config_path = cfg_mod.config_path
    orig_output_dir = backup_mod.output_dir
    cfg_mod.config_path = lambda: config_path
    backup_mod.output_dir = lambda cfg=None: backup_dir.resolve()

    def fail_login(args, **kwargs):
        result = mock.MagicMock()
        cmd = " ".join(args) if isinstance(args, list) else args
        if "login" in cmd:
            result.returncode = 1
            result.stderr = "Invalid API key"
            result.stdout = ""
            return result
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        return result

    mock_subprocess.side_effect = fail_login

    try:
        with pytest.raises(BackupError, match="Invalid API key"):
            run_backup()
    finally:
        cfg_mod.config_path = orig_config_path
        backup_mod.output_dir = orig_output_dir


def test_run_backup_permissions(temp_config_dir, mock_keyring, mock_subprocess, mock_credentials):
    config_path, backup_dir = temp_config_dir
    save_config({"output_dir": str(backup_dir), "retention_days": 7})

    import bitwarden_backup.config as cfg_mod
    import bitwarden_backup.backup as backup_mod
    orig_config_path = cfg_mod.config_path
    orig_output_dir = backup_mod.output_dir
    cfg_mod.config_path = lambda: config_path
    backup_mod.output_dir = lambda cfg=None: backup_dir.resolve()

    mock_subprocess.side_effect = _make_subprocess_fn()

    try:
        path = run_backup()
        stat = os.stat(path)
        assert stat.st_mode & 0o777 == 0o600
    finally:
        cfg_mod.config_path = orig_config_path
        backup_mod.output_dir = orig_output_dir
