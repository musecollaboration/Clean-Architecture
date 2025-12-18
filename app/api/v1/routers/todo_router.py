from fastapi import APIRouter, Depends, status
from uuid import UUID
from app.application.todo.dto import (
    TodoCreateDTO, TodoUpdateDTO, TodoResponseDTO
)
from app.application.todo.services.todo_service import TodoService
from app.api.v1.dependencies import get_todo_service

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=TodoResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_todo(
    dto: TodoCreateDTO,
    service: TodoService = Depends(get_todo_service)
):
    return await service.create_todo(dto)


@router.get("/", response_model=list[TodoResponseDTO])
async def list_todos(service: TodoService = Depends(get_todo_service)):
    return await service.list_todos()


@router.get("/{todo_id}", response_model=TodoResponseDTO)
async def get_todo(
    todo_id: UUID,
    service: TodoService = Depends(get_todo_service)
):
    return await service.get_todo(todo_id)


@router.patch("/{todo_id}", response_model=TodoResponseDTO)
async def update_todo(
    todo_id: UUID,
    dto: TodoUpdateDTO,
    service: TodoService = Depends(get_todo_service)
):
    return await service.update_todo(todo_id, dto)


@router.patch("/{todo_id}/complete", response_model=TodoResponseDTO)
async def complete_todo(
    todo_id: UUID,
    service: TodoService = Depends(get_todo_service)
):
    return await service.complete_todo(todo_id)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: UUID,
    service: TodoService = Depends(get_todo_service)
):
    await service.delete_todo(todo_id)
