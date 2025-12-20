"""Integration тесты для TodoRepository."""
import pytest
from uuid import uuid4

from app.infrastructure.persistence.todo.todo_repository import SqlAlchemyTodoRepository
from app.core.todo.entities import Todo
from app.core.todo.exceptions import TodoNotFoundError


@pytest.mark.asyncio
class TestTodoRepositoryAdd:
    """Тесты добавления задачи в БД."""

    async def test_add_todo(self, db_session):
        """Добавление задачи сохраняет её в БД."""
        repo = SqlAlchemyTodoRepository(db_session)
        todo = Todo.create(title="Test Task", description="Description")

        await repo.add(todo)
        await db_session.commit()

        # Проверяем, что задача сохранена
        retrieved = await repo.get_by_id(todo.id)
        assert retrieved is not None
        assert retrieved.id == todo.id
        assert retrieved.title == "Test Task"
        assert retrieved.description == "Description"

    async def test_add_todo_without_description(self, db_session):
        """Добавление задачи без описания."""
        repo = SqlAlchemyTodoRepository(db_session)
        todo = Todo.create(title="Task")

        await repo.add(todo)
        await db_session.commit()

        retrieved = await repo.get_by_id(todo.id)
        assert retrieved.description is None


@pytest.mark.asyncio
class TestTodoRepositoryGet:
    """Тесты получения задачи из БД."""

    async def test_get_existing_todo(self, db_session):
        """Получение существующей задачи."""
        repo = SqlAlchemyTodoRepository(db_session)
        todo = Todo.create(title="Existing Task")
        await repo.add(todo)
        await db_session.commit()

        retrieved = await repo.get_by_id(todo.id)

        assert retrieved is not None
        assert retrieved.id == todo.id
        assert retrieved.title == "Existing Task"

    async def test_get_nonexistent_todo_returns_none(self, db_session):
        """Получение несуществующей задачи возвращает None."""
        repo = SqlAlchemyTodoRepository(db_session)
        random_id = uuid4()

        result = await repo.get_by_id(random_id)

        assert result is None


@pytest.mark.asyncio
class TestTodoRepositoryListAll:
    """Тесты получения списка всех задач."""

    async def test_list_empty(self, db_session):
        """Пустой список, если задач нет."""
        repo = SqlAlchemyTodoRepository(db_session)

        result = await repo.list_all()

        assert result == []

    async def test_list_multiple_todos(self, db_session):
        """Список возвращает все задачи."""
        repo = SqlAlchemyTodoRepository(db_session)
        todo1 = Todo.create(title="Task 1")
        todo2 = Todo.create(title="Task 2")
        await repo.add(todo1)
        await repo.add(todo2)
        await db_session.commit()

        result = await repo.list_all()

        assert len(result) == 2
        titles = {todo.title for todo in result}
        assert titles == {"Task 1", "Task 2"}

    async def test_list_ordered_by_created_at_desc(self, db_session):
        """Задачи отсортированы по дате создания (новые первыми)."""
        repo = SqlAlchemyTodoRepository(db_session)
        todo1 = Todo.create(title="First")
        todo2 = Todo.create(title="Second")
        await repo.add(todo1)
        await repo.add(todo2)
        await db_session.commit()

        result = await repo.list_all()

        # Вторая задача должна быть первой (новая)
        assert result[0].title == "Second"
        assert result[1].title == "First"


@pytest.mark.asyncio
class TestTodoRepositoryUpdate:
    """Тесты обновления задачи."""

    async def test_update_todo(self, db_session):
        """Обновление задачи изменяет её в БД."""
        repo = SqlAlchemyTodoRepository(db_session)
        todo = Todo.create(title="Original", description="Original Description")
        await repo.add(todo)
        await db_session.commit()

        updated_todo = todo.update(title="Updated")
        await repo.update(updated_todo)
        await db_session.commit()

        retrieved = await repo.get_by_id(todo.id)
        assert retrieved.title == "Updated"
        assert retrieved.description == "Original Description"

    async def test_update_nonexistent_todo_does_nothing(self, db_session):
        """Обновление несуществующей задачи не вызывает ошибку."""
        repo = SqlAlchemyTodoRepository(db_session)
        fake_todo = Todo.create(title="Fake")

        # Не должно вызывать ошибку
        await repo.update(fake_todo)
        await db_session.commit()


@pytest.mark.asyncio
class TestTodoRepositoryDelete:
    """Тесты удаления задачи."""

    async def test_delete_existing_todo(self, db_session):
        """Удаление существующей задачи."""
        repo = SqlAlchemyTodoRepository(db_session)
        todo = Todo.create(title="To Delete")
        await repo.add(todo)
        await db_session.commit()

        await repo.delete(todo.id)
        await db_session.commit()

        # Проверяем, что задача удалена
        result = await repo.get_by_id(todo.id)
        assert result is None

    async def test_delete_nonexistent_todo_does_nothing(self, db_session):
        """Удаление несуществующей задачи не вызывает ошибку."""
        repo = SqlAlchemyTodoRepository(db_session)
        random_id = uuid4()

        # Не должно вызывать ошибку
        await repo.delete(random_id)
        await db_session.commit()
