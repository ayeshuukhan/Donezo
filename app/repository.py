from datetime import datetime, timezone
from threading import Lock
from typing import Optional, Protocol

from app.models import Task, TaskCreate, TaskStatus


class TaskRepository(Protocol):
    """Interface. Kal ko PostgreSQL repo bana do, routes change nahi honge."""

    def list(self, status: Optional[TaskStatus], limit: int, offset: int) -> list[Task]: ...
    def get(self, task_id: int) -> Optional[Task]: ...
    def create(self, data: TaskCreate) -> Task: ...
    def update(self, task_id: int, changes: dict) -> Optional[Task]: ...
    def delete(self, task_id: int) -> bool: ...


class InMemoryTaskRepository:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1
        self._lock = Lock()

    def list(self, status: Optional[TaskStatus] = None, limit: int = 50, offset: int = 0) -> list[Task]:
        tasks = sorted(self._tasks.values(), key=lambda t: t.id)
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        return tasks[offset : offset + limit]

    def get(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)

    def create(self, data: TaskCreate) -> Task:
        now = datetime.now(timezone.utc)
        with self._lock:
            task = Task(id=self._next_id, created_at=now, updated_at=now, **data.model_dump())
            self._tasks[task.id] = task
            self._next_id += 1
        return task

    def update(self, task_id: int, changes: dict) -> Optional[Task]:
        with self._lock:
            existing = self._tasks.get(task_id)
            if existing is None:
                return None
            updated = existing.model_copy(
                update={**changes, "updated_at": datetime.now(timezone.utc)}
            )
            self._tasks[task_id] = updated
            return updated

    def delete(self, task_id: int) -> bool:
        with self._lock:
            return self._tasks.pop(task_id, None) is not None
