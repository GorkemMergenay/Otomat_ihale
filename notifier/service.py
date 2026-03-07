from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.enums import DeliveryStatus, NotificationChannel, NotificationType
from app.models.notification import Notification
from app.models.notification_subscriber import NotificationSubscriber
from app.models.tender import Tender
from app.models.user import User
from notifier.channels.email_sender import EmailSender
from notifier.channels.telegram_sender import TelegramSender


class NotificationManager:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.email_sender = EmailSender()
        self.telegram_sender = TelegramSender()

    def notify_new_highly_relevant(self, tender: Tender) -> None:
        if tender.classification_label != "highly_relevant":
            return
        if tender.total_score < settings.notification_score_threshold:
            return
        subject = f"Yeni Yüksek Potansiyel İhale: {tender.title[:120]}"
        message = self._render_message(tender, "Yeni yüksek potansiyelli ihale tespit edildi.")
        self._dispatch(NotificationType.NEW_HIGHLY_RELEVANT.value, tender, subject, message)

    def notify_official_verified(self, tender: Tender) -> None:
        if not tender.official_verified:
            return
        subject = f"İhale Resmi Olarak Doğrulandı: {tender.title[:120]}"
        message = self._render_message(tender, "Daha önce sinyal olarak görülen ihale resmi kaynakla doğrulandı.")
        self._dispatch(NotificationType.OFFICIAL_VERIFIED.value, tender, subject, message)

    def notify_score_threshold_crossed(self, tender: Tender, previous_total_score: float) -> None:
        threshold = settings.notification_score_threshold
        if previous_total_score < threshold <= tender.total_score:
            subject = f"İhale Skoru Eşiği Geçti ({tender.total_score:.1f})"
            message = self._render_message(
                tender,
                f"İhale toplam skoru {previous_total_score:.1f} -> {tender.total_score:.1f} yükseldi (eşik: {threshold:.1f}).",
            )
            self._dispatch(NotificationType.SCORE_THRESHOLD.value, tender, subject, message)

    def notify_deadline_if_needed(self, tender: Tender) -> None:
        if not tender.deadline_date:
            return

        days_left = (tender.deadline_date - date.today()).days
        if days_left < 0:
            return

        configured = [int(x.strip()) for x in settings.deadline_warning_days.split(",") if x.strip().isdigit()]
        if days_left not in configured:
            return

        subject = f"Son Tarih Yaklaşıyor ({days_left} gün): {tender.title[:80]}"
        message = self._render_message(tender, f"İhale son teklif tarihi {days_left} gün içinde.")
        event_key_suffix = f"{days_left}d"
        self._dispatch(
            NotificationType.DEADLINE_APPROACHING.value,
            tender,
            subject,
            message,
            event_key_suffix=event_key_suffix,
        )

    def scan_deadline_notifications(self) -> int:
        tenders = self.db.scalars(select(Tender).where(Tender.deadline_date.is_not(None))).all()
        sent = 0
        for tender in tenders:
            before = self._notification_count()
            self.notify_deadline_if_needed(tender)
            after = self._notification_count()
            if after > before:
                sent += after - before
        return sent

    def _dispatch(
        self,
        notification_type: str,
        tender: Tender,
        subject: str,
        message: str,
        event_key_suffix: str | None = None,
    ) -> None:
        recipients = self._email_recipients()

        for recipient in recipients:
            self._send_to_channel(
                channel=NotificationChannel.EMAIL.value,
                recipient=recipient,
                notification_type=notification_type,
                tender=tender,
                subject=subject,
                message=message,
                event_key_suffix=event_key_suffix,
            )

        if settings.telegram_chat_id:
            self._send_to_channel(
                channel=NotificationChannel.TELEGRAM.value,
                recipient=settings.telegram_chat_id,
                notification_type=notification_type,
                tender=tender,
                subject=subject,
                message=message,
                event_key_suffix=event_key_suffix,
            )

    def _send_to_channel(
        self,
        channel: str,
        recipient: str,
        notification_type: str,
        tender: Tender,
        subject: str,
        message: str,
        event_key_suffix: str | None,
    ) -> None:
        idempotency_key = self._idempotency_key(
            tender_id=tender.id,
            channel=channel,
            recipient=recipient,
            notification_type=notification_type,
            suffix=event_key_suffix,
        )

        if not self._should_send(idempotency_key, tender.id, channel, recipient, notification_type):
            return

        record = Notification(
            tender_id=tender.id,
            channel=channel,
            recipient=recipient,
            notification_type=notification_type,
            delivery_status=DeliveryStatus.PENDING.value,
            payload={"subject": subject, "message": message},
            idempotency_key=idempotency_key,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        if channel == NotificationChannel.EMAIL.value:
            ok, err = self.email_sender.send(recipient, subject, message)
        else:
            ok, err = self.telegram_sender.send(recipient, subject, message)

        if ok:
            record.delivery_status = DeliveryStatus.SENT.value
        elif err and "disabled" in err.lower():
            record.delivery_status = DeliveryStatus.SKIPPED.value
        else:
            record.delivery_status = DeliveryStatus.FAILED.value
        record.error_message = err
        self.db.add(record)
        self.db.commit()

    def _should_send(
        self,
        idempotency_key: str,
        tender_id: int,
        channel: str,
        recipient: str,
        notification_type: str,
    ) -> bool:
        existing = self.db.scalar(select(Notification).where(Notification.idempotency_key == idempotency_key))
        if existing:
            return False

        cutoff = datetime.now(timezone.utc) - timedelta(minutes=settings.notification_cooldown_minutes)
        recent = self.db.scalar(
            select(Notification)
            .where(Notification.tender_id == tender_id)
            .where(Notification.channel == channel)
            .where(Notification.recipient == recipient)
            .where(Notification.notification_type == notification_type)
            .where(Notification.created_at >= cutoff)
            .where(Notification.delivery_status.not_in([DeliveryStatus.FAILED.value]))
            .limit(1)
        )
        return recent is None

    def _idempotency_key(
        self,
        tender_id: int,
        channel: str,
        recipient: str,
        notification_type: str,
        suffix: str | None,
    ) -> str:
        key = f"{notification_type}:{tender_id}:{channel}:{recipient}"
        if suffix:
            key = f"{key}:{suffix}"
        return key

    def _email_recipients(self) -> list[str]:
        recipients: list[str] = []
        if settings.notification_email_recipients:
            recipients.extend(x.strip() for x in settings.notification_email_recipients.split(",") if x.strip())
        rows = self.db.scalars(
            select(NotificationSubscriber.email)
            .where(NotificationSubscriber.is_active.is_(True))
        ).all()
        for email in rows:
            if email and email.strip() and email.strip() not in recipients:
                recipients.append(email.strip())
        if not recipients:
            fallback = self.db.scalars(
                select(User.email).where(User.is_active.is_(True)).where(User.role.in_(["admin", "analyst"]))
            ).all()
            recipients = [e.strip() for e in fallback if e and e.strip()]
        return recipients

    def _render_message(self, tender: Tender, intro: str) -> str:
        deadline = tender.deadline_date.isoformat() if tender.deadline_date else "belirtilmedi"
        published = tender.publishing_date.isoformat() if tender.publishing_date else "belirtilmedi"
        return (
            f"{intro}\n\n"
            f"Başlık: {tender.title}\n"
            f"Kurum: {tender.institution_name or '-'}\n"
            f"Şehir: {tender.city or '-'}\n"
            f"Kaynak: {tender.source_name}\n"
            f"Yayın Tarihi: {published}\n"
            f"Son Tarih: {deadline}\n"
            f"Toplam Skor: {tender.total_score:.1f}\n"
            f"Etiket: {tender.classification_label}\n"
            f"Link: {tender.source_url}"
        )

    def _notification_count(self) -> int:
        return self.db.scalar(select(func.count()).select_from(Notification)) or 0
