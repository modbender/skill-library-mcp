"""
Health check endpoints.
"""

from datetime import datetime

from fastapi import APIRouter

from src.config.settings import get_settings

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """
    Basic health check endpoint.

    Returns:
        Health status
    """
    settings = get_settings()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/ready")
async def readiness_check() -> dict:
    """
    Readiness check for Kubernetes.

    Returns:
        Readiness status
    """
    # Could add more sophisticated checks here
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/live")
async def liveness_check() -> dict:
    """
    Liveness check for Kubernetes.

    Returns:
        Liveness status
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
    }
