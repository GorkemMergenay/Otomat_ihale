from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models.tender import Tender


def seed_tender(db_session: Session) -> Tender:
    tender = Tender(
        title="Ankara Üniversitesi Kampüs Self Servis Kiosk İhalesi",
        normalized_title="ankara universitesi kampus self servis kiosk ihalesi",
        source_type="official",
        source_name="EKAP",
        source_url="https://example.com/ekap/1",
        external_id="EKAP-1",
        publishing_date=date(2026, 3, 1),
        deadline_date=date(2026, 3, 20),
        institution_name="Ankara Üniversitesi",
        city="Ankara",
        region="İç Anadolu",
        tender_type="hizmet",
        summary="Self servis kiosk ve otomat sistemi alımı",
        raw_text="POS cihazlı satış ünitesi şartları",
        extracted_keywords=["kiosk", "otomat"],
        match_explanation={"reason": "seed"},
        relevance_score=80,
        commercial_score=70,
        technical_score=75,
        total_score=76,
        classification_label="highly_relevant",
        official_verified=True,
        signal_found=False,
        status="new",
        dedupe_key="ekap:1",
    )
    db_session.add(tender)
    db_session.commit()
    db_session.refresh(tender)
    return tender


def test_health_endpoint(client) -> None:
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "tamam"


def test_tenders_list_endpoint(client, db_session: Session) -> None:
    seed_tender(db_session)

    response = client.get("/api/v1/tenders")
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["title"].startswith("Ankara Üniversitesi")


def test_dashboard_overview_endpoint(client, db_session: Session) -> None:
    seed_tender(db_session)

    response = client.get("/api/v1/dashboard/overview")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_tenders"] == 1
    assert payload["highly_relevant_count"] == 1
