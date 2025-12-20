"""Общие фикстуры для всех тестов."""
import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.infrastructure.database.base import Base
from app.api.v1.dependencies import get_db_session
from app.core.todo.entities import Todo


# === Настройка async event loop ===
@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Создаём event loop для всех async тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# === Тестовая база данных ===
TEST_DATABASE_URL = "postgresql+asyncpg://admin:admin1234@localhost:5432/test_db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    future=True,
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Создаём тестовую сессию БД с автоматическим rollback после теста."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        yield session
        await session.rollback()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP клиент для E2E тестов с подменой БД."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# === Фикстуры доменных сущностей ===
@pytest.fixture
def valid_todo() -> Todo:
    """Валидная доменная сущность Todo."""
    return Todo.create(
        title="Test Todo",
        description="Test Description"
    )


@pytest.fixture
def completed_todo() -> Todo:
    """Завершённая задача."""
    todo = Todo.create(
        title="Completed Task",
        description="This task is done"
    )
    return todo.complete()


@pytest.fixture
def todo_without_description() -> Todo:
    """Задача без описания."""
    return Todo.create(title="Task without description")
