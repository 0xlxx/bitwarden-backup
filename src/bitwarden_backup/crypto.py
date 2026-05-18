from __future__ import annotations

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

SALT_LEN = 16
NONCE_LEN = 12
PBKDF2_ITERATIONS = 600_000


def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt(plaintext: bytes, password: str) -> bytes:
    salt = os.urandom(SALT_LEN)
    key = _derive_key(password, salt)
    nonce = os.urandom(NONCE_LEN)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)
    return salt + nonce + ciphertext


def decrypt(data: bytes, password: str) -> bytes:
    salt = data[:SALT_LEN]
    nonce = data[SALT_LEN : SALT_LEN + NONCE_LEN]
    ciphertext = data[SALT_LEN + NONCE_LEN :]
    key = _derive_key(password, salt)
    return AESGCM(key).decrypt(nonce, ciphertext, None)
