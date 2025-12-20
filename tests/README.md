# Тесты для Todo Service

Этот проект использует pytest для тестирования с полным покрытием всех слоёв чистой архитектуры.

## Структура тестов

```
tests/
├── unit/                      # Unit тесты (изолированные, быстрые)
│   ├── test_todo_entity.py   # Тесты доменной логики
│   ├── test_todo_dto.py      # Тесты DTO моделей
│   └── test_todo_service.py  # Тесты бизнес-логики
│
├── integration/               # Integration тесты (с БД)
│   └── test_todo_repository.py
│
├── e2e/                       # End-to-end тесты (полный API)
│   └── test_todo_api.py
│
├── conftest.py               # Общие фикстуры
├── pytest.ini                # Конфигурация pytest
└── README.md                 # Этот файл
```

## Типы тестов

### Unit тесты

- **Цель**: Изолированное тестирование отдельных компонентов
- **Скорость**: Очень быстрые (без БД, без HTTP)
- **Зависимости**: Минимальные, используются моки и фейки
- **Примеры**:
  - Доменная логика (Todo entity)
  - DTO валидация
  - Бизнес-логика сервисов (с фейковым репозиторием)

### Integration тесты

- **Цель**: Тестирование взаимодействия компонентов
- **Скорость**: Средняя (используется тестовая БД)
- **Зависимости**: PostgreSQL
- **Примеры**:
  - Работа репозитория с реальной БД
  - Маппинг между доменом и ORM

### E2E тесты

- **Цель**: Тестирование полного flow через API
- **Скорость**: Медленные (полный стек)
- **Зависимости**: Весь стек (FastAPI + БД)
- **Примеры**:
  - HTTP endpoints
  - Полный жизненный цикл задачи

## Установка зависимостей

```bash
poetry add --group dev pytest pytest-asyncio pytest-cov httpx
```

## Запуск тестов

### Все тесты

```bash
poetry run pytest
```

### Только unit тесты (быстрые)

```bash
poetry run pytest tests/unit/
```

### Только integration тесты

```bash
poetry run pytest tests/integration/
```

### Только e2e тесты

```bash
poetry run pytest tests/e2e/
```

### С покрытием кода

```bash
poetry run pytest --cov=app --cov-report=html
```

### Конкретный файл

```bash
poetry run pytest tests/unit/test_todo_entity.py
```

### Конкретный тест

```bash
poetry run pytest tests/unit/test_todo_entity.py::TestTodoCreation::test_create_valid_todo
```

### С подробным выводом

```bash
poetry run pytest -v
```

### С выводом print

```bash
poetry run pytest -s
```

## Тестовая база данных

Для integration и e2e тестов используется отдельная тестовая БД.

### Настройка

1. Создайте тестовую БД:

```bash
docker exec -it todo_postgres psql -U admin -c "CREATE DATABASE test_db;"
```

2. БД автоматически создаётся и очищается для каждого теста через фикстуры в `conftest.py`.

### Изоляция тестов

- Каждый тест работает в своей транзакции
- После теста транзакция откатывается
- Таблицы создаются и удаляются для каждого теста

## Best Practices

### Unit тесты

✅ **Правильно:**

- Тестируйте одну функцию/метод за раз
- Используйте фейковые репозитории, а не моки
- Не зависьте от БД или HTTP

❌ **Неправильно:**

- Тестировать несколько компонентов вместе
- Использовать реальную БД
- Зависеть от внешних сервисов

### Integration тесты

✅ **Правильно:**

- Тестируйте взаимодействие с реальной БД
- Проверяйте корректность маппинга
- Используйте транзакции для изоляции

❌ **Неправильно:**

- Использовать моки вместо реальной БД
- Не очищать данные после тестов
- Зависеть от порядка выполнения тестов

### E2E тесты

✅ **Правильно:**

- Тестируйте полный flow через HTTP
- Проверяйте status codes и структуру ответов
- Тестируйте как success, так и error cases

❌ **Неправильно:**

- Дублировать unit тесты
- Тестировать только happy path
- Игнорировать валидацию

## Покрытие кода

Цель: **>80% покрытие**

Проверить покрытие:

```bash
poetry run pytest --cov=app --cov-report=term-missing
```

HTML отчёт:

```bash
poetry run pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## CI/CD

Тесты должны запускаться автоматически при каждом коммите.

Пример GitHub Actions:

```yaml
- name: Run tests
  run: |
    poetry run pytest --cov=app --cov-report=xml
```

## Отладка тестов

### Остановка на первой ошибке

```bash
poetry run pytest -x
```

### Запуск последних упавших тестов

```bash
poetry run pytest --lf
```

### Использование pdb

```bash
poetry run pytest --pdb
```

### Логирование в тестах

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Принципы чистой архитектуры в тестах

1. **Unit тесты домена** — тестируют бизнес-логику без зависимостей
2. **Фейковые репозитории** — вместо моков для сервисов
3. **Тестовая БД** — для integration тестов
4. **Изоляция слоёв** — каждый слой тестируется отдельно
5. **Dependency Injection** — легко подменяем зависимости

## Полезные команды

```bash
# Запустить все тесты с покрытием
poetry run pytest --cov=app

# Только быстрые тесты (unit)
poetry run pytest tests/unit/ -v

# Только медленные (integration + e2e)
poetry run pytest tests/integration/ tests/e2e/

# Параллельный запуск (требует pytest-xdist)
poetry run pytest -n auto

# Генерация HTML отчёта
poetry run pytest --cov=app --cov-report=html
```

## Troubleshooting

### Проблема: Тесты не находят модули

**Решение**: Убедитесь, что запускаете через `poetry run pytest`

### Проблема: БД тесты падают

**Решение**: Проверьте, что PostgreSQL запущен и test_db создана

### Проблема: Async тесты не работают

**Решение**: Установите `pytest-asyncio` и используйте `@pytest.mark.asyncio`

## Дополнительные ресурсы

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Testing FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)
- [Clean Architecture Testing](https://blog.cleancoder.com/uncle-bob/2017/10/03/TestContravariance.html)
