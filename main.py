from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import engine, Base
from app.models import User, RoleEnum
from app.dependencies import get_db, get_current_user
from app.routes import admin, manager, employee
from app.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Management System")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

# Include your routes
app.include_router(admin.router)
app.include_router(manager.router)
app.include_router(employee.router)
app.include_router(auth_router)

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard")
def dashboard(current_user: User = Depends(get_current_user)):
    if current_user.role == RoleEnum.admin:
        return RedirectResponse(url="/admin/dashboard")
    elif current_user.role == RoleEnum.manager:
        return RedirectResponse(url="/manager/dashboard")
    elif current_user.role == RoleEnum.employee:
        return RedirectResponse(url="/employee/tasks")
    else:
        raise HTTPException(status_code=403, detail="Forbidden")
