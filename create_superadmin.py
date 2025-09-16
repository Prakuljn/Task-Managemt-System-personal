from app.database import Base, engine, SessionLocal
from app.models import User, RoleEnum
from app.auth import hash_password
from sqlalchemy.exc import IntegrityError

# 1️⃣ Create all tables in DB
print("📦 Creating tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully.")

# 2️⃣ Insert default super admin
db = SessionLocal()

try:
    # Check if superadmin already exists
    existing = db.query(User).filter(User.username=="superadmin").first()
    if existing:
        print(f"ℹ️ Super Admin already exists: {existing.username} ({existing.email})")
    else:
        super_admin = User(
            name="Super Admin",
            username="superadmin",
            email="superadmin@example.com",
            password_hash=hash_password("admin123"),
            role=RoleEnum.admin
        )
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        print(f"✅ Super Admin created: {super_admin.username} - {super_admin.email}")

    total_users = db.query(User).count()
    print(f"👥 Total users in DB now: {total_users}")

except IntegrityError as e:
    db.rollback()
    print(f"❌ Integrity error: {e}")
except Exception as e:
    db.rollback()
    print(f"❌ Failed to insert super admin: {e}")
finally:
    db.close()
