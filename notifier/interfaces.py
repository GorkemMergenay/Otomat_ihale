from __future__ import annotations

from abc import ABC, abstractmethod


class NotificationSender(ABC):
    @abstractmethod
    def send(self, recipient: str, subject: str, message: str) -> tuple[bool, str | None]:
        raise NotImplementedError
