from fastapi import Depends, HTTPException, Request, status
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.app.database.database_conn import get_db
from backend.app.database.models import User
import os

# Load environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))  # Default: 1 hari

# Cek apakah SECRET_KEY tersedia
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY tidak ditemukan dalam environment. Harap set terlebih dahulu.")

# Fungsi untuk membuat access token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    # Encode JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Fungsi untuk mendapatkan user dari JWT token yang ada di cookie
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak ditemukan dalam cookie"
        )

    try:
        # Decode token dan ambil user_id dari payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Payload token tidak valid (sub kosong)"
            )

        # Pastikan user_id berupa integer
        user_id = int(user_id)

    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau korup"
        )

    # Ambil user dari database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User tidak ditemukan dalam database"
        )

    return user
