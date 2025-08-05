from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from backend.app.model.user_model import UserCreate
from backend.app.database.models import User

def create_user(db: Session, user: UserCreate):
    hashed_password = bcrypt.hash(user.password) 
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Fungsi untuk autentikasi user dengan email dan password
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not bcrypt.verify(password, user.hashed_password):
        return None
    return user
