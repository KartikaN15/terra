"""Reset demo user password. Run: python update_pwd.py"""
from app.database import SessionLocal
from app import models
from app.security import hash_password


def update_password():
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.email == "demo@terra.app").first()
        if not user:
            print("User demo@terra.app not found")
            return
        user.hashed_password = hash_password("password123")
        db.commit()
        print("Updated password for demo@terra.app -> password123")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_password()
