from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Tuple

from app.core.config import settings
from app.models.enums import UserRole


@dataclass
class AccessTokenPayload:
    user_id: int
    email: str
    role: UserRole
    issued_at: datetime
    expires_at: datetime


def create_access_token(user_id: int, email: str, role: UserRole) -> Tuple[str, datetime]:
    now = int(time.time())
    expires_at = now + (settings.auth_token_ttl_minutes * 60)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role.value,
        "iat": now,
        "exp": expires_at,
    }
    payload_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    signature = hmac.new(settings.auth_secret_key.encode("utf-8"), payload_bytes, hashlib.sha256).digest()
    token = f"{_to_base64(payload_bytes)}.{_to_base64(signature)}"
    return token, datetime.fromtimestamp(expires_at, tz=timezone.utc)


def decode_access_token(token: str) -> Optional[AccessTokenPayload]:
    try:
        payload_part, signature_part = token.split(".", 1)
        payload_bytes = _from_base64(payload_part)
        signature = _from_base64(signature_part)
    except Exception:  # noqa: BLE001
        return None

    expected_signature = hmac.new(settings.auth_secret_key.encode("utf-8"), payload_bytes, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected_signature):
        return None

    try:
        data = json.loads(payload_bytes.decode("utf-8"))
        exp = int(data["exp"])
        iat = int(data["iat"])
        user_id = int(data["sub"])
        email = str(data["email"])
        role = UserRole(str(data["role"]))
    except Exception:  # noqa: BLE001
        return None

    now = int(time.time())
    if exp <= now:
        return None

    return AccessTokenPayload(
        user_id=user_id,
        email=email,
        role=role,
        issued_at=datetime.fromtimestamp(iat, tz=timezone.utc),
        expires_at=datetime.fromtimestamp(exp, tz=timezone.utc),
    )


def _to_base64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")


def _from_base64(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(value + padding)
