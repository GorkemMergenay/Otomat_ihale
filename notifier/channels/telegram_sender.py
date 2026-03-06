from __future__ import annotations

import httpx

from app.core.config import settings
from notifier.interfaces import NotificationSender


class TelegramSender(NotificationSender):
    def send(self, recipient: str, subject: str, message: str) -> tuple[bool, str | None]:
        if not settings.telegram_enabled:
            return False, "Telegram channel disabled"
        if not settings.telegram_bot_token:
            return False, "Missing Telegram bot token"

        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": recipient,
            "text": f"{subject}\n\n{message}",
            "disable_web_page_preview": True,
        }

        try:
            with httpx.Client(timeout=10) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
            return True, None
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)
