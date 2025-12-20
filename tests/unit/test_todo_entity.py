"""Unit тесты для доменной сущности Todo."""
import pytest
from datetime import datetime
from uuid import UUID

from app.core.todo.entities import Todo
from app.core.todo.exceptions import TodoValidationError


class TestTodoCreation:
    """Тесты создания задачи."""

    def test_create_valid_todo(self):
        """Создание валидной задачи с заголовком и описанием."""
        todo = Todo.create(title="Buy milk", description="From the store")

        assert isinstance(todo.id, UUID)
        assert todo.title == "Buy milk"
        assert todo.description == "From the store"
        assert todo.completed is False
        assert isinstance(todo.created_at, datetime)
        assert isinstance(todo.updated_at, datetime)

    def test_create_todo_without_description(self):
        """Создание задачи без описания."""
        todo = Todo.create(title="Buy milk")

        assert todo.title == "Buy milk"
        assert todo.description is None
        assert todo.completed is False

    def test_create_todo_strips_whitespace(self):
        """Пробелы удаляются из заголовка и описания."""
        todo = Todo.create(title="  Buy milk  ", description="  From store  ")

        assert todo.title == "Buy milk"
        assert todo.description == "From store"

    def test_create_todo_empty_title_raises_error(self):
        """Пустой заголовок вызывает ошибку."""
        with pytest.raises(TodoValidationError, match="Title cannot be empty"):
            Todo.create(title="")

    def test_create_todo_whitespace_only_title_raises_error(self):
        """Заголовок из одних пробелов вызывает ошибку."""
        with pytest.raises(TodoValidationError, match="Title cannot be empty"):
            Todo.create(title="   ")

    def test_create_todo_too_long_title_raises_error(self):
        """Слишком длинный заголовок вызывает ошибку."""
        long_title = "a" * 201
        with pytest.raises(TodoValidationError, match="Title cannot exceed 200 characters"):
            Todo.create(title=long_title)

    def test_create_todo_empty_description_becomes_none(self):
        """Пустое описание преобразуется в None."""
        todo = Todo.create(title="Task", description="")
        assert todo.description is None

    def test_create_todo_whitespace_description_becomes_none(self):
        """Описание из пробелов преобразуется в None."""
        todo = Todo.create(title="Task", description="   ")
        assert todo.description is None


class TestTodoUpdate:
    """Тесты обновления задачи."""

    def test_update_title(self):
        """Обновление заголовка создаёт новую версию задачи."""
        original = Todo.create(title="Old Title", description="Description")
        updated = original.update(title="New Title")

        assert updated.id == original.id
        assert updated.title == "New Title"
        assert updated.description == "Description"
        assert updated.completed == original.completed
        assert updated.updated_at > original.updated_at

    def test_update_description(self):
        """Обновление описания создаёт новую версию задачи."""
        original = Todo.create(title="Title", description="Old Description")
        updated = original.update(description="New Description")

        assert updated.title == "Title"
        assert updated.description == "New Description"
        assert updated.updated_at > original.updated_at

    def test_update_remove_description(self):
        """Описание можно удалить, передав пустую строку."""
        original = Todo.create(title="Title", description="Description")
        updated = original.update(description="")

        assert updated.description is None

    def test_update_empty_title_raises_error(self):
        """Нельзя обновить заголовок на пустой."""
        original = Todo.create(title="Title")
        with pytest.raises(TodoValidationError, match="Title cannot be empty"):
            original.update(title="")

    def test_update_preserves_immutability(self):
        """Оригинальная сущность не изменяется при обновлении."""
        original = Todo.create(title="Original")
        updated = original.update(title="Updated")

        assert original.title == "Original"
        assert updated.title == "Updated"
        assert original is not updated


class TestTodoCompletion:
    """Тесты завершения задачи."""

    def test_mark_completed(self):
        """Задачу можно отметить как выполненную."""
        todo = Todo.create(title="Task")
        completed = todo.complete()

        assert completed.completed is True
        assert completed.updated_at > todo.updated_at
        assert todo.completed is False  # оригинал не изменился

    def test_mark_completed_already_completed(self):
        """Повторное завершение задачи не вызывает ошибку."""
        todo = Todo.create(title="Task")
        completed_once = todo.complete()
        completed_twice = completed_once.complete()

        assert completed_twice.completed is True


class TestTodoImmutability:
    """Тесты иммутабельности сущности."""

    def test_todo_is_frozen(self):
        """Нельзя изменить поля напрямую."""
        todo = Todo.create(title="Task")

        with pytest.raises(AttributeError):
            todo.title = "New Title"  # type: ignore

    def test_todo_returns_new_instance_on_update(self):
        """update() возвращает новый экземпляр."""
        original = Todo.create(title="Original")
        updated = original.update(title="Updated")

        assert id(original) != id(updated)
