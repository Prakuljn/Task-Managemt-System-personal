from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, employee_required
from app.models import Task, TaskHistory, TaskStatusEnum, User
from app.schemas import TaskResponse, TaskUpdate
#from app.utils import send_email

router = APIRouter(prefix="/employee", tags=["Employee"])

# View tasks
@router.get("/tasks", response_model=list[TaskResponse])
def view_tasks(db: Session = Depends(get_db), current_user: User = Depends(employee_required)):
    tasks = db.query(Task).filter(Task.assigned_to_id==current_user.id).all()
    return tasks

# Update task status and hours
@router.put("/update_task/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, update: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(employee_required)):
    task = db.query(Task).filter(Task.id==task_id, Task.assigned_to_id==current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    history = TaskHistory(
        task_id=task.id,
        updated_by_id=current_user.id,
        status_before=task.status,
        status_after=update.status,
        hours_spent=update.hours_spent or task.hours_spent
    )
    task.status = update.status
    if update.hours_spent is not None:
        task.hours_spent = update.hours_spent
    db.add(history)
    db.commit()
    db.refresh(task)
    # Send email if completed
    # if task.status == TaskStatusEnum.completed:
    #     manager = db.query(User).filter(User.id==task.assigned_by_id).first()
    #     if manager:
    #         send_email(manager.email, "Task Completed", f"Employee {current_user.name} completed task: {task.title}")
    return task
