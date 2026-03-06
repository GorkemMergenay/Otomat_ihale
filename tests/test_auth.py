from __future__ import annotations

from app.core.config import settings
from app.core.passwords import hash_password
from app.models.user import User


def test_login_and_me_endpoints(client, db_session) -> None:
    db_session.add(
        User(
            name="Test Admin",
            email="admin@example.com",
            role="admin",
            is_active=True,
            password_hash=hash_password("StrongPass123!"),
        )
    )
    db_session.commit()

    previous_auth_disabled = settings.auth_disabled
    previous_secret = settings.auth_secret_key
    settings.auth_disabled = False
    settings.auth_secret_key = "test-secret"
    try:
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@example.com", "password": "StrongPass123!"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        assert token

        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_response.status_code == 200
        assert me_response.json()["user"]["role"] == "admin"
        assert me_response.json()["user"]["email"] == "admin@example.com"
    finally:
        settings.auth_disabled = previous_auth_disabled
        settings.auth_secret_key = previous_secret


def test_login_rejects_invalid_password(client, db_session) -> None:
    db_session.add(
        User(
            name="Test Analyst",
            email="analyst@example.com",
            role="analyst",
            is_active=True,
            password_hash=hash_password("StrongPass123!"),
        )
    )
    db_session.commit()

    previous_auth_disabled = settings.auth_disabled
    settings.auth_disabled = False
    try:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "analyst@example.com", "password": "WrongPass123!"},
        )
        assert response.status_code == 401
    finally:
        settings.auth_disabled = previous_auth_disabled
