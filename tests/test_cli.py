import json
from pathlib import Path
from unittest import mock

import pytest
from click.testing import CliRunner

from bitwarden_backup.cli import main


@pytest.fixture
def runner():
    return CliRunner()


def test_help(runner):
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "setup" in result.output
    assert "run" in result.output
    assert "list" in result.output
    assert "status" in result.output


def test_list_empty(runner, temp_config_dir, mock_keyring):
    config_path, backup_dir = temp_config_dir
    import bitwarden_backup.config as cfg_mod
    orig = cfg_mod.config_path
    cfg_mod.config_path = lambda: config_path

    try:
        result = runner.invoke(main, ["list"])
        assert result.exit_code == 0
        assert "No backups found" in result.output
    finally:
        cfg_mod.config_path = orig


def test_list_with_backups(runner, temp_backup_dir, mock_keyring):
    (temp_backup_dir / "bw-backup_2026-05-19_120000.json.enc").write_text("encrypted")

    with mock.patch("bitwarden_backup.cli.output_dir", return_value=temp_backup_dir.resolve()):
        with mock.patch("bitwarden_backup.cli.load_config", return_value={
            "output_dir": str(temp_backup_dir), "retention_days": 7
        }):
            result = runner.invoke(main, ["list"])
            assert result.exit_code == 0
            assert "bw-backup_" in result.output


def test_status(runner, temp_config_dir, mock_keyring, mock_credentials):
    config_path, backup_dir = temp_config_dir

    import bitwarden_backup.config as cfg_mod
    import bitwarden_backup.config as config_mod
    orig_path = cfg_mod.config_path
    orig_output = config_mod.output_dir
    cfg_mod.config_path = lambda: config_path
    config_mod.output_dir = lambda cfg=None: backup_dir.resolve()

    try:
        with mock.patch("bitwarden_backup.cli.schedule_status",
                        return_value={"platform": "Darwin", "installed": False, "running": False}):
            result = runner.invoke(main, ["status"])
            assert result.exit_code == 0
            assert "configured" in result.output
    finally:
        cfg_mod.config_path = orig_path
        config_mod.output_dir = orig_output


def test_teardown_confirm(runner, mock_keyring, mock_credentials):
    with mock.patch("bitwarden_backup.cli.uninstall_schedule"):
        with mock.patch("bitwarden_backup.cli.clear_all"):
            result = runner.invoke(main, ["teardown"], input="y\n")
            assert result.exit_code == 0


def test_teardown_decline(runner, mock_keyring, mock_credentials):
    result = runner.invoke(main, ["teardown"], input="n\n")
    assert result.exit_code == 0
