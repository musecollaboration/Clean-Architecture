"""E2E тесты для API endpoints Todo."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestTodoAPICreate:
    """E2E тесты создания задачи через API."""

    async def test_create_todo_success(self, client: AsyncClient):
        """Создание задачи возвращает 201 и корректные данные."""
        response = await client.post(
            "/api/v1/todos",
            json={"title": "Buy milk", "description": "From the store"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy milk"
        assert data["description"] == "From the store"
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_todo_without_description(self, client: AsyncClient):
        """Создание задачи без описания."""
        response = await client.post(
            "/api/v1/todos",
            json={"title": "Task without description"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Task without description"
        assert data["description"] is None

    async def test_create_todo_empty_title_returns_422(self, client: AsyncClient):
        """Пустой заголовок возвращает 422."""
        response = await client.post(
            "/api/v1/todos",
            json={"title": ""}
        )

        assert response.status_code == 422

    async def test_create_todo_missing_title_returns_422(self, client: AsyncClient):
        """Отсутствие заголовка возвращает 422."""
        response = await client.post(
            "/api/v1/todos",
            json={"description": "No title"}
        )

        assert response.status_code == 422

    async def test_create_todo_title_too_long_returns_422(self, client: AsyncClient):
        """Слишком длинный заголовок возвращает 422."""
        response = await client.post(
            "/api/v1/todos",
            json={"title": "a" * 201}
        )

        assert response.status_code == 422


@pytest.mark.asyncio
class TestTodoAPIGet:
    """E2E тесты получения задачи."""

    async def test_get_existing_todo(self, client: AsyncClient):
        """Получение существующей задачи возвращает 200."""
        # Создаём задачу
        create_response = await client.post(
            "/api/v1/todos",
            json={"title": "Test Task"}
        )
        todo_id = create_response.json()["id"]

        # Получаем задачу
        response = await client.get(f"/api/v1/todos/{todo_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == todo_id
        assert data["title"] == "Test Task"

    async def test_get_nonexistent_todo_returns_404(self, client: AsyncClient):
        """Получение несуществующей задачи возвращает 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/todos/{fake_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_get_invalid_uuid_returns_422(self, client: AsyncClient):
        """Невалидный UUID возвращает 422."""
        response = await client.get("/api/v1/todos/invalid-uuid")

        assert response.status_code == 422


@pytest.mark.asyncio
class TestTodoAPIList:
    """E2E тесты получения списка задач."""

    async def test_list_empty(self, client: AsyncClient):
        """Пустой список возвращает 200 и []."""
        response = await client.get("/api/v1/todos")

        assert response.status_code == 200
        assert response.json() == []

    async def test_list_multiple_todos(self, client: AsyncClient):
        """Список возвращает все задачи."""
        # Создаём несколько задач
        await client.post("/api/v1/todos", json={"title": "Task 1"})
        await client.post("/api/v1/todos", json={"title": "Task 2"})
        await client.post("/api/v1/todos", json={"title": "Task 3"})

        response = await client.get("/api/v1/todos")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        titles = {todo["title"] for todo in data}
        assert titles == {"Task 1", "Task 2", "Task 3"}

    async def test_list_ordered_by_created_at_desc(self, client: AsyncClient):
        """Задачи отсортированы по дате создания (новые первыми)."""
        response1 = await client.post("/api/v1/todos", json={"title": "First"})
        response2 = await client.post("/api/v1/todos", json={"title": "Second"})

        response = await client.get("/api/v1/todos")
        data = response.json()

        # Вторая задача должна быть первой
        assert data[0]["title"] == "Second"
        assert data[1]["title"] == "First"


@pytest.mark.asyncio
class TestTodoAPIUpdate:
    """E2E тесты обновления задачи."""

    async def test_update_todo_title(self, client: AsyncClient):
        """Обновление заголовка возвращает 200."""
        # Создаём задачу
        create_response = await client.post(
            "/api/v1/todos",
            json={"title": "Old Title", "description": "Description"}
        )
        todo_id = create_response.json()["id"]

        # Обновляем
        response = await client.patch(
            f"/api/v1/todos/{todo_id}",
            json={"title": "New Title"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["description"] == "Description"

    async def test_update_todo_description(self, client: AsyncClient):
        """Обновление описания возвращает 200."""
        create_response = await client.post(
            "/api/v1/todos",
            json={"title": "Title"}
        )
        todo_id = create_response.json()["id"]

        response = await client.patch(
            f"/api/v1/todos/{todo_id}",
            json={"description": "New Description"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "New Description"

    async def test_update_nonexistent_todo_returns_404(self, client: AsyncClient):
        """Обновление несуществующей задачи возвращает 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.patch(
            f"/api/v1/todos/{fake_id}",
            json={"title": "New Title"}
        )

        assert response.status_code == 404

    async def test_update_empty_body_returns_422(self, client: AsyncClient):
        """Пустое тело запроса возвращает 422."""
        create_response = await client.post(
            "/api/v1/todos",
            json={"title": "Task"}
        )
        todo_id = create_response.json()["id"]

        response = await client.patch(f"/api/v1/todos/{todo_id}", json={})

        assert response.status_code == 422


@pytest.mark.asyncio
class TestTodoAPIComplete:
    """E2E тесты завершения задачи."""

    async def test_complete_todo(self, client: AsyncClient):
        """Завершение задачи возвращает 200."""
        # Создаём задачу
        create_response = await client.post(
            "/api/v1/todos",
            json={"title": "Task to complete"}
        )
        todo_id = create_response.json()["id"]

        # Завершаем
        response = await client.patch(f"/api/v1/todos/{todo_id}/complete")

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True

    async def test_complete_nonexistent_todo_returns_404(self, client: AsyncClient):
        """Завершение несуществующей задачи возвращает 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.patch(f"/api/v1/todos/{fake_id}/complete")

        assert response.status_code == 404


@pytest.mark.asyncio
class TestTodoAPIDelete:
    """E2E тесты удаления задачи."""

    async def test_delete_todo(self, client: AsyncClient):
        """Удаление задачи возвращает 204."""
        # Создаём задачу
        create_response = await client.post(
            "/api/v1/todos",
            json={"title": "Task to delete"}
        )
        todo_id = create_response.json()["id"]

        # Удаляем
        response = await client.delete(f"/api/v1/todos/{todo_id}")

        assert response.status_code == 204

        # Проверяем, что задача действительно удалена
        get_response = await client.get(f"/api/v1/todos/{todo_id}")
        assert get_response.status_code == 404

    async def test_delete_nonexistent_todo_returns_404(self, client: AsyncClient):
        """Удаление несуществующей задачи возвращает 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(f"/api/v1/todos/{fake_id}")

        assert response.status_code == 404


@pytest.mark.asyncio
class TestTodoAPIFlow:
    """E2E тесты полного flow работы с задачами."""

    async def test_complete_todo_flow(self, client: AsyncClient):
        """Полный цикл: создание → получение → обновление → завершение → удаление."""
        # 1. Создание
        create_response = await client.post(
            "/api/v1/todos",
            json={"title": "Learn FastAPI", "description": "Complete tutorial"}
        )
        assert create_response.status_code == 201
        todo_id = create_response.json()["id"]

        # 2. Получение
        get_response = await client.get(f"/api/v1/todos/{todo_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Learn FastAPI"

        # 3. Обновление
        update_response = await client.patch(
            f"/api/v1/todos/{todo_id}",
            json={"title": "Master FastAPI"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Master FastAPI"

        # 4. Завершение
        complete_response = await client.patch(f"/api/v1/todos/{todo_id}/complete")
        assert complete_response.status_code == 200
        assert complete_response.json()["completed"] is True

        # 5. Удаление
        delete_response = await client.delete(f"/api/v1/todos/{todo_id}")
        assert delete_response.status_code == 204

        # 6. Проверка удаления
        final_get = await client.get(f"/api/v1/todos/{todo_id}")
        assert final_get.status_code == 404
