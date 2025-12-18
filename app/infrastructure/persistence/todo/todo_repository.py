from uuid import UUID
from loguru import logger
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.todo.ports import AbstractTodoRepository
from app.core.todo.entities import Todo
from app.infrastructure.persistence.todo.models import TodoModel


class SqlAlchemyTodoRepository(AbstractTodoRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, todo: Todo) -> None:
        logger.debug(f"Adding todo to database: id={todo.id}")
        db_todo = TodoModel.from_entity(todo)
        self.session.add(db_todo)
        # await self.session.flush() не обязательно — commit в UoW

    async def get_by_id(self, todo_id: UUID) -> Todo | None:
        logger.debug(f"Querying todo by id: {todo_id}")
        stmt = select(TodoModel).where(TodoModel.id == todo_id)
        result = await self.session.execute(stmt)
        db_todo = result.scalar_one_or_none()
        return db_todo.to_entity() if db_todo else None

    async def list_all(self) -> list[Todo]:
        logger.debug("Querying all todos from database")
        stmt = select(TodoModel).order_by(TodoModel.created_at.desc())
        result = await self.session.execute(stmt)
        todos = [db_todo.to_entity() for db_todo in result.scalars().all()]
        logger.debug(f"Found {len(todos)} todos in database")
        return todos

    async def update(self, todo: Todo) -> None:
        logger.debug(f"Updating todo in database: id={todo.id}")
        # Благодаря иммутабельности домена — ищем и обновляем
        stmt = select(TodoModel).where(TodoModel.id == todo.id)
        result = await self.session.execute(stmt)
        db_todo = result.scalar_one_or_none()
        if db_todo:
            db_todo.update_from_entity(todo)
        # flush/commit в UoW

    async def delete(self, todo_id: UUID) -> None:
        logger.debug(f"Deleting todo from database: id={todo_id}")
        stmt = delete(TodoModel).where(TodoModel.id == todo_id)
        await self.session.execute(stmt)
        # commit в UoW
