from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.source_config import SourceConfig
from collector.types import CollectorOutput


class BaseCollector(ABC):
    parser_version = "1.0"

    def __init__(self, source_config: SourceConfig) -> None:
        self.source_config = source_config

    @abstractmethod
    def collect(self) -> CollectorOutput:
        raise NotImplementedError
