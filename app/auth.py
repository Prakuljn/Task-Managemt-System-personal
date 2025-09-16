from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import os

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import models
from app.dependencies import get_current_user, oauth2_scheme, get_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# bcrypt setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ----------------- Password utils -----------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# ----------------- JWT Token -----------------
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ----------------- Login -----------------
@router.post("/login")
def login(request: Request, db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})

    token = create_access_token({"sub": user.username})
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response

# ----------------- Logout -----------------
@router.post("/logout", summary="Logout user", tags=["Auth"])
def logout_user(
    current_user: models.User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Save token to revoked tokens only if token is present
    if token:
        revoked_token = models.RevokedToken(token=token)
        db.add(revoked_token)
        db.commit()
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")
    return response
