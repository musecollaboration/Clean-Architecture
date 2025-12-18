from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import UUID
from datetime import datetime

from app.infrastructure.database.base import Base
from app.core.todo.entities import Todo


class TodoModel(Base):
    __tablename__ = "todos"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    @classmethod
    def from_entity(cls, entity: Todo) -> "TodoModel":
        """Преобразование доменной сущности в ORM-модель."""
        return cls(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            completed=entity.completed,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def to_entity(self) -> Todo:
        """Преобразование ORM-модели в доменную сущность."""
        return Todo(
            id=self.id,
            title=self.title,
            description=self.description,
            completed=self.completed,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def update_from_entity(self, entity: Todo) -> None:
        """Обновление полей модели из новой версии доменной сущности."""
        self.title = entity.title
        self.description = entity.description
        self.completed = entity.completed
        self.updated_at = entity.updated_at
