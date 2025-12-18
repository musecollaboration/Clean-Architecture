from uuid import UUID


class DomainError(Exception):
    """Базовое исключение для всех доменных ошибок."""
    pass


class TodoNotFoundError(DomainError):
    """Задача с указанным ID не найдена."""

    def __init__(self, todo_id: UUID):
        self.todo_id = todo_id
        super().__init__(f"Todo with id {todo_id} not found")


class TodoValidationError(DomainError):
    """Нарушение доменных правил при создании/обновлении задачи."""

    def __init__(self, message: str):
        super().__init__(message)
