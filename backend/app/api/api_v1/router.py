from __future__ import annotations

from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    actions,
    auth,
    dashboard,
    health,
    keyword_rules,
    notification_subscribers,
    notifications,
    sources,
    tenders,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(tenders.router)
api_router.include_router(sources.router)
api_router.include_router(keyword_rules.router)
api_router.include_router(notifications.router)
api_router.include_router(notification_subscribers.router)
api_router.include_router(actions.router)
