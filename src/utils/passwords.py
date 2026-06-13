"""Password hashing and verification (stdlib only)."""

import hashlib
import hmac
import secrets

_PBKDF2_ITERATIONS = 120_000


def hash_password(password: str) -> tuple[str, str]:
    salt = secrets.token_hex(16)
    digest = _derive(password, salt)
    return digest, salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    expected = _derive(password, salt)
    return hmac.compare_digest(expected, password_hash)


def _derive(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        _PBKDF2_ITERATIONS,
    ).hex()
