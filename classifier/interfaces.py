from __future__ import annotations

from abc import ABC, abstractmethod

from classifier.types import ClassificationResult


class ClassifierInterface(ABC):
    @abstractmethod
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
        raise NotImplementedError
