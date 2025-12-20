"""Unit тесты для TodoService."""
import pytest
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock

from app.application.todo.services.todo_service import TodoService
from app.application.todo.dto import TodoCreateDTO, TodoUpdateDTO, TodoResponseDTO
from app.core.todo.entities import Todo
from app.core.todo.exceptions import TodoNotFoundError


class FakeTodoRepository:
    """Фейковый репозиторий для тестирования сервиса."""

    def __init__(self):
        self.todos: dict[UUID, Todo] = {}

    async def add(self, todo: Todo) -> None:
        self.todos[todo.id] = todo

    async def get_by_id(self, todo_id: UUID) -> Todo | None:
        return self.todos.get(todo_id)

    async def list_all(self) -> list[Todo]:
        return list(self.todos.values())

    async def update(self, todo: Todo) -> None:
        if todo.id not in self.todos:
            raise TodoNotFoundError(todo.id)
        self.todos[todo.id] = todo

    async def delete(self, todo_id: UUID) -> None:
        if todo_id in self.todos:
            del self.todos[todo_id]


@pytest.fixture
def fake_repo():
    """Фикстура для фейкового репозитория."""
    return FakeTodoRepository()


@pytest.fixture
def service(fake_repo):
    """Фикстура для сервиса с фейковым репозиторием."""
    return TodoService(fake_repo)


class TestTodoServiceCreate:
    """Тесты создания задачи через сервис."""

    @pytest.mark.asyncio
    async def test_create_todo(self, service, fake_repo):
        """Создание задачи сохраняет её в репозиторий."""
        dto = TodoCreateDTO(title="New Task", description="Description")
        result = await service.create_todo(dto)

        assert isinstance(result, TodoResponseDTO)
        assert result.title == "New Task"
        assert result.description == "Description"
        assert result.completed is False

        # Проверяем, что задача сохранена
        saved_todo = await fake_repo.get_by_id(result.id)
        assert saved_todo is not None
        assert saved_todo.title == "New Task"

    @pytest.mark.asyncio
    async def test_create_todo_without_description(self, service):
        """Создание задачи без описания."""
        dto = TodoCreateDTO(title="Task")
        result = await service.create_todo(dto)

        assert result.description is None


class TestTodoServiceGet:
    """Тесты получения задачи."""

    @pytest.mark.asyncio
    async def test_get_existing_todo(self, service, fake_repo):
        """Получение существующей задачи."""
        todo = Todo.create(title="Existing Task")
        await fake_repo.add(todo)

        result = await service.get_todo(todo.id)

        assert result.id == todo.id
        assert result.title == "Existing Task"

    @pytest.mark.asyncio
    async def test_get_nonexistent_todo_raises_error(self, service):
        """Получение несуществующей задачи вызывает ошибку."""
        random_id = uuid4()

        with pytest.raises(TodoNotFoundError) as exc_info:
            await service.get_todo(random_id)

        assert exc_info.value.todo_id == random_id


class TestTodoServiceList:
    """Тесты получения списка задач."""

    @pytest.mark.asyncio
    async def test_list_empty(self, service):
        """Список пустой, если задач нет."""
        result = await service.list_todos()

        assert result == []

    @pytest.mark.asyncio
    async def test_list_multiple_todos(self, service, fake_repo):
        """Список возвращает все задачи."""
        todo1 = Todo.create(title="Task 1")
        todo2 = Todo.create(title="Task 2")
        await fake_repo.add(todo1)
        await fake_repo.add(todo2)

        result = await service.list_todos()

        assert len(result) == 2
        titles = {dto.title for dto in result}
        assert titles == {"Task 1", "Task 2"}


class TestTodoServiceUpdate:
    """Тесты обновления задачи."""

    @pytest.mark.asyncio
    async def test_update_todo_title(self, service, fake_repo):
        """Обновление заголовка задачи."""
        todo = Todo.create(title="Old Title", description="Description")
        await fake_repo.add(todo)

        dto = TodoUpdateDTO(title="New Title")
        result = await service.update_todo(todo.id, dto)

        assert result.title == "New Title"
        assert result.description == "Description"

        # Проверяем сохранение
        updated = await fake_repo.get_by_id(todo.id)
        assert updated.title == "New Title"

    @pytest.mark.asyncio
    async def test_update_nonexistent_todo_raises_error(self, service):
        """Обновление несуществующей задачи вызывает ошибку."""
        random_id = uuid4()
        dto = TodoUpdateDTO(title="New Title")

        with pytest.raises(TodoNotFoundError):
            await service.update_todo(random_id, dto)


class TestTodoServiceComplete:
    """Тесты завершения задачи."""

    @pytest.mark.asyncio
    async def test_complete_todo(self, service, fake_repo):
        """Завершение задачи изменяет статус."""
        todo = Todo.create(title="Task")
        await fake_repo.add(todo)

        result = await service.complete_todo(todo.id)

        assert result.completed is True

        # Проверяем сохранение
        completed = await fake_repo.get_by_id(todo.id)
        assert completed is not None
        assert completed.completed is True

    @pytest.mark.asyncio
    async def test_complete_nonexistent_todo_raises_error(self, service):
        """Завершение несуществующей задачи вызывает ошибку."""
        random_id = uuid4()

        with pytest.raises(TodoNotFoundError):
            await service.complete_todo(random_id)


class TestTodoServiceDelete:
    """Тесты удаления задачи."""

    @pytest.mark.asyncio
    async def test_delete_existing_todo(self, service, fake_repo):
        """Удаление существующей задачи."""
        todo = Todo.create(title="Task to delete")
        await fake_repo.add(todo)

        await service.delete_todo(todo.id)

        # Проверяем, что задача удалена
        deleted = await fake_repo.get_by_id(todo.id)
        assert deleted is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_todo_raises_error(self, service):
        """Удаление несуществующей задачи вызывает ошибку."""
        random_id = uuid4()

        with pytest.raises(TodoNotFoundError):
            await service.delete_todo(random_id)
