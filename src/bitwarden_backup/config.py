from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG: dict[str, Any] = {
    "output_dir": "~/.local/share/bitwarden-backup",
    "retention_days": 7,
    "backup_time": "02:00",
}


def _config_dir() -> Path:
    path = Path("~/.config/bitwarden-backup").expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_path() -> Path:
    return _config_dir() / "config.yaml"


def load_config() -> dict[str, Any]:
    cfg = dict(DEFAULT_CONFIG)
    path = config_path()
    if path.exists():
        with open(path) as f:
            file_cfg = yaml.safe_load(f) or {}
        cfg.update(file_cfg)
    return cfg


def save_config(cfg: dict[str, Any]) -> None:
    with open(config_path(), "w") as f:
        yaml.safe_dump(cfg, f, default_flow_style=False)
    os.chmod(config_path(), 0o600)


def output_dir(cfg: dict[str, Any] | None = None) -> Path:
    if cfg is None:
        cfg = load_config()
    path = Path(cfg["output_dir"]).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o700)
    return path
