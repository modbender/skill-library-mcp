import logging
import sys
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.db.database import init_db

# Configure logging
import os
log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MoltFundMe API",
    description="Where AI agents help humans help humans",
    version="0.1.0",
)

# Security headers (before CORS so they apply to all responses)
from app.core.security_headers import SecurityHeadersMiddleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware
# In production, only allow the configured frontend URL
cors_origins = [settings.frontend_url]
if settings.env != "production":
    cors_origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.api.routes import campaigns, agents, advocacy, warroom, evaluations, feed, auth, kyc, creators

app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(creators.router, prefix="/api/creators", tags=["creators"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(advocacy.router, prefix="/api/campaigns", tags=["advocacy"])
app.include_router(warroom.router, prefix="/api/campaigns", tags=["warroom"])
app.include_router(evaluations.router, prefix="/api/campaigns", tags=["evaluations"])
app.include_router(feed.router, prefix="/api/feed", tags=["feed"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(kyc.router, prefix="/api/kyc", tags=["kyc"])


# Serve uploaded files (agents, campaigns)
@app.get("/api/uploads/agents/{agent_id}/{filename}")
async def serve_agent_avatar(agent_id: str, filename: str):
    """Serve agent avatar image."""
    from pathlib import Path
    from fastapi.responses import FileResponse

    if ".." in filename or ".." in agent_id:
        raise HTTPException(status_code=400, detail="Invalid path")
    base_dir = Path("data/uploads/agents")
    file_path = base_dir / agent_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@app.get("/api/uploads/campaigns/{campaign_id}/{filename}")
async def serve_campaign_image(campaign_id: str, filename: str):
    """Serve campaign image."""
    from pathlib import Path
    from fastapi.responses import FileResponse

    if ".." in filename or ".." in campaign_id:
        raise HTTPException(status_code=400, detail="Invalid path")
    base_dir = Path("data/uploads/campaigns")
    file_path = base_dir / campaign_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler for unhandled errors."""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
        }
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing information."""
    import time
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
    )
    
    return response


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await init_db()
    # Start balance polling scheduler (skip in test environment)
    import os
    if os.getenv("TESTING") != "true":
        from app.services.scheduler import start_scheduler
        start_scheduler()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    import os
    if os.getenv("TESTING") != "true":
        from app.services.scheduler import shutdown_scheduler
        shutdown_scheduler()


@app.get("/")
async def root():
    return {"message": "MoltFundMe API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check endpoint that verifies database connectivity."""
    from fastapi import HTTPException
    from sqlalchemy import text
    from app.db.database import engine
    
    try:
        # Verify database connectivity
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        # Log the error but don't expose internal details
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=503, detail="Service unavailable")


def run_dev():
    """Run development server with hot reload."""
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


def run_prod():
    """Run production server."""
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
