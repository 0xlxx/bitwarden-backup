from __future__ import annotations

import keyring

SERVICE = "bitwarden-backup"


def _key(name: str) -> str:
    return f"{SERVICE}/{name}"


def set_credential(name: str, value: str) -> None:
    keyring.set_password(SERVICE, _key(name), value)


def get_credential(name: str) -> str | None:
    return keyring.get_password(SERVICE, _key(name))


def delete_credential(name: str) -> None:
    try:
        keyring.delete_password(SERVICE, _key(name))
    except keyring.errors.PasswordDeleteError:
        pass


def save_api_credentials(client_id: str, client_secret: str) -> None:
    set_credential("client_id", client_id)
    set_credential("client_secret", client_secret)


def get_api_credentials() -> tuple[str | None, str | None]:
    return get_credential("client_id"), get_credential("client_secret")


def save_encrypt_password(password: str) -> None:
    set_credential("encrypt_password", password)


def get_encrypt_password() -> str | None:
    return get_credential("encrypt_password")


def clear_all() -> None:
    for name in ("client_id", "client_secret", "encrypt_password"):
        delete_credential(name)
