from passlib.context import CryptContext
from app.database import SessionLocal
from app import models
import sys

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def update_password():
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.email == "demo@terra.app").first()
        if not user:
            print("User not found")
            return
        
        # Set pre-generated hash for 'password123'
        print(f"Setting hash for {user.email}...")
        user.hashed_password = "$2b$12$z6nntHXruyv1OH2cBcUK7eW9NJKQ92OeOiXmjydSjQBT0WhX7OxM."
        print("Committing...")
        db.commit()
        print("Updated password hash successfully")
    except Exception as e:
        db.rollback()
        print(f"Error during update: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    update_password()
