from __future__ import annotations

import logging
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import click

from bitwarden_backup.config import load_config, save_config, output_dir
from bitwarden_backup.credentials import (
    save_api_credentials,
    save_encrypt_password,
    save_master_password,
    get_api_credentials,
    get_encrypt_password,
    clear_all,
)
from bitwarden_backup.backup import run_backup, BackupError, BW_PATH
from bitwarden_backup.schedule import install as install_schedule
from bitwarden_backup.schedule import uninstall as uninstall_schedule
from bitwarden_backup.schedule import status as schedule_status

logger = logging.getLogger(__name__)


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def main(verbose: bool = False) -> None:
    _setup_logging(verbose)


@main.command()
def setup() -> None:
    """Interactive first-time setup."""

    click.echo()
    click.secho("  Bitwarden Backup Setup", bold=True)
    click.echo("  " + "─" * 30)
    click.echo()

    # Check bw CLI
    if shutil.which(BW_PATH) is None:
        click.secho(f"  Bitwarden CLI not found at {BW_PATH}", fg="red")
        click.echo("  Install with: brew install bitwarden-cli")
        sys.exit(1)
    click.secho("  Bitwarden CLI detected", fg="green")
    click.echo()

    # API credentials
    click.echo("  Create an API Key at:")
    click.secho("  https://vault.bitwarden.com/#/settings/security/security-keys", fg="blue")
    click.echo()

    client_id = click.prompt("  Client ID").strip()
    client_secret = click.prompt("  Client Secret").strip()
    click.echo()

    # Vault master password (needed to unlock vault for export)
    click.echo("  Bitwarden master password (required to unlock vault)")
    while True:
        master_pwd = click.prompt("  Master password", hide_input=True)
        confirm = click.prompt("  Confirm master password", hide_input=True)
        if master_pwd == confirm:
            break
        click.secho("  Passwords don't match, try again.", fg="red")
    click.echo()

    # Backup encryption password
    click.echo("  Backup encryption password (do NOT use your Bitwarden master password)")
    while True:
        pwd = click.prompt("  Password", hide_input=True)
        confirm = click.prompt("  Confirm password", hide_input=True)
        if pwd == confirm:
            break
        click.secho("  Passwords don't match, try again.", fg="red")
    click.echo()

    # Retention
    retention = click.prompt("  Keep backups for how many days?", type=int, default=7)
    click.echo()

    # Save everything
    save_config({
        "output_dir": str(Path("~/.local/share/bitwarden-backup").expanduser()),
        "retention_days": retention,
    })
    save_api_credentials(client_id, client_secret)
    save_master_password(master_pwd)
    save_encrypt_password(pwd)

    click.secho("  Configuration saved", fg="green")

    # Install schedule
    try:
        install_schedule()
        click.secho("  Schedule installed (daily at 02:00)", fg="green")
    except Exception as e:
        click.secho(f"  Warning: failed to install schedule: {e}", fg="yellow")

    # Test backup
    click.echo()
    click.echo("  Running first test backup...")
    try:
        path = run_backup()
        click.secho(f"  Test backup successful: {path.name}", fg="green")
    except BackupError as e:
        click.secho(f"  Test backup failed: {e}", fg="red")
        click.echo("  Setup is incomplete. Fix the issue and run 'bw-backup run' to verify.")
        sys.exit(1)

    click.echo()
    click.secho("  All set! Backups will run automatically every day at 02:00.", bold=True)
    click.echo(f"  Backup location: {output_dir()}")
    click.echo()


@main.command()
def run() -> None:
    """Run a manual backup now."""
    try:
        path = run_backup()
        click.echo(f"Backup saved: {path}")
    except BackupError as e:
        click.secho(f"Backup failed: {e}", fg="red", err=True)
        sys.exit(1)


@main.command()
def list() -> None:
    """List all backups."""
    cfg = load_config()
    d = output_dir(cfg)

    files = sorted(d.glob("bw-backup_*.json.enc"), reverse=True)
    if not files:
        click.echo("No backups found.")
        return

    for f in files:
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        size_kb = f.stat().st_size / 1024
        click.echo(f"  {f.name}  {size_kb:.1f} KB  {mtime.strftime('%Y-%m-%d %H:%M')}")


@main.command()
def status() -> None:
    """Show backup status."""
    cfg = load_config()
    d = output_dir(cfg)

    client_id, _ = get_api_credentials()
    has_password = get_encrypt_password() is not None
    sched = schedule_status()

    click.echo(f"  API credentials: {'configured' if client_id else 'missing'}")
    click.echo(f"  Encryption password: {'configured' if has_password else 'missing'}")
    click.echo(f"  Backup directory: {d}")
    click.echo(f"  Retention: {cfg['retention_days']} days")

    files = sorted(d.glob("bw-backup_*.json.enc"), reverse=True)
    click.echo(f"  Backups stored: {len(files)}")
    if files:
        mtime = datetime.fromtimestamp(files[0].stat().st_mtime, tz=timezone.utc)
        click.echo(f"  Last backup: {mtime.strftime('%Y-%m-%d %H:%M')}")

    click.echo(f"  Schedule: {'installed' if sched.get('installed') else 'not installed'}")


@main.command()
def teardown() -> None:
    """Remove all configuration, credentials, and schedule."""
    if not click.confirm("Remove all configuration, credentials, and the backup schedule?"):
        return

    try:
        uninstall_schedule()
    except Exception:
        pass

    clear_all()

    import bitwarden_backup.config as cfg_mod
    path = cfg_mod.config_path()
    if path.exists():
        path.unlink()

    click.echo("All configuration and credentials removed. Backup files are kept.")
