from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import engine, Base
from app.models import User
from app.auth import verify_password, create_access_token, router as auth_router
from app.dependencies import get_db
from app.routes import admin, manager, employee

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Management System")

# Include your routes
app.include_router(admin.router)
app.include_router(manager.router)
app.include_router(employee.router)
app.include_router(auth_router)  # ✅ Add this to include login/logout

# JWT login endpoint (optional, already in auth.py as /login)
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/")
def read_root():
    return {"message": "Task Management API is running 🚀"}
