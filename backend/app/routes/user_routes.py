from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.app.database.database_conn import get_db
from backend.app.model.user_model import UserLogin, UserResponse, UserCreate,EmailRequest, ResetPasswordRequest
from backend.app.service.user_services import create_user
from backend.app.auth.auth import create_access_token, get_current_user
from passlib.context import CryptContext
from backend.app.database.models import User

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.post("/login")
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_login.email).first()
    if not user or not pwd_context.verify(user_login.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email atau password salah")  # ✅ pakai 401
    
    access_token = create_access_token(data={"sub": str(user.id)})

    response = JSONResponse(content={
        "message": "Login berhasil",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    })
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        path="/",
        secure=True,  # ⚠️ Ubah jadi True untuk production (HTTPS)
        samesite="lax",
        max_age=60 * 60 * 24  # ✅ 1 hari dalam detik
    )
    return response

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
def logout(response: Response):
    res = JSONResponse(content={"message": "Logout berhasil"})
    res.delete_cookie(key="access_token", path="/")
    return res
@router.post("/lupa-password")
def lupa_password(data: EmailRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email tidak ditemukan")
    return {"message": "Email ditemukan, silakan masukkan password baru."}

@router.post("/reset-password-langsung")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    hashed_password = pwd_context.hash(data.new_password)
    user.hashed_password = hashed_password
    db.commit()
    
    return {"message": "Password berhasil diubah"}