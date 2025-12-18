# Todo Service - Clean Architecture Example

> Production-ready FastAPI проект с чистой архитектурой, демонстрирующий best practices 2025 года

## Описание

Todo Service — это RESTful API для управления задачами (todos), построенный на принципах Clean Architecture. Проект демонстрирует современные подходы к разработке на Python с использованием FastAPI, SQLAlchemy, PostgreSQL и асинхронного программирования.

## Архитектура

Проект следует принципам **Clean Architecture** (Чистая архитектура) с чётким разделением слоёв и зависимостей:

```
┌─────────────────────────────────────────────────────────────┐
│                         API Layer                           │
│  (FastAPI endpoints, dependencies, routers)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    Application Layer                        │
│  (Use cases, services, DTOs, ports/interfaces)              │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                      Domain Layer                           │
│  (Business entities, domain logic, exceptions)              │
└─────────────────────────────────────────────────────────────┘
                     ▲
┌────────────────────┴────────────────────────────────────────┐
│                  Infrastructure Layer                       │
│  (Database, repositories, external services)                │
└─────────────────────────────────────────────────────────────┘
```

### Структура проекта

```
project-root/
├── app/
│   ├── api/                      # API слой (endpoints, роутеры)
│   │   └── v1/
│   │       ├── dependencies.py   # Dependency Injection
│   │       └── routers/
│   │           └── todo_router.py
│   │
│   ├── application/              # Слой use cases
│   │   └── todo/
│   │       ├── dto.py            # Data Transfer Objects
│   │       ├── ports.py          # Абстрактные интерфейсы
│   │       └── services/
│   │           └── todo_service.py
│   │
│   ├── core/                     # Доменный слой (чистый Python)
│   │   └── todo/
│   │       ├── entities.py       # Бизнес-сущности
│   │       └── exceptions.py     # Доменные исключения
│   │
│   ├── infrastructure/           # Инфраструктурный слой
│   │   ├── database/
│   │   │   ├── base.py          # SQLAlchemy Base
│   │   │   └── engine.py        # Async engine
│   │   └── persistence/
│   │       └── todo/
│   │           ├── models.py     # SQLAlchemy модели
│   │           └── todo_repository.py
│   │
│   ├── config/                   # Конфигурация
│   │   └── settings.py
│   │
│   ├── shared/                   # Общие утилиты
│   │   └── logging.py
│   │
│   ├── lifespan.py              # Lifecycle management
│   └── main.py                  # Точка входа
│
├── migrations/                   # Alembic миграции
├── tests/                        # Тесты
├── .env                          # Переменные окружения
├── .env.example                  # Шаблон для .env
├── alembic.ini                   # Конфигурация Alembic
├── docker-compose.yaml           # Docker конфигурация
└── pyproject.toml               # Poetry зависимости
```

## Принципы и паттерны

### Clean Architecture

- **Domain Layer (Core)**: Чистая бизнес-логика без зависимостей от фреймворков
- **Application Layer**: Use cases и бизнес-правила приложения
- **Infrastructure Layer**: Реализация внешних зависимостей (БД, API)
- **API Layer**: HTTP-интерфейс и обработка запросов

### SOLID принципы

- **S**ingle Responsibility: Каждый модуль отвечает за одну вещь
- **O**pen/Closed: Открыт для расширения, закрыт для модификации
- **L**iskov Substitution: Использование абстракций (ports)
- **I**nterface Segregation: Минимальные интерфейсы (AbstractTodoRepository)
- **D**ependency Inversion: Зависимость от абстракций, а не от конкретики

### Паттерны проектирования

- **Repository Pattern**: Абстракция доступа к данным
- **Dependency Injection**: Внедрение зависимостей через FastAPI Depends
- **Unit of Work**: Управление транзакциями на уровне запроса
- **DTO Pattern**: Разделение доменных сущностей и API моделей

## Технологии

- **FastAPI** - современный async веб-фреймворк
- **SQLAlchemy 2.0** - async ORM для работы с БД
- **PostgreSQL** - реляционная СУБД
- **Asyncpg** - асинхронный драйвер PostgreSQL
- **Alembic** - миграции базы данных
- **Pydantic v2** - валидация данных и настройки
- **Poetry** - управление зависимостями
- **Docker** - контейнеризация

## Установка и запуск

### Предварительные требования

- Python 3.12+
- Poetry
- Docker и Docker Compose

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd todo_service
```

### 2. Установка зависимостей

```bash
poetry install
```

### 3. Настройка окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` при необходимости:

```env
# Database
DATABASE_URL=postgresql+asyncpg://admin:admin1234@localhost:5432/db

# Application
APP_NAME=Todo Service
DEBUG=False
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=8000
```

### 4. Запуск PostgreSQL

```bash
docker-compose up -d
```

### 5. Применение миграций

```bash
poetry run alembic upgrade head
```

### 6. Запуск приложения

```bash
poetry run uvicorn app.main:app --reload
```

Приложение будет доступно по адресу: http://localhost:8000

## API Документация

После запуска приложения документация API доступна по адресам:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Основные endpoints

- `POST /api/v1/todos` - Создать новую задачу
- `GET /api/v1/todos` - Получить список всех задач
- `GET /api/v1/todos/{id}` - Получить задачу по ID
- `PATCH /api/v1/todos/{id}` - Обновить задачу
- `PATCH /api/v1/todos/{id}/complete` - Отметить задачу как выполненную
- `DELETE /api/v1/todos/{id}` - Удалить задачу

## База данных

### Создание миграции

```bash
poetry run alembic revision --autogenerate -m "описание изменений"
```

### Применение миграций

```bash
poetry run alembic upgrade head
```

### Откат миграции

```bash
poetry run alembic downgrade -1
```

## Тестирование

```bash
poetry run pytest
```

## Разработка

### Активация виртуального окружения

```bash
poetry shell
```

### Добавление зависимостей

```bash
poetry add <package-name>
poetry add --group dev <dev-package-name>
```

### Линтинг и форматирование

```bash
# Добавить ruff/black при необходимости
poetry add --group dev ruff black
poetry run ruff check .
poetry run black .
```

## Docker

### Запуск всех сервисов

```bash
docker-compose up -d
```

### Остановка сервисов

```bash
docker-compose down
```

### Просмотр логов

```bash
docker-compose logs -f
```

## Мониторинг БД

Проект включает CloudBeaver для работы с базой данных:

- URL: http://localhost:8978
- Подключение к БД:
  - Host: `db`
  - Port: `5432`
  - Database: `db`
  - User: `admin`
  - Password: `admin1234`

## Best Practices 2025

Этот проект демонстрирует:

- Async/await везде (FastAPI, SQLAlchemy, PostgreSQL)  
- Type hints для всех функций и методов  
- Pydantic v2 для валидации и настроек  
- Environment-based конфигурация через `.env`  
- Dependency Injection через FastAPI  
- Unit of Work с commit/rollback на уровне запроса  
- Чистая архитектура с разделением слоёв  
- Repository Pattern для доступа к данным  
- DTO для разделения API и domain моделей  
- Alembic для управления миграциями

## Лицензия

MIT

## Автор

https://stepik.org/a/223717


---

**Примечание**: Этот проект создан в образовательных целях для демонстрации современных подходов к разработке на Python и FastAPI.
