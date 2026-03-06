"""
Baseline management API endpoints.
"""

from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter()

# These endpoints will be populated when the agent is running
# For now, they provide the structure


@router.get("/baselines")
async def list_baselines() -> dict[str, Any]:
    """
    List all baselines.

    Note: This endpoint is implemented in main.py with direct agent access.
    """
    raise HTTPException(
        status_code=501,
        detail="Use /api/v1/baselines in main app for baseline listing",
    )


@router.get("/baselines/{metric_name}")
async def get_baseline(metric_name: str) -> dict[str, Any]:
    """Get baseline for a specific metric."""
    raise HTTPException(
        status_code=501,
        detail="Baseline lookup requires direct agent access",
    )


@router.post("/baselines/refresh")
async def refresh_baselines() -> dict[str, Any]:
    """Trigger baseline refresh."""
    raise HTTPException(
        status_code=501,
        detail="Baseline refresh requires direct agent access",
    )
