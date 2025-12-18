from dataclasses import dataclass, replace
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Self
from app.core.todo.exceptions import TodoValidationError


@dataclass(frozen=True)
class Todo:
    id: UUID
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def _validate_title(cls, title: str) -> str:
        """Валидация и нормализация заголовка. Возвращает очищенный title."""
        cleaned = title.strip()
        if not cleaned:
            raise TodoValidationError("Title cannot be empty")
        if len(cleaned) > 200:
            raise TodoValidationError("Title cannot exceed 200 characters")
        return cleaned

    @classmethod
    def _normalize_description(cls, description: str | None) -> str | None:
        """Нормализация описания: strip, пустая строка → None, ограничение длины."""
        if description is None:
            return None
        cleaned = description.strip()
        if not cleaned:
            return None
        if len(cleaned) > 1000:
            raise TodoValidationError("Description cannot exceed 1000 characters")
        return cleaned

    @classmethod
    def create(cls, title: str, description: str | None = None) -> Self:
        """Фабричный метод создания новой задачи."""
        return cls(
            id=uuid4(),
            title=cls._validate_title(title),
            description=cls._normalize_description(description),
            completed=False,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )

    def complete(self) -> Self:
        """Возвращает новую версию задачи с completed=True."""
        return replace(self, completed=True, updated_at=datetime.now(tz=timezone.utc))

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
    ) -> Self:
        """Возвращает обновлённую копию задачи."""
        if title is None and description is None:
            return self

        new_title = Todo._validate_title(title) if title is not None else self.title
        new_description = (
            Todo._normalize_description(description)
            if description is not None
            else self.description
        )

        return replace(
            self,
            title=new_title,
            description=new_description,
            updated_at=datetime.now(tz=timezone.utc),
        )
