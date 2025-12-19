from typing import AsyncGenerator, NoReturn
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.infrastructure.database.engine import AsyncSessionLocal
from app.infrastructure.persistence.todo.todo_repository import SqlAlchemyTodoRepository
from app.application.todo.services.todo_service import TodoService
from app.core.todo.exceptions import TodoNotFoundError, TodoValidationError

from loguru import logger


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для получения database session с автоматическим commit/rollback и закрытием сессии."""
    from loguru import logger

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
            logger.debug("Database session committed successfully")
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session rollback due to error: {e}")
            raise
        finally:
            await session.close()
            logger.debug("Database session closed")


async def get_todo_repository(session: AsyncSession = Depends(get_db_session)) -> SqlAlchemyTodoRepository:
    """Dependency для получения Todo репозитория."""
    return SqlAlchemyTodoRepository(session)


async def get_todo_service(repo: SqlAlchemyTodoRepository = Depends(get_todo_repository)) -> TodoService:
    """Dependency для получения Todo сервиса."""
    return TodoService(repo)


def todo_not_found_handler(request: Request, exc: TodoNotFoundError) -> NoReturn:
    """Handler для TodoNotFoundError."""
    logger.warning(f"Todo not found: {exc.todo_id} | path: {request.url.path}")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Todo with id {exc.todo_id} not found"
    )


def todo_validation_error_handler(request: Request, exc: TodoValidationError) -> NoReturn:
    """Handler для TodoValidationError."""
    logger.warning(f"Todo validation error: {str(exc)} | path: {request.url.path}")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc)
    )


async def pydantic_validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handler для Pydantic ValidationError с красивым форматированием."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(f"Pydantic validation error: {errors} | path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors}
    )
