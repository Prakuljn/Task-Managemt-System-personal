from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum, uuid

class RoleEnum(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    employee = "employee"

class TaskStatusEnum(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, default=lambda: str(uuid.uuid4()), unique=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to track who created this user
    created_by = relationship(
        "User",
        remote_side=[id],
        foreign_keys=[created_by_id],
        backref="created_users"
    )

    tasks_assigned = relationship(
        "Task",
        foreign_keys="Task.assigned_by_id",
        backref="assigned_by"
    )
    tasks_received = relationship(
        "Task",
        foreign_keys="Task.assigned_to_id",
        backref="assigned_to"
    )

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    assigned_by_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.pending)
    hours_spent = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    history = relationship(
        "TaskHistory",
        backref="task",
        cascade="all, delete"
    )

class TaskHistory(Base):
    __tablename__ = "task_history"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    updated_by_id = Column(Integer, ForeignKey("users.id"))
    status_before = Column(Enum(TaskStatusEnum))
    status_after = Column(Enum(TaskStatusEnum))
    hours_spent = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)

    updated_by = relationship("User")
