from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models.keyword_rule import KeywordRule
from app.models.tender import Tender
from app.services.scoring_service import rescore_tender


def test_rescore_tender_updates_scores_and_explanation(db_session: Session) -> None:
    db_session.add_all(
        [
            KeywordRule(keyword="otomat", category="direct", weight=4.0, matching_type="contains", target_field="any"),
            KeywordRule(keyword="self servis", category="related", weight=3.0, matching_type="contains", target_field="any"),
            KeywordRule(keyword="havalimanı", category="institution_signal", weight=2.5, matching_type="contains", target_field="any"),
            KeywordRule(
                keyword="temizlik hizmeti",
                category="negative",
                weight=3.0,
                matching_type="contains",
                target_field="any",
                is_negative=True,
            ),
        ]
    )

    tender = Tender(
        title="Havalimanı Self Servis Kahve Otomatı İhalesi",
        normalized_title="havalimani self servis kahve otomati ihalesi",
        source_type="official",
        source_name="EKAP",
        source_url="https://example.com/tender/1",
        publishing_date=date(2026, 3, 1),
        deadline_date=date(2026, 3, 22),
        institution_name="İstanbul Havalimanı",
        city="İstanbul",
        summary="Kiosk ve otomat sistemleri",
        raw_text="POS destekli unattended retail çözümü",
        extracted_keywords=[],
        match_explanation={},
        dedupe_key="seed-1",
        official_verified=True,
        signal_found=False,
    )
    db_session.add(tender)
    db_session.commit()
    db_session.refresh(tender)

    rescore_tender(db_session, tender)

    assert tender.total_score > 60
    assert tender.relevance_score > 60
    assert "positive_hits" in tender.match_explanation
    assert len(tender.extracted_keywords) > 0
