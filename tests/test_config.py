import os
from pathlib import Path

import yaml

from bitwarden_backup.config import load_config, save_config, output_dir, DEFAULT_CONFIG


def test_default_config():
    """Without a config file, returns defaults."""
    cfg = load_config()
    assert cfg["retention_days"] == 7
    assert "output_dir" in cfg


def test_custom_config(temp_config_dir):
    """Config file values override defaults."""
    config_path, backup_dir = temp_config_dir
    cfg_data = {"output_dir": str(backup_dir), "retention_days": 14}
    with open(config_path, "w") as f:
        yaml.safe_dump(cfg_data, f)

    # Patch config_path to use our temp file
    import bitwarden_backup.config as mod
    original = mod.config_path
    mod.config_path = lambda: config_path
    try:
        cfg = load_config()
        assert cfg["retention_days"] == 14
        assert cfg["output_dir"] == str(backup_dir)
    finally:
        mod.config_path = original


def test_output_dir_creates_and_sets_perms(temp_config_dir):
    config_path, backup_dir = temp_config_dir
    cfg = {"output_dir": str(backup_dir), "retention_days": 7}

    d = output_dir(cfg)
    assert d == backup_dir.resolve()
    assert d.exists()


def test_save_config_creates_file(temp_config_dir):
    config_path, backup_dir = temp_config_dir
    import bitwarden_backup.config as mod
    original = mod.config_path
    mod.config_path = lambda: config_path
    try:
        save_config({"output_dir": str(backup_dir), "retention_days": 30})
        cfg = load_config()
        assert cfg["retention_days"] == 30
    finally:
        mod.config_path = original
