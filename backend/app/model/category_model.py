from pydantic import BaseModel
from typing import Optional

class CategoryBase(BaseModel):
    name: str
    type: str # 'income', 'expense', 'both'
    is_default: bool = False

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    user_id: Optional[int] = None 
    
    class Config:
        orm_mode = True