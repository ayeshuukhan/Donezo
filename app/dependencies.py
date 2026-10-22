from functools import lru_cache

from app.repository import InMemoryTaskRepository, TaskRepository


@lru_cache
def get_task_repository() -> TaskRepository:
    """Singleton repo. Tests mein app.dependency_overrides se replace hota hai."""
    return InMemoryTaskRepository()
