from __future__ import annotations

import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)

BACKUP_PATTERN = "bw-backup_*.json.enc"


def cleanup(backup_dir: Path, retention_days: int) -> list[Path]:
    cutoff = time.time() - retention_days * 86400
    deleted: list[Path] = []

    for path in sorted(backup_dir.glob(BACKUP_PATTERN)):
        if path.stat().st_mtime < cutoff:
            path.unlink()
            deleted.append(path)
            logger.info(f"Deleted old backup: {path.name}")

    return deleted
