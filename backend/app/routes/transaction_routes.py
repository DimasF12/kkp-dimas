from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database.database_conn import get_db
from backend.app.database import models
from backend.app.model.transaction_model import TransactionCreate, TransactionResponse
from backend.app.auth.auth import get_current_user
from backend.app.service.transaction_services import (
    create_transaction,
    get_transactions,
    get_transaction_by_id,
    delete_transaction,
    update_transaction,
)

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

# Util: Konversi model ORM + category_name → response
def build_transaction_response(trans_obj: models.Transaction, category_name: str) -> TransactionResponse:
    return TransactionResponse(
        id=trans_obj.id,
        user_id=trans_obj.user_id,
        transaction_type=trans_obj.transaction_type,
        amount=float(trans_obj.amount),
        transaction_date=trans_obj.transaction_date,
        description=trans_obj.description,
        category_id=trans_obj.category_id,
        category_name=category_name
    )


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def add_transaction_route(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_transaction = create_transaction(db=db, transaction=transaction, user_id=current_user.id)

    category_name = db.query(models.Category.name).filter(models.Category.id == db_transaction.category_id).scalar()
    return build_transaction_response(db_transaction, category_name)


@router.get("/", response_model=List[TransactionResponse])
def get_transactions_route(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transactions_with_category = get_transactions(db=db, user_id=current_user.id)

    return [build_transaction_response(trx, cat_name) for trx, cat_name in transactions_with_category]


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction_by_id_route(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = get_transaction_by_id(db=db, transaction_id=transaction_id, user_id=current_user.id)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    trx, category_name = result
    return build_transaction_response(trx, category_name)


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction_route(
    transaction_id: int,
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    updated_trx = update_transaction(db=db, transaction_id=transaction_id, transaction=transaction, user_id=current_user.id)

    if not updated_trx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found or not owned by user")

    category_name = db.query(models.Category.name).filter(models.Category.id == updated_trx.category_id).scalar()
    return build_transaction_response(updated_trx, category_name)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction_route(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transaction = db.query(models.Transaction).filter_by(id=transaction_id, user_id=current_user.id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")

    db.delete(transaction)
    db.commit()
    return

