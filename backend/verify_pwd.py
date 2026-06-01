"""Verify demo user password. Run: python verify_pwd.py"""
from app.database import SessionLocal
from app import models
from app.security import verify_password


def verify():
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.email == "demo@terra.app").first()
    if not user:
        print("User not found")
        return
    password = "password123"
    is_valid = verify_password(password, user.hashed_password)
    print(f"Password: {password}")
    print(f"Is Valid: {is_valid}")


if __name__ == "__main__":
    verify()
