# Best Practices для тестирования Clean Architecture проектов (2025)

## Принципы тестирования чистой архитектуры

### 1. Пирамида тестирования

```
         /\
        /  \  E2E (10%)
       /____\
      /      \  Integration (20%)
     /________\
    /          \  Unit (70%)
   /____________\
```

- **Unit тесты (70%)**: Быстрые, изолированные, тестируют отдельные компоненты
- **Integration тесты (20%)**: Тестируют взаимодействие компонентов
- **E2E тесты (10%)**: Тестируют полный flow через API

### 2. Независимость слоёв

✅ **Правильно:**

- Domain слой тестируется без зависимостей
- Application слой тестируется с фейковыми репозиториями
- Infrastructure слой тестируется с реальной БД

❌ **Неправильно:**

- Тестировать domain с БД
- Использовать моки везде
- Смешивать тесты разных слоёв

### 3. Фейки вместо моков

```python
# ❌ Плохо: Использование моков
mock_repo = Mock(spec=AbstractTodoRepository)
mock_repo.get_by_id.return_value = todo

# ✅ Хорошо: Использование фейкового репозитория
class FakeTodoRepository:
    def __init__(self):
        self.todos = {}

    async def get_by_id(self, todo_id):
        return self.todos.get(todo_id)
```

**Почему фейки лучше:**

- Ближе к реальному поведению
- Легче поддерживать
- Можно переиспользовать
- Проверяют реальное взаимодействие

### 4. Fixture-driven testing

```python
@pytest.fixture
def valid_todo() -> Todo:
    """Валидная доменная сущность."""
    return Todo.create(title="Test", description="Description")

@pytest.fixture
def service(fake_repo):
    """Сервис с фейковым репозиторием."""
    return TodoService(fake_repo)
```

**Преимущества:**

- Переиспользование кода
- Явные зависимости
- Лёгкая модификация

### 5. AAA Pattern (Arrange-Act-Assert)

```python
async def test_create_todo(self, service):
    # Arrange
    dto = TodoCreateDTO(title="Task", description="Description")

    # Act
    result = await service.create_todo(dto)

    # Assert
    assert result.title == "Task"
    assert result.completed is False
```

### 6. Изоляция тестов

✅ **Правильно:**

- Каждый тест независим
- Используются транзакции для БД
- Нет shared state между тестами

❌ **Неправильно:**

- Тесты зависят друг от друга
- Общие данные между тестами
- Порядок выполнения важен

### 7. Тестирование граничных случаев

```python
class TestTodoCreation:
    def test_create_valid_todo(self):
        """Happy path."""
        todo = Todo.create(title="Task")
        assert todo.title == "Task"

    def test_create_empty_title_raises_error(self):
        """Граничный случай: пустой заголовок."""
        with pytest.raises(TodoValidationError):
            Todo.create(title="")

    def test_create_too_long_title_raises_error(self):
        """Граничный случай: слишком длинный заголовок."""
        with pytest.raises(TodoValidationError):
            Todo.create(title="a" * 201)
```

### 8. Async/await правильно

```python
@pytest.mark.asyncio
async def test_create_todo(service):
    """Все async функции помечены @pytest.mark.asyncio."""
    result = await service.create_todo(dto)
    assert result is not None
```

### 9. Параметризованные тесты

```python
@pytest.mark.parametrize("title,expected", [
    ("Task", "Task"),
    ("  Task  ", "Task"),  # Пробелы удаляются
    ("TASK", "TASK"),
])
def test_title_normalization(title, expected):
    todo = Todo.create(title=title)
    assert todo.title == expected
```

### 10. Coverage ≠ Quality

✅ **80% покрытие + хорошие тесты**
❌ **100% покрытие + плохие тесты**

**Важнее:**

- Тестировать критическую логику
- Граничные случаи
- Error paths

## Структура тестов по слоям

### Domain Layer (Core)

```python
# tests/unit/test_todo_entity.py
class TestTodoCreation:
    def test_create_valid_todo(self):
        """Бизнес-логика без зависимостей."""
        todo = Todo.create(title="Task")
        assert todo.completed is False
```

**Что тестируем:**

- Создание сущностей
- Валидацию бизнес-правил
- Иммутабельность
- Методы обновления

### Application Layer

