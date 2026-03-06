from __future__ import annotations

from classifier.interfaces import ClassifierInterface
from classifier.types import ClassificationResult


class AIClassifierPlaceholder(ClassifierInterface):
    """Placeholder for future LLM/ML integration.

    The interface is stable so this class can be replaced with a model-backed
    implementation without changing ingestion pipelines.
    """

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
        return ClassificationResult(
            relevance_score=0.0,
            commercial_score=0.0,
            technical_score=0.0,
            total_score=0.0,
            classification_label="irrelevant",
            extracted_keywords=[],
            match_explanation={"note": "AI classifier not implemented yet"},
        )
