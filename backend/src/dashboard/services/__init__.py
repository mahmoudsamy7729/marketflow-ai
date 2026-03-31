from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from src.dashboard.repositories import DashboardRepository
from src.dashboard.services.dashboard_service import DashboardService
from src.database import db_dependency


def get_dashboard_repository(session: db_dependency) -> DashboardRepository:
    return DashboardRepository(session)


def get_dashboard_service(
    repository: Annotated[DashboardRepository, Depends(get_dashboard_repository)],
) -> DashboardService:
    return DashboardService(repository)


dashboard_service_dependency = Annotated[DashboardService, Depends(get_dashboard_service)]

__all__ = [
    "DashboardService",
    "dashboard_service_dependency",
    "get_dashboard_repository",
    "get_dashboard_service",
]
