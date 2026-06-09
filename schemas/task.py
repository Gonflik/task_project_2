from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional
from models.task import TaskStatus

class TaskCreate(BaseModel):
    title: str
    description: str
    email: EmailStr
    due_date: datetime

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    status: TaskStatus | None = None

class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    email: EmailStr
    status: TaskStatus
    due_date: datetime
    created_at: datetime
    updated_at: datetime