from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Transaction, User
from app.schemas import TransactionCreate, TransactionResponse, TransactionUpdate

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def get_owned_transaction(transaction_id: int, user_id: int, db: Session) -> Transaction:
    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.owner_id == user_id)
        .first()
    )
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transaction = Transaction(**transaction_data.model_dump(), owner_id=current_user.id)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("", response_model=list[TransactionResponse])
def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Transaction)
        .filter(Transaction.owner_id == current_user.id)
        .order_by(Transaction.id)
        .all()
    )


@router.get("/filter", response_model=list[TransactionResponse])
def filter_transactions(
    type: Literal["income", "expense"] | None = Query(default=None),
    category: str | None = Query(default=None),
    minimum_amount: float | None = Query(default=None, gt=0),
    maximum_amount: float | None = Query(default=None, gt=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (
        minimum_amount is not None
        and maximum_amount is not None
        and minimum_amount > maximum_amount
    ):
        raise HTTPException(
            status_code=400,
            detail="minimum_amount cannot be greater than maximum_amount",
        )

    query = db.query(Transaction).filter(Transaction.owner_id == current_user.id)

    if type is not None:
        query = query.filter(Transaction.type == type)
    if category is not None:
        query = query.filter(Transaction.category == category)
    if minimum_amount is not None:
        query = query.filter(Transaction.amount >= minimum_amount)
    if maximum_amount is not None:
        query = query.filter(Transaction.amount <= maximum_amount)

    return query.order_by(Transaction.id).all()


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_owned_transaction(transaction_id, current_user.id, db)


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transaction = get_owned_transaction(transaction_id, current_user.id, db)

    for field, value in transaction_data.model_dump(exclude_unset=True).items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transaction = get_owned_transaction(transaction_id, current_user.id, db)
    db.delete(transaction)
    db.commit()
    return {"message": "Transaction deleted successfully"}
