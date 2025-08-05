# backend/app/routes/category_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database.database_conn import get_db
from backend.app.database import models
from backend.app.model.category_model import CategoryResponse # Pastikan ini mengacu ke Pydantic model CategoryResponse

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Category).filter(models.Category.is_default == True).all()
    return categories