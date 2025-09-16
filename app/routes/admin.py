# Remove Manager

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.models import User, RoleEnum
from app.auth import hash_password
from app.dependencies import get_db, admin_required
from sqlalchemy import func
router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    total_managers = db.query(User).filter(User.role == RoleEnum.manager).count()
    total_employees = db.query(User).filter(User.role == RoleEnum.employee).count()
    from app.models import Task, TaskStatusEnum
    active_tasks = db.query(Task).filter(Task.status != TaskStatusEnum.completed).count()
    completed_tasks = db.query(Task).filter(Task.status == TaskStatusEnum.completed).count()
    managers = db.query(User).filter(User.role == RoleEnum.manager).order_by(User.created_at.desc()).limit(5).all()

    for m in managers:
        m.employees_count = db.query(User).filter(User.created_by_id == m.id, User.role == RoleEnum.employee).count()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": current_user,
            "total_managers": total_managers,
            "total_employees": total_employees,
            "active_tasks": active_tasks,
            "completed_tasks": completed_tasks,
            "managers": managers,
        },
    )

@router.get("/create_manager", response_class=HTMLResponse)
def create_manager_form(request: Request, current_user: User = Depends(admin_required)):
    return templates.TemplateResponse("admin/create_manager.html", {"request": request, "user": current_user})
@router.post("/create_manager")
def create_manager(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
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
        role=RoleEnum.manager,
        created_by_id=current_user.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return RedirectResponse(url="/admin/dashboard", status_code=303)

@router.get("/managers", response_class=HTMLResponse)
def list_managers(request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    managers = db.query(User).filter(User.role == RoleEnum.manager).all()
    return templates.TemplateResponse("admin/managers.html", {"request": request, "managers": managers, "user": current_user})


@router.get("/manager/{manager_id}", response_class=HTMLResponse)
def get_manager(request: Request, manager_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    manager = db.query(User).filter(User.id == manager_id, User.role == RoleEnum.manager).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    return templates.TemplateResponse("admin/manager_detail.html", {"request": request, "manager": manager, "user": current_user})
@router.post("/manager/{manager_id}/remove")
def remove_manager(manager_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    manager = db.query(User).filter(User.id == manager_id, User.role == RoleEnum.manager).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    db.delete(manager)
    db.commit()
    return RedirectResponse(url="/admin/managers", status_code=303)