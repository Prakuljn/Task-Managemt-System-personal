from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, manager_required
from app.models import User, RoleEnum, Task, TaskHistory, TaskStatusEnum
from app.schemas import UserCreate, UserResponse, TaskCreate, TaskResponse
from app.auth import hash_password
try:
    from app.utils import send_email
except Exception:
    # utils.send_email may be commented out in development; define a noop fallback
    def send_email(to: str, subject: str, body: str):
        return None

router = APIRouter(prefix="/manager", tags=["Manager"])

# Create Employee
@router.post("/create_employee", response_model=UserResponse)
def create_employee(user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    if user.role != RoleEnum.employee:
        raise HTTPException(status_code=400, detail="Role must be employee")
    existing = db.query(User).filter((User.username==user.username)|(User.email==user.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    db_user = User(
        name=user.name,
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
        role=RoleEnum.employee,
        manager_id=current_user.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Assign Task
@router.post("/assign_task", response_model=TaskResponse)
def assign_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    employee = db.query(User).filter(User.id==task.assigned_to_id, User.manager_id==current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db_task = Task(
        title=task.title,
        description=task.description,
        assigned_to_id=employee.id,
        assigned_by_id=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    # Send email notification (noop if not configured)
    send_email(employee.email, "New Task Assigned", f"You have been assigned a task: {db_task.title}")
    return db_task

# Reassign Task
@router.put("/reassign_task/{task_id}", response_model=TaskResponse)
def reassign_task(task_id: int, new_employee_id: int, db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    task = db.query(Task).filter(Task.id==task_id, Task.assigned_by_id==current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    new_employee = db.query(User).filter(User.id==new_employee_id, User.manager_id==current_user.id).first()
    if not new_employee:
        raise HTTPException(status_code=404, detail="New employee not found")
    task.assigned_to_id = new_employee.id
    db.commit()
    db.refresh(task)
    send_email(new_employee.email, "Task Reassigned", f"You have been assigned a task: {task.title}")
    return task

# View Employees & their tasks
@router.get("/employees_tasks")
def view_employees_tasks(db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    employees = db.query(User).filter(User.manager_id==current_user.id).all()
    result = []
    for emp in employees:
        tasks = db.query(Task).filter(Task.assigned_to_id==emp.id).all()
        result.append({"employee": emp, "tasks": tasks})
    # FastAPI will use the response model inference; return raw data but ensure ORM objects are usable via orm_mode in schemas
    return result
