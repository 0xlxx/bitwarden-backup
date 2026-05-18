# bitwarden-backup

Automated daily encrypted backups for your Bitwarden vault.

## Install

```bash
brew tap 0xlxx/homebrew-tap
brew install bitwarden-backup
```

Requires Bitwarden CLI — `brew install bitwarden-cli` if not already installed.

## Usage

One-time setup (interactive, ~30 seconds):

```bash
bw-backup setup
```

You'll need a Bitwarden API key. Create one at:
https://vault.bitwarden.com/#/settings/security/security-keys

After setup, backups run automatically every day at 02:00. Files are stored in
`~/.local/share/bitwarden-backup/`.

Manual commands:

```bash
bw-backup run       # Run a backup now
bw-backup list      # List all backups
bw-backup status    # Show configuration and schedule status
bw-backup teardown  # Remove configuration and schedule
```

## Backup format

Exports your vault as unencrypted JSON, then encrypts it locally with
AES-256-GCM using a password you provide during setup. Encryption key is
derived via PBKDF2 (600,000 iterations).

This follows the [Bitwarden official backup guide](https://bitwarden.com/resources/guide-how-to-create-and-store-a-backup-of-your-bitwarden-vault/)
recommendation: export unencrypted JSON, then encrypt yourself.
The `encrypted_json` format is tied to your Bitwarden account and cannot be
imported into other password managers.

## Uninstall

```bash
bw-backup teardown
brew uninstall bitwarden-backup
```

Backup files are kept in `~/.local/share/bitwarden-backup/` — delete them
manually if desired.
