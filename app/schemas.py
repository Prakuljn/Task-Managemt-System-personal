from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models import RoleEnum, TaskStatusEnum

# ---------------- User Schemas ----------------
class CreatorInfo(BaseModel):
    id: int
    uuid: Optional[str] = None
    name: str
    username: str
    email: EmailStr

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str
    role: RoleEnum

class UserResponse(BaseModel):
    id: int
    uuid: Optional[str] = None
    name: str
    username: str
    email: EmailStr
    role: RoleEnum
    created_by: Optional[CreatorInfo] = None  # ✅ nested creator
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# ---------------- Task Schemas ----------------
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to_id: int
    assigned_by_id: Optional[int] = None

class TaskUpdate(BaseModel):
    status: TaskStatusEnum
    hours_spent: Optional[float] = 0.0

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    assigned_to_id: int
    assigned_by_id: int
    status: TaskStatusEnum
    hours_spent: float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# ---------------- Task History ----------------
class TaskHistoryResponse(BaseModel):
    id: int
    task_id: int
    updated_by_id: int
    status_before: TaskStatusEnum
    status_after: TaskStatusEnum
    hours_spent: float
    timestamp: datetime

    class Config:
        orm_mode = True
