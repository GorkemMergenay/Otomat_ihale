from __future__ import annotations

from dataclasses import dataclass

from classifier.rule_based_classifier import RuleBasedClassifier


@dataclass
class FakeRule:
    keyword: str
    category: str
    weight: float
    is_active: bool = True
    is_negative: bool = False
    matching_type: str = "contains"
    target_field: str = "any"


def test_rule_based_classifier_flags_highly_relevant_tender() -> None:
    rules = [
        FakeRule("otomat", "direct", 4.0),
        FakeRule("self servis kiosk", "direct", 3.5),
        FakeRule("havalimanı", "institution_signal", 2.0),
        FakeRule("giyim", "negative", 3.0, is_negative=True),
    ]
    classifier = RuleBasedClassifier(rules)

    result = classifier.classify(
        title="Havalimanı Self Servis Kiosk ve Kahve Otomatı Kurulumu",
        summary="Yolcu alanlarında unattended retail çözümü",
        raw_text="POS destekli satış ünitesi ve bakım hizmeti",
        source_type="official",
        official_verified=True,
        institution_name="İstanbul Havalimanı",
        city="İstanbul",
    )

    assert result.total_score >= 75
    assert result.classification_label == "highly_relevant"
    assert "otomat" in result.extracted_keywords
    assert "positive_hits" in result.match_explanation
