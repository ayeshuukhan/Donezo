from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskCreate(BaseModel):
    """POST body. Unknown fields reject hongi (extra=forbid) -> 422."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=120, examples=["Write unit tests"])
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TaskStatus = TaskStatus.todo
    priority: int = Field(default=3, ge=1, le=5, description="1 = lowest, 5 = highest")


class TaskUpdate(BaseModel):
    """PATCH body. Sab fields optional; sirf bheji gayi fields update hongi."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[TaskStatus] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)

    @field_validator("title", "status", "priority")
    @classmethod
    def not_null(cls, v):
        # Field explicitly null bheji ho to reject (description null allowed hai, clear karne ke liye)
        if v is None:
            raise ValueError("this field cannot be null")
        return v


class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: int
    created_at: datetime
    updated_at: datetime
