from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.dependencies import get_task_repository
from app.models import Task, TaskCreate, TaskStatus, TaskUpdate
from app.repository import TaskRepository

router = APIRouter(prefix="/tasks", tags=["tasks"])

Repo = Annotated[TaskRepository, Depends(get_task_repository)]


def _not_found(task_id: int) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found")


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED, summary="Create a task")
def create_task(payload: TaskCreate, repo: Repo):
    return repo.create(payload)


@router.get("", response_model=list[Task], summary="List tasks")
def list_tasks(
    repo: Repo,
    status_filter: Optional[TaskStatus] = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    return repo.list(status_filter, limit, offset)


@router.get("/{task_id}", response_model=Task, summary="Get one task")
def get_task(task_id: int, repo: Repo):
    task = repo.get(task_id)
    if task is None:
        raise _not_found(task_id)
    return task


@router.patch("/{task_id}", response_model=Task, summary="Partially update a task")
def update_task(task_id: int, payload: TaskUpdate, repo: Repo):
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No fields provided to update")
    task = repo.update(task_id, changes)
    if task is None:
        raise _not_found(task_id)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task")
def delete_task(task_id: int, repo: Repo):
    if not repo.delete(task_id):
        raise _not_found(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
