from fastapi import APIRouter, Query, Depends
from model.transaction import TransactionModel
from services.transaction import (
    add_transaction_service,
    update_transaction_service,
    delete_transaction_service,
    list_transactions_service
)
from services.auth import get_current_user

router = APIRouter(tags=["Transactions"])

@router.post("/")
async def add_transaction(txn: TransactionModel, current_user: dict = Depends(get_current_user)):
    return await add_transaction_service(txn, current_user)

@router.put("/{txn_id}")
async def update_transaction(txn_id: str, txn: TransactionModel, current_user: dict = Depends(get_current_user)):
    return await update_transaction_service(txn_id, txn, current_user)

@router.delete("/{txn_id}")
async def delete_transaction(txn_id: str, current_user: dict = Depends(get_current_user)):
    return await delete_transaction_service(txn_id, current_user)

@router.get("/")
async def list_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: str = "",
    status: str = "",
    sort_by: str = "transaction_date",
    current_user: dict = Depends(get_current_user)
):
    return await list_transactions_service(page, limit, search, status, sort_by, current_user)
