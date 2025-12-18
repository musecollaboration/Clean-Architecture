from fastapi import FastAPI
from pydantic import ValidationError

from app.lifespan import lifespan
from app.config.settings import settings
from app.api.v1.routers.todo_router import router as todo_router
from app.api.v1.dependencies import (
    todo_not_found_handler,
    todo_validation_error_handler,
    pydantic_validation_error_handler,
)
from app.core.todo.exceptions import TodoNotFoundError, TodoValidationError


app = FastAPI(
    lifespan=lifespan,
    title=settings.APP_NAME,
    version="1.0.0",
    description="Clean Architecture Todo Service with FastAPI and PostgreSQL",
    debug=settings.DEBUG,
)

app.include_router(todo_router, prefix="/api/v1")

# Глобальные обработчики исключений (современный стиль)
app.add_exception_handler(TodoNotFoundError, todo_not_found_handler)
app.add_exception_handler(TodoValidationError, todo_validation_error_handler)
app.add_exception_handler(ValidationError, pydantic_validation_error_handler)
