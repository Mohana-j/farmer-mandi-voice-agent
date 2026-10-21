"""Farmer Mandi Price Voice Agent - FastAPI Application Entrypoint."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.routes_actions import router as actions_router
from backend.app.api.routes_alerts import router as alerts_router
from backend.app.api.routes_config import router as config_router
from backend.app.api.routes_exports import router as exports_router
from backend.app.api.routes_markets import router as markets_router
from backend.app.api.routes_queries import router as queries_router
from backend.app.api.routes_tests import router as tests_router
from backend.app.config import settings
from backend.app.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("mandi_agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize database and verify configuration."""
    logger.info("Initializing database schema...")
    init_db()
    logger.info(f"Database initialized. Operating in '{settings.DATA_PROVIDER_MODE}' mode.")
    yield
    logger.info("Application shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Official Agentic AI system for agricultural mandi price retrieval, unit normalization, "
        "bilingual voice assistance (English & Tamil), human-in-the-loop approvals, and audit trails. "
        "Built for the Agentic AI Hackathon 2026 — Powered by Ziro.Digital."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global safe exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing your agricultural query.",
            "path": request.url.path,
        },
    )

# Include API Routers
app.include_router(config_router, prefix="/api")
app.include_router(queries_router, prefix="/api")
app.include_router(actions_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
app.include_router(exports_router, prefix="/api")
app.include_router(markets_router, prefix="/api")
app.include_router(tests_router, prefix="/api")


@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/api/health",
        "mode": settings.DATA_PROVIDER_MODE,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
