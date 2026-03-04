"""
FastAPI application entry point.

Provides REST API for:
- Health checks
- Anomaly queries
- Baseline management
- Agent control
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.agent.orchestrator import SREAgentOrchestrator, setup_logging
from src.api.routes import anomalies, health
from src.config.constants import AnomalySeverity, MetricCategory
from src.config.settings import get_settings

logger = structlog.get_logger()

# Global agent instance
_agent: Optional[SREAgentOrchestrator] = None
_agent_task: Optional[asyncio.Task] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global _agent, _agent_task

    setup_logging()
    logger.info("Starting SRE Agent API...")

    # Initialize and start the agent
    _agent = SREAgentOrchestrator()
    _agent_task = asyncio.create_task(_agent.start())

    yield

    # Shutdown
    logger.info("Shutting down SRE Agent API...")
    if _agent:
        await _agent.stop()
    if _agent_task:
        _agent_task.cancel()
        try:
            await _agent_task
        except asyncio.CancelledError:
            pass


# Create FastAPI app
settings = get_settings()

app = FastAPI(
    title="SRE Agent API",
    description="AI-powered Intelligent Operations Agent for Cryptocurrency Trading Systems",
    version=settings.app_version,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(anomalies.router, prefix="/api/v1", tags=["Anomalies"])


def get_agent() -> SREAgentOrchestrator:
    """Get the global agent instance."""
    if _agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return _agent


# Additional endpoints that need direct agent access


@app.get("/api/v1/status")
async def get_status() -> Dict[str, Any]:
    """Get agent status."""
    agent = get_agent()
    return agent.get_status()


@app.get("/api/v1/infrastructure")
async def get_infrastructure_status() -> Dict[str, Any]:
    """
    Get infrastructure status.

    Shows the status of all configured infrastructure components:
    - connected: Service is configured and connected
    - auto_created: Service was auto-created for local development
    - failed: Service is configured but connection failed
    - not_configured: Service is not configured
    """
    agent = get_agent()
    return agent.get_infrastructure_status()


@app.get("/api/v1/anomalies")
async def list_anomalies(
    category: Optional[MetricCategory] = Query(None, description="Filter by category"),
    severity: Optional[AnomalySeverity] = Query(None, description="Filter by severity"),
    active_only: bool = Query(True, description="Only return active anomalies"),
) -> Dict[str, Any]:
    """List anomalies."""
    agent = get_agent()

    anomalies = agent._anomaly_detector.get_active_anomalies(
        category=category,
        severity=severity,
    )

    return {
        "count": len(anomalies),
        "anomalies": [
            {
                "id": a.id,
                "metric_name": a.metric_name,
                "category": a.category.value,
                "severity": a.severity.value,
                "current_value": a.current_value,
                "baseline_value": a.baseline_value,
                "deviation": a.deviation,
                "deviation_percent": a.deviation_percent,
                "detected_at": a.detected_at.isoformat(),
                "duration_minutes": a.duration_minutes,
                "labels": a.labels,
                "acknowledged": a.acknowledged,
            }
            for a in anomalies
        ],
    }


@app.get("/api/v1/anomalies/{anomaly_id}")
async def get_anomaly(anomaly_id: str) -> Dict[str, Any]:
    """Get a specific anomaly by ID."""
    agent = get_agent()

    for anomaly in agent._anomaly_detector.state.active_anomalies.values():
        if anomaly.id == anomaly_id:
            return {
                "id": anomaly.id,
                "metric_name": anomaly.metric_name,
                "category": anomaly.category.value,
                "severity": anomaly.severity.value,
                "anomaly_type": anomaly.anomaly_type.value,
                "current_value": anomaly.current_value,
                "baseline_value": anomaly.baseline_value,
                "deviation": anomaly.deviation,
                "deviation_percent": anomaly.deviation_percent,
                "detected_at": anomaly.detected_at.isoformat(),
                "started_at": anomaly.started_at.isoformat() if anomaly.started_at else None,
                "duration_minutes": anomaly.duration_minutes,
                "labels": anomaly.labels,
                "scores": [
                    {
                        "algorithm": s.algorithm,
                        "score": s.score,
                        "threshold": s.threshold,
                        "is_anomaly": s.is_anomaly,
                    }
                    for s in anomaly.scores
                ],
                "ensemble_score": anomaly.ensemble_score,
                "acknowledged": anomaly.acknowledged,
                "acknowledged_by": anomaly.acknowledged_by,
            }

    raise HTTPException(status_code=404, detail="Anomaly not found")


@app.post("/api/v1/anomalies/{anomaly_id}/acknowledge")
async def acknowledge_anomaly(
    anomaly_id: str,
    acknowledged_by: str = Query(..., description="Person acknowledging"),
) -> Dict[str, Any]:
    """Acknowledge an anomaly."""
    agent = get_agent()

    success = agent._anomaly_detector.acknowledge_anomaly(anomaly_id, acknowledged_by)
    if not success:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    return {"status": "acknowledged", "anomaly_id": anomaly_id}


@app.get("/api/v1/baselines")
async def list_baselines() -> Dict[str, Any]:
    """List all baselines."""
    agent = get_agent()

    baselines = agent._baseline_engine.baselines.baselines

    return {
        "count": len(baselines),
        "baselines": [
            {
                "metric_name": b.metric_name,
                "labels": b.labels,
                "created_at": b.created_at.isoformat(),
                "updated_at": b.updated_at.isoformat(),
                "sample_count": b.sample_count,
                "coverage_days": b.coverage_days,
                "quality_score": b.quality_score,
                "global_stats": {
                    "mean": b.global_stats.mean,
                    "std": b.global_stats.std,
                    "median": b.global_stats.median,
                    "min": b.global_stats.min,
                    "max": b.global_stats.max,
                },
            }
            for b in baselines.values()
        ],
    }


@app.get("/api/v1/metrics")
async def list_metrics() -> Dict[str, Any]:
    """List configured metrics."""
    agent = get_agent()

    if not agent._metrics_collector:
        raise HTTPException(status_code=503, detail="Metrics collector not available")

    return {
        "configured_metrics": agent._metrics_collector.configured_metrics,
        "count": len(agent._metrics_collector.configured_metrics),
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        path=request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
