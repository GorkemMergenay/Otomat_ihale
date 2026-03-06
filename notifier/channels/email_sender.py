from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.core.config import settings
from notifier.interfaces import NotificationSender


class EmailSender(NotificationSender):
    def send(self, recipient: str, subject: str, message: str) -> tuple[bool, str | None]:
        if not settings.email_enabled:
            return False, "Email channel disabled"

        email = EmailMessage()
        email["From"] = settings.email_from
        email["To"] = recipient
        email["Subject"] = subject
        email.set_content(message)

        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                if settings.smtp_username:
                    smtp.starttls()
                    smtp.login(settings.smtp_username, settings.smtp_password)
                smtp.send_message(email)
            return True, None
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)
