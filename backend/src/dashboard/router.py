from __future__ import annotations

from fastapi import APIRouter

from src.dashboard.schemas import DashboardResponse
from src.dashboard.services import dashboard_service_dependency
from src.dependencies import current_user_dependency


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: current_user_dependency,
    service: dashboard_service_dependency,
) -> DashboardResponse:
    return await service.get_dashboard(current_user)
