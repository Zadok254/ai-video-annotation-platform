"""Integration-test application and isolated async SQLite database."""

import asyncio
import os
from collections.abc import Iterator

os.environ.update(
    {
        "APP_ENVIRONMENT": "test",
        "APP_SECRET_KEY": "test-only-signing-secret-that-is-never-used-outside-tests",
        "APP_DATABASE_URL": "sqlite+aiosqlite://",
        "APP_REDIS_URL": "redis://localhost:6379/15",
        "APP_CORS_ORIGINS": '["http://testserver"]',
    }
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_session
from app.main import app


@pytest.fixture()
def client() -> Iterator[TestClient]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def initialize() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def override_session():
        async with sessions() as session:
            yield session

    asyncio.run(initialize())
    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_session, None)
    asyncio.run(engine.dispose())
