from __future__ import annotations

from dataclasses import asdict
from typing import Any

from rapidfuzz import fuzz

from app.core.config import settings
from classifier.interfaces import ClassifierInterface
from classifier.text_utils import normalize_text
from classifier.types import ClassificationResult, MatchHit

FIELD_MULTIPLIERS = {
    "title": 1.6,
    "summary": 1.2,
    "raw_text": 1.0,
    "institution_name": 1.1,
    "city": 0.7,
}

CATEGORY_MULTIPLIERS = {
    "direct": 3.2,
    "related": 2.3,
    "commercial": 2.1,
    "institution_signal": 1.8,
    "technical": 2.0,
    "negative": 2.8,
}

SOURCE_TRUST_BONUS = {
    "official": 12,
    "public_announcement": 9,
    "institution": 6,
    "news": 4,
}

HIGH_TRAFFIC_SIGNALS = [
    "havalimani",
    "metro",
    "universite",
    "hastane",
    "terminal",
    "istasyon",
    "spor tesisi",
]

TECHNICAL_CLUES = [
    "otomasyon",
    "self servis",
    "odeme",
    "pos",
    "cihaz",
    "kurulum",
    "bakim",
    "akilli",
    "kiosk",
    "otomat",
]


class RuleBasedClassifier(ClassifierInterface):
    def __init__(self, keyword_rules: list[Any]) -> None:
        self.keyword_rules = keyword_rules

    def classify(
        self,
        title: str,
        summary: str,
        raw_text: str,
        source_type: str,
        official_verified: bool,
        institution_name: str,
        city: str,
    ) -> ClassificationResult:
        normalized_fields = {
            "title": normalize_text(title),
            "summary": normalize_text(summary),
            "raw_text": normalize_text(raw_text),
            "institution_name": normalize_text(institution_name),
            "city": normalize_text(city),
        }

        positive_hits: list[MatchHit] = []
        negative_hits: list[MatchHit] = []

        for rule in self.keyword_rules:
            hit = self._evaluate_rule(rule, normalized_fields)
            if not hit:
                continue

            if getattr(rule, "is_negative", False):
                negative_hits.append(hit)
            else:
                positive_hits.append(hit)

        relevance_score = self._compute_relevance_score(positive_hits, negative_hits, source_type, official_verified)
        commercial_score = self._compute_commercial_score(positive_hits, normalized_fields, source_type)
        technical_score = self._compute_technical_score(positive_hits, normalized_fields)

        total_score = round((relevance_score * 0.50) + (commercial_score * 0.30) + (technical_score * 0.20), 2)

        if total_score >= settings.scoring_high_threshold:
            label = "highly_relevant"
        elif total_score >= settings.scoring_relevant_threshold:
            label = "relevant"
        elif total_score >= settings.scoring_maybe_threshold:
            label = "maybe_relevant"
        else:
            label = "irrelevant"

        extracted_keywords = sorted({hit.keyword for hit in positive_hits})

        explanation = {
            "positive_hits": [asdict(hit) for hit in positive_hits],
            "negative_hits": [asdict(hit) for hit in negative_hits],
            "components": {
                "source_type": source_type,
                "official_verified": official_verified,
                "source_trust_bonus": SOURCE_TRUST_BONUS.get(source_type, 0),
                "scoring_weights": {
                    "relevance": 0.50,
                    "commercial": 0.30,
                    "technical": 0.20,
                },
            },
            "final_label": label,
        }

        return ClassificationResult(
            relevance_score=relevance_score,
            commercial_score=commercial_score,
            technical_score=technical_score,
            total_score=total_score,
            classification_label=label,
            extracted_keywords=extracted_keywords,
            match_explanation=explanation,
        )

    def _evaluate_rule(self, rule: Any, fields: dict[str, str]) -> MatchHit | None:
        keyword = normalize_text(getattr(rule, "keyword", ""))
        if not keyword:
            return None

        matching_type = str(getattr(rule, "matching_type", "contains"))
        target_field = str(getattr(rule, "target_field", "any"))

        candidate_fields = [target_field] if target_field != "any" else list(fields.keys())

        best_field = ""
        best_score = 0.0

        for field in candidate_fields:
            text = fields.get(field, "")
            if not text:
                continue
            score = self._match_score(keyword, text, matching_type)
            if score > best_score:
                best_score = score
                best_field = field

        if best_score < 65:
            return None

        category = str(getattr(rule, "category", "related"))
        weight = float(getattr(rule, "weight", 1.0))
        is_negative = bool(getattr(rule, "is_negative", False))

        contribution = round(
            weight
            * CATEGORY_MULTIPLIERS.get(category, 1.5)
            * FIELD_MULTIPLIERS.get(best_field, 1.0)
            * (best_score / 100.0),
            2,
        )

        return MatchHit(
            keyword=keyword,
            category=category,
            weight=weight,
            is_negative=is_negative,
            target_field=target_field,
            matched_field=best_field,
            matching_type=matching_type,
            match_score=round(best_score, 2),
            contribution=contribution,
        )

    def _match_score(self, keyword: str, text: str, matching_type: str) -> float:
        if matching_type == "exact":
            return 100.0 if keyword == text else 0.0
        if matching_type == "contains":
            return 100.0 if keyword in text else 0.0
        return float(fuzz.partial_ratio(keyword, text))

    def _compute_relevance_score(
        self,
        positive_hits: list[MatchHit],
        negative_hits: list[MatchHit],
        source_type: str,
        official_verified: bool,
    ) -> float:
        positive = sum(hit.contribution for hit in positive_hits)
        negative = sum(hit.contribution for hit in negative_hits)
        trust_bonus = SOURCE_TRUST_BONUS.get(source_type, 0)
        verified_bonus = 10 if official_verified else 0

        raw = (positive * 3.2) - (negative * 2.8) + trust_bonus + verified_bonus
        return max(0.0, min(100.0, round(raw, 2)))

    def _compute_commercial_score(
        self,
        positive_hits: list[MatchHit],
        fields: dict[str, str],
        source_type: str,
    ) -> float:
        commercial_points = 0.0
        for hit in positive_hits:
            if hit.category in {"commercial", "institution_signal", "direct", "related"}:
                commercial_points += hit.contribution

        signal_bonus = 0
        context_text = " ".join([fields["title"], fields["summary"], fields["raw_text"], fields["institution_name"]])
        for signal in HIGH_TRAFFIC_SIGNALS:
            if signal in context_text:
                signal_bonus += 4

        source_bonus = 5 if source_type == "official" else 2
        raw = (commercial_points * 2.4) + signal_bonus + source_bonus
        return max(0.0, min(100.0, round(raw, 2)))

    def _compute_technical_score(self, positive_hits: list[MatchHit], fields: dict[str, str]) -> float:
        technical_points = 0.0
        for hit in positive_hits:
            if hit.category in {"technical", "direct", "related"}:
                technical_points += hit.contribution

        clue_bonus = 0
        context_text = " ".join([fields["title"], fields["summary"], fields["raw_text"]])
        for clue in TECHNICAL_CLUES:
            if clue in context_text:
                clue_bonus += 3

        raw = (technical_points * 2.1) + clue_bonus
        return max(0.0, min(100.0, round(raw, 2)))
