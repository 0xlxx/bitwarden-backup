# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
.venv/bin/python -m pytest tests/ -v

# Run a single test file
.venv/bin/python -m pytest tests/test_crypto.py -v

# Run the CLI
.venv/bin/python -m bitwarden_backup --help

# Install dev deps
uv pip install -e ".[dev]" --python .venv/bin/python
```

## Architecture

```
CLI (Click) → backup.py → subprocess (bw CLI) + crypto (AES-256-GCM)
```

- `cli.py` — Click commands: `setup`, `run`, `list`, `status`, `teardown`
- `backup.py` — Core: `bw login --apikey` → `bw sync` → `bw export --format json` → AES encrypt → save (.json.enc)
- `crypto.py` — AES-256-GCM encryption with PBKDF2 key derivation (600k iterations)
- `credentials.py` — System keychain (keyring) for API client_id/secret and backup password
- `config.py` — YAML config for non-sensitive settings (output_dir, retention_days)
- `retention.py` — Deletes backups older than N days
- `schedule.py` — macOS launchd / Linux cron install/uninstall/status

## Key design decisions

- **Unencrypted JSON export + AES encrypt** per Bitwarden official backup guide (not `encrypted_json` format which ties to account)
- **Credentials in system keychain**, never in config file
- **`setup` command** interactively gathers all config, installs schedule, runs test backup
- **0o600** on backup files, **0o700** on backup directory
- **bw path** hardcoded to `/opt/homebrew/bin/bw` (macOS Homebrew default)
