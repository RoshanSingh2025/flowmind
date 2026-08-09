"""Shared pytest fixtures.

Uses an in-memory SQLite database (via aiosqlite) for fast, isolated tests and
overrides the `get_db_session` dependency so no real Postgres is required to
run the unit/integration test suite locally.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database.base import Base
from app.database.session import get_db_session, get_session_factory
from app.main import create_app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def test_app(
    db_engine: AsyncEngine, db_session: AsyncSession
) -> AsyncGenerator[FastAPI, None]:
    app = create_app()

    async def _override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    def _override_get_session_factory() -> async_sessionmaker[AsyncSession]:
        # Background tasks (e.g. the processing pipeline) open their own
        # session via this factory — bind it to the same engine as
        # `db_session` so both the request path and any background task
        # triggered by it see the same in-memory test database, not the
        # real configured one.
        return async_sessionmaker(bind=db_engine, expire_on_commit=False)

    app.dependency_overrides[get_db_session] = _override_get_db_session
    app.dependency_overrides[get_session_factory] = _override_get_session_factory
    yield app


@pytest_asyncio.fixture
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
