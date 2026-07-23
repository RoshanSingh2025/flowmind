"""FlowMind API entrypoint.

Application factory pattern: `create_app()` builds and wires the FastAPI
instance (middleware, routers, exception handlers) so tests can construct
fresh, isolated app instances instead of importing a module-level singleton.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.error_handlers import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.middleware import LoggingMiddleware, RequestIDMiddleware

settings = get_settings()
configure_logging(settings)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info(
        "application_startup",
        environment=settings.environment.value,
        version=settings.version,
    )
    yield
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        lifespan=lifespan,
    )

    # --- Middleware (order matters: outermost added last executes first) ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.backend_cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # --- Exception handling ---
    register_exception_handlers(app)

    # --- Routers ---
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
