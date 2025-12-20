"""Unit тесты для DTO моделей."""
import pytest
from pydantic import ValidationError

from app.application.todo.dto import TodoCreateDTO, TodoUpdateDTO, TodoResponseDTO
from app.core.todo.entities import Todo


class TestTodoCreateDTO:
    """Тесты для TodoCreateDTO."""

    def test_valid_create_dto(self):
        """Создание валидного DTO."""
        dto = TodoCreateDTO(title="Task", description="Description")

        assert dto.title == "Task"
        assert dto.description == "Description"

    def test_create_dto_without_description(self):
        """DTO без описания."""
        dto = TodoCreateDTO(title="Task")

        assert dto.title == "Task"
        assert dto.description is None

    def test_create_dto_strips_whitespace(self):
        """Пробелы удаляются из полей."""
        dto = TodoCreateDTO(title="  Task  ", description="  Desc  ")

        assert dto.title == "Task"
        assert dto.description == "Desc"

    def test_create_dto_empty_string_becomes_none(self):
        """Пустая строка преобразуется в None."""
        dto = TodoCreateDTO(title="Task", description="")

        assert dto.description is None

    def test_create_dto_whitespace_becomes_none(self):
        """Строка из пробелов преобразуется в None."""
        dto = TodoCreateDTO(title="Task", description="   ")

        assert dto.description is None

    def test_create_dto_title_too_long(self):
        """Слишком длинный заголовок вызывает ошибку."""
        with pytest.raises(ValidationError):
            TodoCreateDTO(title="a" * 201)

    def test_create_dto_description_too_long(self):
        """Слишком длинное описание вызывает ошибку."""
        with pytest.raises(ValidationError):
            TodoCreateDTO(title="Task", description="a" * 1001)


class TestTodoUpdateDTO:
    """Тесты для TodoUpdateDTO."""

    def test_valid_update_dto(self):
        """Создание валидного DTO для обновления."""
        dto = TodoUpdateDTO(title="New Title")

        assert dto.title == "New Title"
        assert dto.description is None

    def test_update_dto_all_fields_none_raises_error(self):
        """Нельзя создать DTO без полей для обновления."""
        with pytest.raises(ValidationError, match="At least one field"):
            TodoUpdateDTO()

    def test_update_dto_strips_whitespace(self):
        """Пробелы удаляются."""
        dto = TodoUpdateDTO(title="  New Title  ")

        assert dto.title == "New Title"

    def test_update_dto_with_description_only(self):
        """Можно обновить только описание."""
        dto = TodoUpdateDTO(description="New Description")

        assert dto.title is None
        assert dto.description == "New Description"

    def test_update_dto_remove_description(self):
        """Можно явно удалить описание."""
        dto = TodoUpdateDTO(title="Title", description=None)

        assert dto.description is None


class TestTodoResponseDTO:
    """Тесты для TodoResponseDTO."""

    def test_response_dto_from_entity(self):
        """Преобразование доменной сущности в DTO."""
        todo = Todo.create(title="Task", description="Description")
        dto = TodoResponseDTO.model_validate(todo)

        assert dto.id == todo.id
        assert dto.title == todo.title
        assert dto.description == todo.description
        assert dto.completed == todo.completed
        assert dto.created_at == todo.created_at
        assert dto.updated_at == todo.updated_at

    def test_response_dto_without_description(self):
        """DTO для задачи без описания."""
        todo = Todo.create(title="Task")
        dto = TodoResponseDTO.model_validate(todo)

        assert dto.description is None
