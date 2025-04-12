from typing import Sequence
from fastapi import HTTPException
from sqlalchemy import delete, update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.utils.redis import Redis
from freelance_marketplace.api.utils.sql_util import build_transaction_query
from freelance_marketplace.models.sql.request_model.OrderRequest import OrderRequest
from freelance_marketplace.models.sql.sql_tables import Order


class OrdersLogic:

    @staticmethod
    async def create(
            db : AsyncSession,
            order_data: OrderRequest,
            service_id: int
    ) -> bool:
        try:
            await Order.create(db=db, service_id=service_id, **order_data.model_dump())
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def delete(
            db: AsyncSession,
            order_id: int
    )-> bool:
        try:
            stmt = (
                update(Order)
                .where(Order.order_id == order_id)
                .values(deleted=True)
            )
            result = await db.execute(stmt)
            await db.commit()
            if result.rowcount > 0:
                return True
            else:
                raise HTTPException(status_code=404, detail="Notification not found or already deleted")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def update(
            db: AsyncSession,
            order_id: int,
            order_data: OrderRequest
    ) -> bool:
        try:
            stmt = (
                update(Order)
                .where(Order.order_id == order_id)
                .values(**order_data.model_dump())
                .execution_options(synchronize_session="fetch")
            )
            await db.execute(stmt)
            await db.commit()
            return True

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=f"{str(e)}")
    @staticmethod
    async def get(
            db: AsyncSession,
            order_id: int
    ) -> Order:
        cache_key = f"orders:{order_id}"
        redis_data = await Redis.get_redis_data(cache_key)
        if redis_data:
            return redis_data

        result = await db.execute(
            select(Order)
            .where(Order.order_id == order_id)
        )
        order = result.scalars().first()
        if not order:
            raise HTTPException(status_code=404, detail=f"Order not found")

        await Redis.set_redis_data(cache_key, order)
        return order

    @staticmethod
    async def get_all(
            db: AsyncSession,
            query_params: dict
    ) -> Sequence[Order]:

        transaction = await build_transaction_query(
            object=Order,
            query_params=query_params
        )

        result = await db.execute(transaction)
        orders = result.scalars().all()
        if not orders:
            raise HTTPException(status_code=404, detail=f"orders not found")
        return orders

