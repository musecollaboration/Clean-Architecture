from typing import Annotated

from pydantic import BaseModel, Field, field_validator, model_validator
from uuid import UUID
from datetime import datetime

TITLE_MAX_LENGTH = 200
DESCRIPTION_MAX_LENGTH = 1000


class TodoCreateDTO(BaseModel):
    title: Annotated[str, Field(max_length=TITLE_MAX_LENGTH)]
    description: Annotated[str | None, Field(default=None, max_length=DESCRIPTION_MAX_LENGTH)]

    @field_validator("title", "description", mode="before")
    @classmethod
    def normalize_strings(cls, v: str | None) -> str | None:
        """Нормализация строк: strip и преобразование пустых в None."""
        if v is None:
            return None
        stripped = v.strip() if isinstance(v, str) else v
        return stripped if stripped else None


class TodoUpdateDTO(BaseModel):
    title: Annotated[str | None, Field(default=None, max_length=TITLE_MAX_LENGTH)]
    description: Annotated[str | None, Field(default=None, max_length=DESCRIPTION_MAX_LENGTH)]

    @field_validator("title", "description", mode="before")
    @classmethod
    def normalize_strings(cls, v: str | None) -> str | None:
        """Нормализация строк: strip и преобразование пустых в None."""
        if v is None:
            return None
        stripped = v.strip() if isinstance(v, str) else v
        return stripped if stripped else None

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        """Проверка что хотя бы одно поле для обновления заполнено."""
        if self.title is None and self.description is None:
            raise ValueError("At least one field (title or description) must be provided")
        return self


class TodoResponseDTO(BaseModel):
    id: Annotated[UUID, Field()]
    title: Annotated[str, Field()]
    description: Annotated[str | None, Field(default=None)]
    completed: Annotated[bool, Field()]
    created_at: Annotated[datetime, Field()]
    updated_at: Annotated[datetime, Field()]

    model_config = {"from_attributes": True}  # Для model_validate из доменной сущности
