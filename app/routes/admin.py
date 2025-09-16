from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserResponse
from app.models import User, RoleEnum
from app.auth import hash_password
from app.dependencies import get_db, admin_required

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/create_manager", response_model=UserResponse)
def create_manager(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    if user.role != RoleEnum.manager:
        raise HTTPException(status_code=400, detail="Role must be manager")

    existing = db.query(User).filter((User.username==user.username) | (User.email==user.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    db_user = User(
        name=user.name,
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
        role=RoleEnum.manager,
        created_by_id=current_user.id  # ✅ set created_by_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/managers", response_model=list[UserResponse])
def list_managers(db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    managers = db.query(User).filter(User.role == RoleEnum.manager).all()
    return managers

@router.get("/manager/{manager_id}", response_model=UserResponse)
def get_manager(manager_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    manager = db.query(User).filter(User.id==manager_id, User.role==RoleEnum.manager).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    return manager
