from __future__ import annotations

import base64
import hashlib
import hmac
import secrets


PBKDF2_ALGORITHM = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 260_000
SALT_BYTES = 16


def hash_password(password: str, iterations: int = PBKDF2_ITERATIONS) -> str:
    salt = secrets.token_hex(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    digest_b64 = base64.urlsafe_b64encode(digest).decode("utf-8")
    return f"{PBKDF2_ALGORITHM}${iterations}${salt}${digest_b64}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_raw, salt, digest_b64 = password_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != PBKDF2_ALGORITHM:
        return False

    if not iterations_raw.isdigit():
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations_raw),
    )
    expected = base64.urlsafe_b64decode(_pad_base64(digest_b64))
    return hmac.compare_digest(digest, expected)


def _pad_base64(value: str) -> str:
    return value + "=" * ((4 - len(value) % 4) % 4)