```python
# tests/unit/test_todo_service.py
@pytest.mark.asyncio
async def test_create_todo(service, fake_repo):
    """Use cases с фейковым репозиторием."""
    dto = TodoCreateDTO(title="Task")
    result = await service.create_todo(dto)
    assert result.title == "Task"
```

**Что тестируем:**

- Use cases
- Взаимодействие с репозиторием (через фейк)
- Обработку ошибок
- DTO преобразования

### Infrastructure Layer

```python
# tests/integration/test_todo_repository.py
@pytest.mark.asyncio
async def test_add_todo(db_session):
    """Реальная работа с БД."""
    repo = SqlAlchemyTodoRepository(db_session)
    todo = Todo.create(title="Task")
    await repo.add(todo)
    await db_session.commit()

    retrieved = await repo.get_by_id(todo.id)
    assert retrieved.title == "Task"
```

**Что тестируем:**

- Сохранение/извлечение из БД
- Маппинг между domain и ORM
- SQL queries
- Транзакции

### API Layer

```python
# tests/e2e/test_todo_api.py
@pytest.mark.asyncio
async def test_create_todo_api(client):
    """Полный flow через HTTP."""
    response = await client.post(
        "/api/v1/todos",
        json={"title": "Task"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Task"
```

**Что тестируем:**

- HTTP endpoints
- Status codes
- Validation
- Error handling
- Полный flow

## Производительность тестов

### Быстрые unit тесты

```bash
# Должны выполняться < 1 секунды
poetry run pytest tests/unit/ -v
# 50+ тестов за < 1s
```

### Умеренные integration тесты

```bash
# Должны выполняться < 10 секунд
poetry run pytest tests/integration/ -v
# 20+ тестов за < 10s
```

### Медленные e2e тесты

```bash
# Могут выполняться медленнее
poetry run pytest tests/e2e/ -v
# 15+ тестов за < 30s
```

## Инструменты и библиотеки (2025)

### Обязательные

- `pytest` — основной фреймворк
- `pytest-asyncio` — поддержка async/await
- `pytest-cov` — покрытие кода
- `httpx` — HTTP клиент для E2E

### Дополнительные

- `faker` — генерация тестовых данных
- `pytest-xdist` — параллельный запуск
- `pytest-watch` — автозапуск при изменениях
- `hypothesis` — property-based testing

### CI/CD

- GitHub Actions
- Coverage reporting (Codecov)
- Pre-commit hooks

## Антипаттерны

### ❌ 1. Тестирование реализации, а не поведения

```python
# Плохо
def test_internal_method(service):
    service._internal_method()  # Не тестируем приватные методы

# Хорошо
async def test_create_todo_behavior(service):
    result = await service.create_todo(dto)
    assert result.completed is False
```

### ❌ 2. Моки везде

```python
# Плохо
mock_repo = Mock()
mock_repo.get_by_id = AsyncMock(return_value=todo)

# Хорошо
fake_repo = FakeTodoRepository()
await fake_repo.add(todo)
```

### ❌ 3. Зависимость от порядка выполнения

```python
# Плохо
def test_1_create():
    global todo_id
    todo_id = create_todo()

def test_2_update():
    update_todo(todo_id)  # Зависит от test_1

# Хорошо
def test_update(todo):  # Фикстура создаёт todo
    update_todo(todo.id)
```

### ❌ 4. Тесты без assert

```python
# Плохо
async def test_create_todo(service):
    await service.create_todo(dto)  # Что проверяем?

# Хорошо
async def test_create_todo(service):
    result = await service.create_todo(dto)
    assert isinstance(result, TodoResponseDTO)
    assert result.title == "Task"
```

### ❌ 5. Флаки тесты (flaky tests)

```python
# Плохо
def test_with_sleep():
    time.sleep(0.1)  # Недетерминированность
    assert result

# Хорошо
async def test_with_proper_await():
    result = await async_function()
    assert result
```

## Continuous Improvement

1. **Запускайте тесты часто** — каждый коммит
2. **Мониторьте покрытие** — не ниже 80%
3. **Рефакторьте тесты** — как и prod код
4. **Удаляйте мёртвый код** — включая тесты
5. **Обновляйте зависимости** — pytest, httpx и т.д.

## Чек-лист перед коммитом

- [ ] Все тесты проходят
- [ ] Покрытие не упало
- [ ] Новые фичи покрыты тестами
- [ ] Граничные случаи проверены
- [ ] Тесты читаемые и понятные
- [ ] Нет флаки тестов
- [ ] CI/CD настроен и работает
