from passlib.context import CryptContext
from app.database import SessionLocal
from app import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify():
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.email == "demo@terra.app").first()
    if not user:
        print("User not found")
        return
    
    password = "password123"
    is_valid = pwd_context.verify(password, user.hashed_password)
    print(f"Password: {password}")
    print(f"Stored Hash: {user.hashed_password}")
    print(f"Is Valid: {is_valid}")

if __name__ == "__main__":
    verify()
