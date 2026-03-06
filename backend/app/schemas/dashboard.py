from __future__ import annotations

from pydantic import BaseModel


class DashboardOverview(BaseModel):
    total_tenders: int
    newly_found_today: int
    highly_relevant_count: int
    approaching_deadlines: int
    official_verified_count: int
    active_sources: int
    source_failures_last_24h: int
