from __future__ import annotations

import logging
import os
import platform
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

LAUNCHD_LABEL = "com.bitwarden-backup"
LAUNCHD_PLIST = Path(f"~/Library/LaunchAgents/{LAUNCHD_LABEL}.plist").expanduser()

CRON_MARKER = "# bitwarden-backup"
def _cron_job(hour: int, minute: int) -> str:
    return f"{minute} {hour} * * * {{python}} -m bitwarden_backup run"


def _python_path() -> str:
    return sys.executable


def install(time_str: str = "02:00") -> None:
    hour, minute = _parse_time(time_str)
    system = platform.system()
    if system == "Darwin":
        _install_launchd(hour, minute)
    elif system == "Linux":
        _install_cron(hour, minute)
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def _parse_time(time_str: str) -> tuple[int, int]:
    parts = time_str.strip().split(":")
    return int(parts[0]), int(parts[1])


def uninstall() -> None:
    system = platform.system()
    if system == "Darwin":
        _uninstall_launchd()
    elif system == "Linux":
        _uninstall_cron()


def status() -> dict:
    system = platform.system()
    if system == "Darwin":
        return _status_launchd()
    elif system == "Linux":
        return _status_cron()
    return {"platform": system, "installed": False}


def _install_launchd(hour: int = 2, minute: int = 0) -> None:
    python = _python_path()
    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{LAUNCHD_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python}</string>
        <string>-m</string>
        <string>bitwarden_backup</string>
        <string>run</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>{hour}</integer>
        <key>Minute</key>
        <integer>{minute}</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{Path('~/.local/share/bitwarden-backup/backup.log').expanduser()}</string>
    <key>StandardErrorPath</key>
    <string>{Path('~/.local/share/bitwarden-backup/backup.log').expanduser()}</string>
    <key>RunAtLoad</key>
    <false/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>"""
    LAUNCHD_PLIST.parent.mkdir(parents=True, exist_ok=True)
    LAUNCHD_PLIST.write_text(plist)

    subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{LAUNCHD_LABEL}"],
                   capture_output=True)
    subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(LAUNCHD_PLIST)],
                   check=True)
    logger.info("Launchd job installed (daily at 02:00)")


def _uninstall_launchd() -> None:
    subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{LAUNCHD_LABEL}"],
                   capture_output=True)
    if LAUNCHD_PLIST.exists():
        LAUNCHD_PLIST.unlink()
    logger.info("Launchd job removed")


def _status_launchd() -> dict:
    result = subprocess.run(
        ["launchctl", "print", f"gui/{os.getuid()}/{LAUNCHD_LABEL}"],
        capture_output=True, text=True
    )
    installed = LAUNCHD_PLIST.exists()
    running = result.returncode == 0
    return {"platform": "Darwin", "installed": installed, "running": running}


def _install_cron(hour: int = 2, minute: int = 0) -> None:
    python = _python_path()
    job_line = f"{_cron_job(hour, minute).format(python=python)} {CRON_MARKER}"

    try:
        existing = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True
        ).stdout
    except subprocess.CalledProcessError:
        existing = ""

    lines = [l for l in existing.splitlines() if CRON_MARKER not in l]
    lines.append(job_line)
    if lines and lines[0] == "":
        lines.pop(0)

    subprocess.run(["crontab", "-"], input="\n".join(lines) + "\n",
                   text=True, check=True)
    logger.info("Cron job installed (daily at 02:00)")


def _uninstall_cron() -> None:
    try:
        existing = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True
        ).stdout
    except subprocess.CalledProcessError:
        return

    lines = [l for l in existing.splitlines() if CRON_MARKER not in l]
    if lines:
        subprocess.run(["crontab", "-"], input="\n".join(lines) + "\n",
                       text=True, check=True)
    else:
        subprocess.run(["crontab", "-r"], check=True)
    logger.info("Cron job removed")


def _status_cron() -> dict:
    try:
        existing = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True
        ).stdout
    except subprocess.CalledProcessError:
        return {"platform": "Linux", "installed": False, "running": False}

    installed = CRON_MARKER in existing
    return {"platform": "Linux", "installed": installed, "running": installed}
