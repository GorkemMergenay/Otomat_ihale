from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.keyword_rule import KeywordRule
from app.models.tender import Tender
from app.models.tender_event import TenderEvent
from app.models.enums import TenderStatus
from classifier.rule_based_classifier import RuleBasedClassifier
from notifier.service import NotificationManager


def _build_classifier(db: Session) -> RuleBasedClassifier:
    rules = db.scalars(select(KeywordRule).where(KeywordRule.is_active.is_(True))).all()
    return RuleBasedClassifier(rules)


def rescore_tender(db: Session, tender: Tender) -> None:
    previous_total = tender.total_score
    previous_label = tender.classification_label
    previous_status = tender.status

    classifier = _build_classifier(db)
    result = classifier.classify(
        title=tender.title,
        summary=tender.summary or "",
        raw_text=tender.raw_text or "",
        source_type=tender.source_type,
        official_verified=tender.official_verified,
        institution_name=tender.institution_name or "",
        city=tender.city or "",
    )

    tender.relevance_score = result.relevance_score
    tender.commercial_score = result.commercial_score
    tender.technical_score = result.technical_score
    tender.total_score = result.total_score
    tender.classification_label = result.classification_label
    tender.extracted_keywords = result.extracted_keywords
    tender.match_explanation = result.match_explanation
    tender.last_scored_at = datetime.now(timezone.utc)
    if tender.status == TenderStatus.NEW.value and result.classification_label in {
        "highly_relevant",
        "relevant",
        "maybe_relevant",
    }:
        tender.status = TenderStatus.AUTO_FLAGGED.value
    elif tender.status == TenderStatus.AUTO_FLAGGED.value and result.classification_label == "irrelevant":
        tender.status = TenderStatus.NEW.value

    db.add(tender)
    db.add(
        TenderEvent(
            tender_id=tender.id,
            event_type="rescored",
            event_data={
                "relevance": result.relevance_score,
                "commercial": result.commercial_score,
                "technical": result.technical_score,
                "total": result.total_score,
                "label": result.classification_label,
            },
        )
    )
    if tender.status != previous_status:
        reason = "auto_flagged_by_scoring"
        if previous_status == TenderStatus.AUTO_FLAGGED.value and tender.status == TenderStatus.NEW.value:
            reason = "auto_unflagged_by_scoring"
        db.add(
            TenderEvent(
                tender_id=tender.id,
                event_type="status_changed",
                event_data={"from": previous_status, "to": tender.status, "reason": reason},
            )
        )
    db.commit()
    db.refresh(tender)

    notifier = NotificationManager(db)
    if previous_label != "highly_relevant" and tender.classification_label == "highly_relevant":
        notifier.notify_new_highly_relevant(tender)
    notifier.notify_score_threshold_crossed(tender, previous_total)
    notifier.notify_deadline_if_needed(tender)


def reprocess_all(db: Session) -> int:
    tenders = db.scalars(select(Tender)).all()
    for tender in tenders:
        rescore_tender(db, tender)
    return len(tenders)
