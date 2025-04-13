from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.routes.transactions.transactionsLogic import TransactionsLogic
from freelance_marketplace.db.sql.database import get_sql_db
from freelance_marketplace.models.sql.request_model.TransactionRequest import TransactionRequest

router = APIRouter()

@router.get("/transaction", tags=["transactions"])
async def get_transaction(
        db: AsyncSession = Depends(get_sql_db),
        transaction_id: int | None = Query(None),
        milestone_id: int | None = Query(None)
):
    query_params = {
        "transaction_id": transaction_id,
        "milestone_id": milestone_id
    }
    return await TransactionsLogic.get(db=db, query_params=query_params)

@router.get("/transactions", tags=["transactions"])
async def get_all_transactions(
        db: AsyncSession = Depends(get_sql_db),
        amount: float | None = Query(None, description="Filter by amount"),
        token_name: int | None = Query(None, description="Filter by token_name"),
        deleted: bool | None = Query(False, description="Filter by deleted"),
        receiver_address: str | None = Query(False, description="Filter by receiver_address"),
        client_id: int | None = Query(False, description="Filter by client_id"),
        freelancer_id: int | None = Query(False, description="Filter by freelancer_id"),
):
    query_params: dict = {
        'amount': amount,
        'receiver_address': receiver_address,
        'freelancer_id': freelancer_id,
        "client_id": client_id,
        "deleted": deleted
    }
    return await TransactionsLogic.get_all(db=db, query_params=query_params)

@router.patch("/transaction", tags=["transactions"])
async def update_transaction(
        transaction_data: TransactionRequest,
        transaction_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await TransactionsLogic.update(db=db, transaction_id=transaction_id, transaction_data=transaction_data)

@router.post("/transaction", tags=["transactions"])
async def create_transaction(
        transaction_data: TransactionRequest,
        milestone_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await TransactionsLogic.create(db=db, transaction_data=transaction_data, milestone_id=milestone_id)

@router.delete("/transaction", tags=["transactions"])
async def delete_transaction(
        transaction_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await TransactionsLogic.delete(db=db, transaction_id=transaction_id)