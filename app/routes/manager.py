
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import Integer, String
from app.dependencies import get_db, manager_required
from app.models import User, RoleEnum, Task
from app.schemas import UserCreate, TaskCreate
from app.auth import hash_password

router = APIRouter(prefix="/manager", tags=["Manager"])
templates = Jinja2Templates(directory="templates")

# Manager dashboard
@router.get("/dashboard", response_class=HTMLResponse)
def manager_dashboard(request: Request, current_user: User = Depends(manager_required)):
    from sqlalchemy import func
    db = next(get_db())
    # Employees created by this manager
    employees_count = db.query(User).filter(User.created_by_id == current_user.id, User.role == RoleEnum.employee).count()
    # Tasks assigned by this manager
    assigned_tasks = db.query(Task).filter(Task.assigned_by_id == current_user.id).count()
    # Tasks awaiting review (status: in_progress)
    awaiting_review = db.query(Task).filter(Task.assigned_by_id == current_user.id, Task.status == 'in_progress').count()
    # Tasks completed
    completed = db.query(Task).filter(Task.assigned_by_id == current_user.id, Task.status == 'completed').count()
    # Recent tasks (last 5)
    recent_tasks_query = db.query(Task).filter(Task.assigned_by_id == current_user.id).order_by(Task.created_at.desc()).limit(5).all()
    recent_tasks = []
    for t in recent_tasks_query:
        emp = db.query(User).filter(User.id == t.assigned_to_id).first()
        recent_tasks.append({
            'title': t.title,
            'employee_name': emp.name if emp else 'N/A',
            'due_date': t.updated_at.strftime('%Y-%m-%d') if hasattr(t, 'updated_at') and t.updated_at else '',
            'status': t.status.value if hasattr(t.status, 'value') else t.status
        })
    # Dummy chart values (could be replaced with real data)
    # For PostgreSQL: use CURRENT_DATE - INTERVAL 'i days'
    # Calculate chart values using Python date arithmetic for compatibility
    from datetime import date, timedelta
    chart_values = ','.join([
        str(
            db.query(Task)
            .filter(
                Task.assigned_by_id == current_user.id,
                func.date(Task.created_at) == (date.today() - timedelta(days=i))
            )
            .count()
        )
        for i in range(7)
    ])
    return templates.TemplateResponse(
        "manager/dashboard.html",
        {
            "request": request,
            "user": current_user,
            "employees_count": employees_count,
            "assigned_tasks": assigned_tasks,
            "awaiting_review": awaiting_review,
            "completed": completed,
            "chart_values": chart_values,
            "recent_tasks": recent_tasks
        }
    )

# Create Employee form
@router.get("/create_employee", response_class=HTMLResponse)
def create_employee_form(request: Request, current_user: User = Depends(manager_required)):
    return templates.TemplateResponse("manager/create_employee.html", {"request": request, "user": current_user})

# Create Employee logic
@router.post("/create_employee")
def create_employee(
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_required),
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    existing = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    db_user = User(
        name=name,
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=RoleEnum.employee,
        created_by_id=current_user.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return RedirectResponse(url="/manager/dashboard", status_code=303)

# Assign Task form
@router.get("/assign_task", response_class=HTMLResponse)
def assign_task_form(request: Request, db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    employees = db.query(User).filter(User.created_by_id == current_user.id, User.role == RoleEnum.employee).all()
    return templates.TemplateResponse("manager/assign_task.html", {"request": request, "employees": employees, "user": current_user})

# Assign Task logic
@router.post("/assign_task")
def assign_task(
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_required),
    title: str = Form(...),
    description: str = Form(...),
    assigned_to_id: int = Form(...)
):
    employee = db.query(User).filter(User.id == assigned_to_id, User.created_by_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db_task = Task(
        title=title,
        description=description,
        assigned_to_id=employee.id,
        assigned_by_id=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return RedirectResponse(url="/manager/dashboard", status_code=303)

# Reassign Task form
@router.get("/reassign_task/{task_id}", response_class=HTMLResponse)
def reassign_task_form(request: Request, task_id: int, db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    task = db.query(Task).filter(Task.id == task_id, Task.assigned_by_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    employees = db.query(User).filter(User.created_by_id == current_user.id, User.role == RoleEnum.employee).all()
    return templates.TemplateResponse("manager/reassign_task.html", {"request": request, "task": task, "employees": employees, "user": current_user})

# Reassign Task logic
@router.post("/reassign_task/{task_id}")
def reassign_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_required),
    new_employee_id: int = Form(...)
):
    task = db.query(Task).filter(Task.id == task_id, Task.assigned_by_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    new_employee = db.query(User).filter(User.id == new_employee_id, User.created_by_id == current_user.id).first()
    if not new_employee:
        raise HTTPException(status_code=404, detail="New employee not found")
    task.assigned_to_id = new_employee_id
    db.commit()
    db.refresh(task)
    return RedirectResponse(url="/manager/dashboard", status_code=303)

# View Employees & their tasks
@router.get("/employees_tasks", response_class=HTMLResponse)
def view_employees_tasks(request: Request, db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    employees = db.query(User).filter(User.created_by_id == current_user.id).all()
    result = []
    for emp in employees:
        tasks = db.query(Task).filter(Task.assigned_to_id == emp.id).all()
        result.append({"employee": emp, "tasks": tasks})
    return templates.TemplateResponse("manager/employees_tasks.html", {"request": request, "result": result, "user": current_user})
