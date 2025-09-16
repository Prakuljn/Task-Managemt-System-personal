from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import os

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models
from app.dependencies import get_current_user, oauth2_scheme, get_db

router = APIRouter()

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

# ----------------- Logout -----------------
@router.post("/logout", summary="Logout user", tags=["Auth"])
def logout_user(
    current_user: models.User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Save token to revoked tokens
    revoked_token = models.RevokedToken(token=token)
    db.add(revoked_token)
    db.commit()
    return {"message": "Logged out successfully"}
