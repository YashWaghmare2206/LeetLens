"""
LeetLens FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.router import router as v1_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Stateless startup: zero database dependencies."""
    logger.info("Starting LeetLens stateless backend...")
    yield
    logger.info("LeetLens stateless backend shutting down.")


app = FastAPI(
    title="LeetLens API",
    description=(
        "LeetCode DSA Pattern Analyzer — analyze your LeetCode profile "
        "by topics, patterns and difficulty."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — allow the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(v1_router, prefix="/api/v1", tags=["analytics"])


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
