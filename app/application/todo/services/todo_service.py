from uuid import UUID
from loguru import logger

from app.application.todo.dto import TodoCreateDTO, TodoUpdateDTO, TodoResponseDTO
from app.application.todo.ports import AbstractTodoRepository
from app.core.todo.entities import Todo
from app.core.todo.exceptions import TodoNotFoundError


class TodoService:
    def __init__(self, repo: AbstractTodoRepository):
        self.repo = repo

    async def create_todo(self, dto: TodoCreateDTO) -> TodoResponseDTO:
        logger.info(f"Creating new todo: title='{dto.title}'")
        todo = Todo.create(title=dto.title, description=dto.description)
        await self.repo.add(todo)
        logger.info(f"Todo created successfully: id={todo.id}")
        return TodoResponseDTO.model_validate(todo)

    async def get_todo(self, todo_id: UUID) -> TodoResponseDTO:
        logger.debug(f"Fetching todo: id={todo_id}")
        todo = await self.repo.get_by_id(todo_id)
        if todo is None:
            logger.warning(f"Todo not found: id={todo_id}")
            raise TodoNotFoundError(todo_id)
        return TodoResponseDTO.model_validate(todo)

    async def list_todos(self) -> list[TodoResponseDTO]:
        logger.debug("Fetching all todos")
        todos = await self.repo.list_all()
        logger.info(f"Retrieved {len(todos)} todos")
        return [TodoResponseDTO.model_validate(t) for t in todos]

    async def update_todo(self, todo_id: UUID, dto: TodoUpdateDTO) -> TodoResponseDTO:
        logger.info(f"Updating todo: id={todo_id}")
        todo = await self.repo.get_by_id(todo_id)
        if todo is None:
            logger.warning(f"Todo not found for update: id={todo_id}")
            raise TodoNotFoundError(todo_id)

        updated_todo = todo.update(title=dto.title, description=dto.description)
        await self.repo.update(updated_todo)
        logger.info(f"Todo updated successfully: id={todo_id}")
        return TodoResponseDTO.model_validate(updated_todo)

    async def complete_todo(self, todo_id: UUID) -> TodoResponseDTO:
        logger.info(f"Completing todo: id={todo_id}")
        todo = await self.repo.get_by_id(todo_id)
        if todo is None:
            logger.warning(f"Todo not found for completion: id={todo_id}")
            raise TodoNotFoundError(todo_id)

        completed_todo = todo.complete()
        await self.repo.update(completed_todo)
        logger.info(f"Todo completed successfully: id={todo_id}")
        return TodoResponseDTO.model_validate(completed_todo)

    async def delete_todo(self, todo_id: UUID) -> None:
        logger.info(f"Deleting todo: id={todo_id}")
        todo = await self.repo.get_by_id(todo_id)
        if todo is None:
            logger.warning(f"Todo not found for deletion: id={todo_id}")
            raise TodoNotFoundError(todo_id)
        await self.repo.delete(todo_id)
        logger.info(f"Todo deleted successfully: id={todo_id}")
