# Быстрый старт: Тестирование

## Подготовка

### 1. Установите зависимости

```bash
poetry install
```

### 2. Создайте тестовую БД

```bash
# Запустите PostgreSQL
docker-compose up -d

# Создайте тестовую базу
docker exec -it todo_postgres psql -U admin -c "CREATE DATABASE test_db;"
```

## 🚀 Запуск тестов

### Все тесты

```bash
./run_tests.sh all
# или
poetry run pytest
# или
make test
```

### Только unit тесты (быстрые, без БД)

```bash
./run_tests.sh unit
# или
poetry run pytest tests/unit/ -v
# или
make test-unit
```

### Integration тесты (с БД)

```bash
./run_tests.sh integration
# или
poetry run pytest tests/integration/ -v
# или
make test-integration
```

### E2E тесты (полный API)

```bash
./run_tests.sh e2e
# или
poetry run pytest tests/e2e/ -v
# или
make test-e2e
```

### С покрытием кода

```bash
./run_tests.sh cov
# или
poetry run pytest --cov=app --cov-report=html
# или
make test-cov

# Открыть HTML отчёт
open htmlcov/index.html
```

## Что тестируется

### Unit тесты (70% покрытия)

- ✅ Доменная логика (`Todo` entity)
- ✅ DTO валидация
- ✅ Бизнес-логика сервисов
- ✅ Исключения

**Особенности:**

- Без БД
- Без HTTP
- Используются фейковые репозитории
- Выполняются < 1 секунды

### Integration тесты (20% покрытия)

- ✅ Работа репозитория с PostgreSQL
- ✅ Маппинг domain ↔ ORM
- ✅ SQL queries
- ✅ Транзакции

**Особенности:**

- С реальной БД (test_db)
- Изоляция через транзакции
- Автоочистка после тестов
- Выполняются < 10 секунд

### E2E тесты (10% покрытия)

- ✅ HTTP endpoints
- ✅ Status codes
- ✅ Validation
- ✅ Полный flow (создание → обновление → удаление)

**Особенности:**

- Полный стек (FastAPI + БД)
- Тестирование через HTTP
- Проверка всего flow
- Выполняются < 30 секунд

## Статистика покрытия

```bash
# Терминальный отчёт
poetry run pytest --cov=app --cov-report=term-missing

# HTML отчёт с подробностями
poetry run pytest --cov=app --cov-report=html
open htmlcov/index.html
```

**Цель:** >80% покрытие кода

## Примеры тестов

### Unit тест

```python
def test_create_valid_todo():
    """Создание валидной задачи."""
    todo = Todo.create(title="Buy milk", description="From store")

    assert todo.title == "Buy milk"
    assert todo.description == "From store"
    assert todo.completed is False
```

### Integration тест

```python
@pytest.mark.asyncio
async def test_add_todo(db_session):
    """Сохранение задачи в БД."""
    repo = SqlAlchemyTodoRepository(db_session)
    todo = Todo.create(title="Task")

    await repo.add(todo)
    await db_session.commit()

    retrieved = await repo.get_by_id(todo.id)
    assert retrieved.title == "Task"
```

### E2E тест

```python
@pytest.mark.asyncio
async def test_create_todo_api(client):
    """Создание задачи через API."""
    response = await client.post(
        "/api/v1/todos",
        json={"title": "Buy milk"}
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Buy milk"
```

## Отладка тестов

### Остановка на первой ошибке

```bash
poetry run pytest -x
```

### Запуск конкретного теста

```bash
poetry run pytest tests/unit/test_todo_entity.py::TestTodoCreation::test_create_valid_todo
```

### С выводом print

```bash
poetry run pytest -s
```

### С подробным traceback

```bash
poetry run pytest --tb=long
```

### В режиме отладки (pdb)

```bash
poetry run pytest --pdb
```

## Создание новых тестов

### 1. Выберите тип теста

- **Unit** — для доменной логики, DTO, сервисов
- **Integration** — для репозиториев, БД
- **E2E** — для API endpoints

### 2. Создайте файл

```bash
# Unit
touch tests/unit/test_my_feature.py

# Integration
touch tests/integration/test_my_repository.py

# E2E
touch tests/e2e/test_my_api.py
```

### 3. Используйте шаблон

```python
"""Описание тестируемой функциональности."""
import pytest
from app.core.todo.entities import Todo


class TestMyFeature:
    """Группа тестов для фичи."""

    def test_happy_path(self):
        """Тест успешного сценария."""
        # Arrange
        todo = Todo.create(title="Task")

        # Act
        result = todo.mark_completed()

        # Assert
        assert result.completed is True

    def test_error_case(self):
        """Тест ошибочного сценария."""
        with pytest.raises(TodoValidationError):
            Todo.create(title="")
```

## Troubleshooting

### Проблема: Тесты не находят модули

```bash
# Решение: Запускайте через poetry
poetry run pytest
```

### Проблема: БД тесты падают

```bash
# Решение: Проверьте PostgreSQL
docker ps | grep postgres

# Создайте test_db
docker exec -it todo_postgres psql -U admin -c "CREATE DATABASE test_db;"
```

### Проблема: Async тесты не работают

```bash
# Решение: Убедитесь, что установлен pytest-asyncio
poetry add --group dev pytest-asyncio

# И используйте декоратор
@pytest.mark.asyncio
async def test_async_function():
    result = await async_func()
    assert result
```

### Проблема: Низкое покрытие

```bash
# Проверьте, какие файлы не покрыты
poetry run pytest --cov=app --cov-report=term-missing

# Добавьте тесты для непокрытых участков
```

## Дополнительные ресурсы

- [README по тестам](tests/README.md) — подробная документация
- [Best Practices](tests/BEST_PRACTICES.md) — принципы тестирования 2025
- [Pytest документация](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## Чек-лист перед коммитом

- [ ] Все тесты проходят (`./run_tests.sh all`)
- [ ] Покрытие >80% (`./run_tests.sh cov`)
- [ ] Новый код покрыт тестами
- [ ] Граничные случаи проверены
- [ ] CI/CD проходит

---

**Совет**: Запускайте `./run_tests.sh unit` часто — эти тесты очень быстрые!
