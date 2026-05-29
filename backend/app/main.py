"""
FastAPI Application Entry Point
"""
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .api import productions, events, factors, ml, reports, documents, auth, notifications, ai

logger = logging.getLogger("terra.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables (dev convenience; use Alembic in production)
    Base.metadata.create_all(bind=engine)
    logger.info("Terra API starting up — tables ensured")
    yield
    # Shutdown
    logger.info("Terra API shutting down")


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s — %s — %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response


app.include_router(productions.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(factors.router, prefix="/api/v1")
app.include_router(ml.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name, "version": "0.2.0"}
