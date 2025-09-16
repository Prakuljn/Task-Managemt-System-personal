from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, RoleEnum, RevokedToken
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    # Check if token is revoked
    if db.query(RevokedToken).filter(RevokedToken.token == token).first():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise credentials_exception
    return user

def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role != RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def manager_required(current_user: User = Depends(get_current_user)):
    if current_user.role != RoleEnum.manager:
        raise HTTPException(status_code=403, detail="Manager access required")
    return current_user

def employee_required(current_user: User = Depends(get_current_user)):
    if current_user.role != RoleEnum.employee:
        raise HTTPException(status_code=403, detail="Employee access required")
    return current_user
