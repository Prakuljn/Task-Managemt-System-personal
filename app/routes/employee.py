from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.dependencies import get_db, employee_required
from app.models import Task, TaskHistory, User, TaskStatusEnum
from app.schemas import TaskResponse, TaskUpdate

router = APIRouter(prefix="/employee", tags=["Employee"])
templates = Jinja2Templates(directory="templates")

# View tasks
@router.get("/tasks", response_class=HTMLResponse)
def view_tasks(request: Request, db: Session = Depends(get_db), current_user: User = Depends(employee_required)):
    tasks = db.query(Task).filter(Task.assigned_to_id == current_user.id).all()
    return templates.TemplateResponse("employee/tasks.html", {"request": request, "tasks": tasks, "user": current_user})

# Update task form
@router.get("/update_task/{task_id}", response_class=HTMLResponse)
def update_task_form(request: Request, task_id: int, db: Session = Depends(get_db), current_user: User = Depends(employee_required)):
    task = db.query(Task).filter(Task.id == task_id, Task.assigned_to_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return templates.TemplateResponse("employee/update_task.html", {"request": request, "task": task, "user": current_user, "statuses": TaskStatusEnum})

# Update task logic
@router.post("/update_task/{task_id}")
def update_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_required),
    status: TaskStatusEnum = Form(...),
    hours_spent: int = Form(...)
):
    task = db.query(Task).filter(Task.id == task_id, Task.assigned_to_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    history = TaskHistory(
        task_id=task.id,
        updated_by_id=current_user.id,
        status_before=task.status,
        status_after=status,
        hours_spent=hours_spent
    )

    task.status = status
    task.hours_spent = hours_spent

    db.add(history)
    db.commit()
    db.refresh(task)
    return RedirectResponse(url="/employee/tasks", status_code=303)

# View task history
@router.get("/task_history/{task_id}", response_class=HTMLResponse)
def view_task_history(request: Request, task_id: int, db: Session = Depends(get_db), current_user: User = Depends(employee_required)):
    task = db.query(Task).filter(Task.id == task_id, Task.assigned_to_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    history = db.query(TaskHistory).filter(TaskHistory.task_id == task_id).all()
    return templates.TemplateResponse("employee/task_history.html", {"request": request, "history": history, "task": task, "user": current_user})
