from pydantic import BaseModel
from datetime import date
from typing import Optional

class TransactionBase(BaseModel):
    transaction_type: bool  # True = Income, False = Expense
    amount: float
    transaction_date: date
    description: Optional[str] = None
    category_id: Optional[int] = None  # Boleh kosong saat pembuatan

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    category_name: Optional[str] = None

    class Config:
        orm_mode = True
