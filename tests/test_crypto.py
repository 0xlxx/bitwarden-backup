from bitwarden_backup.crypto import encrypt, decrypt


def test_roundtrip():
    plaintext = b"hello world"
    ciphertext = encrypt(plaintext, "mypassword")
    assert ciphertext != plaintext
    assert decrypt(ciphertext, "mypassword") == plaintext


def test_wrong_password_fails():
    ciphertext = encrypt(b"secret", "correct")
    try:
        decrypt(ciphertext, "wrong")
        assert False, "should have raised"
    except Exception:
        pass


def test_empty_plaintext():
    ciphertext = encrypt(b"", "password")
    assert decrypt(ciphertext, "password") == b""


def test_large_plaintext():
    data = b"x" * 100_000
    ciphertext = encrypt(data, "password")
    assert decrypt(ciphertext, "password") == data


def test_unicode_password():
    plaintext = b"data"
    ciphertext = encrypt(plaintext, "中文密码🔐")
    assert decrypt(ciphertext, "中文密码🔐") == plaintext


def test_different_outputs():
    """Same plaintext, same password should produce different ciphertext (random salt/nonce)."""
    c1 = encrypt(b"data", "password")
    c2 = encrypt(b"data", "password")
    assert c1 != c2
