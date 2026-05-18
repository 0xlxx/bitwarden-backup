import os
import time
from pathlib import Path

from bitwarden_backup.retention import cleanup


def _make_old(path: Path, days: int) -> None:
    path.write_text("test")
    mtime = time.time() - days * 86400
    os.utime(path, (mtime, mtime))


def test_no_backups(temp_backup_dir):
    deleted = cleanup(temp_backup_dir, 7)
    assert deleted == []


def test_keeps_recent_backups(temp_backup_dir):
    f = temp_backup_dir / "bw-backup_2026-05-19_120000.json.enc"
    _make_old(f, 1)
    deleted = cleanup(temp_backup_dir, 7)
    assert deleted == []


def test_deletes_old_backups(temp_backup_dir):
    f = temp_backup_dir / "bw-backup_2026-05-01_120000.json.enc"
    _make_old(f, 30)
    deleted = cleanup(temp_backup_dir, 7)
    assert len(deleted) == 1
    assert not f.exists()


def test_mixed_old_and_new(temp_backup_dir):
    recent = temp_backup_dir / "bw-backup_2026-05-18_120000.json.enc"
    old = temp_backup_dir / "bw-backup_2026-04-01_120000.json.enc"
    _make_old(recent, 2)
    _make_old(old, 50)
    deleted = cleanup(temp_backup_dir, 7)
    assert len(deleted) == 1
    assert not old.exists()
    assert recent.exists()


def test_ignores_non_backup_files(temp_backup_dir):
    other = temp_backup_dir / "readme.txt"
    other.write_text("hello")
    _make_old(other, 100)
    deleted = cleanup(temp_backup_dir, 1)
    assert deleted == []
    assert other.exists()
