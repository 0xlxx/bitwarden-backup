from __future__ import annotations

import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from bitwarden_backup.config import load_config, output_dir
from bitwarden_backup.credentials import get_api_credentials, get_encrypt_password
from bitwarden_backup.crypto import encrypt
from bitwarden_backup.retention import cleanup

logger = logging.getLogger(__name__)

BW_PATH = "/opt/homebrew/bin/bw"


class BackupError(Exception):
    pass


def _run(args: list[str], env: dict[str, str] | None = None, timeout: int = 120) -> str:
    """Run a bw command, return stdout. Raises BackupError on failure."""
    cmd = [BW_PATH, *args]
    merged_env = {**os.environ, "BW_NOINTERACTION": "true"}
    if env:
        merged_env.update(env)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=merged_env,
            timeout=timeout,
        )
    except FileNotFoundError:
        raise BackupError(
            "Bitwarden CLI not found. Install with: brew install bitwarden-cli"
        )
    except subprocess.TimeoutExpired:
        raise BackupError(f"Command timed out after {timeout}s: bw {' '.join(args)}")

    if result.returncode != 0:
        msg = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise BackupError(f"bw {' '.join(args)} failed: {msg}")

    return result.stdout


def run_backup() -> Path:
    client_id, client_secret = get_api_credentials()
    if not client_id or not client_secret:
        raise BackupError(
            "API credentials not found. Run 'bw-backup setup' first."
        )

    password = get_encrypt_password()
    if not password:
        raise BackupError(
            "Encryption password not found. Run 'bw-backup setup' first."
        )

    cfg = load_config()
    out_dir = output_dir(cfg)

    # Build env with API credentials for login
    login_env = {
        "BW_CLIENTID": client_id,
        "BW_CLIENTSECRET": client_secret,
    }

    logger.info("Logging in to Bitwarden...")
    session_key = _run(["login", "--apikey", "--raw"], env=login_env).strip()
    if not session_key:
        raise BackupError("Failed to obtain session key")

    session_env = {"BW_SESSION": session_key}

    try:
        logger.info("Syncing vault...")
        _run(["sync"], env=session_env, timeout=60)

        logger.info("Exporting vault...")
        json_data = _run(["export", "--format", "json", "--raw"], env=session_env)

        logger.info("Encrypting backup...")
        encrypted = encrypt(json_data.encode("utf-8"), password)

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
        filename = f"bw-backup_{timestamp}.json.enc"
        filepath = out_dir / filename

        with open(filepath, "wb") as f:
            f.write(encrypted)
        os.chmod(filepath, 0o600)

        logger.info(f"Backup saved: {filepath}")

        logger.info("Cleaning up old backups...")
        cleanup(out_dir, cfg["retention_days"])

        return filepath
    finally:
        logger.info("Logging out...")
        try:
            _run(["logout"], env=session_env, timeout=10)
        except BackupError:
            pass  # best-effort logout
