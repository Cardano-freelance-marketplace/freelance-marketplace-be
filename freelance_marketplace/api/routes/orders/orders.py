from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.routes.orders.ordersLogic import OrdersLogic
from freelance_marketplace.db.sql.database import get_sql_db
from freelance_marketplace.models.sql.request_model.OrderRequest import OrderRequest

router = APIRouter()

@router.get("/order", tags=["orders"])
async def get_order(
        db: AsyncSession = Depends(get_sql_db),
        order_id: int = Query(...)
):
    return await OrdersLogic.get(db=db, order_id=order_id)

@router.get("/orders", tags=["orders"])
async def get_all_orders(
        db: AsyncSession = Depends(get_sql_db),
        order_status_id: int | None = Query(None, description="Filter by order_status_id (CANCELED = 0, DRAFT = 1, PENDING = 2, ACCEPTED = 3, IN_PROGRESS = 4, COMPLETED = 5, DENIED_BY_FREELANCER = 6)"),
        service_id: int | None = Query(None, description="Filter by service_id"),
        client_id: int | None = Query(None, description="Filter by client_id"),
        deleted: bool | None = Query(False, description="Filter by deleted")
):
    query_params: dict = {
        'order_status_id': order_status_id,
        'service_id': service_id,
        "client_id": client_id,
        "deleted": deleted
    }
    return await OrdersLogic.get_all(db=db, query_params=query_params)

@router.patch("/order", tags=["orders"])
async def update_order(
        order_data: OrderRequest,
        order_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await OrdersLogic.update(db=db, order_id=order_id, order_data=order_data)

@router.post("/order", tags=["orders"])
async def create_order(
        order_data: OrderRequest,
        service_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await OrdersLogic.create(db=db, order_data=order_data, service_id=service_id)

@router.delete("/order", tags=["orders"])
async def delete_order(
        order_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await OrdersLogic.delete(db=db, order_id=order_id)