from sqlalchemy.orm import Session
from backend.app.database import models 
from backend.app.model.transaction_model import TransactionCreate 
from sqlalchemy import and_ 

def create_transaction(db: Session, transaction: TransactionCreate, user_id: int):
    db_transaction = models.Transaction(
        user_id=user_id,
        transaction_type=transaction.transaction_type, 
        amount=transaction.amount,
        transaction_date=transaction.transaction_date, 
        description=transaction.description,
        category_id=transaction.category_id 
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(
        models.Transaction,
        models.Category.name.label("category_name") 
    ).join(models.Category, models.Transaction.category_id == models.Category.id)\
     .filter(models.Transaction.user_id == user_id)\
     .offset(skip).limit(limit).all()

def get_transaction_by_id(db: Session, transaction_id: int, user_id: int):
    return db.query(
        models.Transaction,
        models.Category.name.label("category_name")
    ).join(models.Category, models.Transaction.category_id == models.Category.id)\
     .filter(and_(models.Transaction.id == transaction_id, models.Transaction.user_id == user_id)).first()

def delete_transaction(db: Session, transaction_id: int, user_id: int) -> bool:
    transaction = db.query(models.Transaction).filter(
        and_(models.Transaction.id == transaction_id, models.Transaction.user_id == user_id) 
    ).first()
    
    if not transaction:
        return False

    db.delete(transaction)
    db.commit()
    return True

def update_transaction(db: Session, transaction_id: int, transaction: TransactionCreate, user_id: int):
    db_transaction = db.query(models.Transaction).filter(
        and_(models.Transaction.id == transaction_id, models.Transaction.user_id == user_id)
    ).first()

    if not db_transaction:
        return None

    db_transaction.transaction_type = transaction.transaction_type 
    db_transaction.amount = transaction.amount
    db_transaction.transaction_date = transaction.transaction_date 
    db_transaction.description = transaction.description
    db_transaction.category_id = transaction.category_id 

    db.commit()
    db.refresh(db_transaction)
    return db_transaction