from typing import Sequence
from fastapi import HTTPException
from sqlalchemy import update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.services.redis import Redis
from freelance_marketplace.api.utils.sql_util import build_transaction_query, soft_delete
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
            await Redis.invalidate_cache("orders")
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def delete(
            db: AsyncSession,
            order_id: int
    )-> bool:
        try:
            result = await soft_delete(db=db, object=Order, attribute="order_id", object_id=order_id)
            if result.rowcount > 0:
                await Redis.invalidate_cache("orders")
                return True
            else:
                raise HTTPException(status_code=404, detail="Order not found or already deleted")
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
            await Redis.invalidate_cache("orders")
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
        redis_data, cache_key = await Redis.get_redis_data(match=f"orders:{order_id}")
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
        redis_data, cache_key = await Redis.get_redis_data(prefix="orders", query_params=query_params)
        if redis_data:
            return redis_data

        transaction = await build_transaction_query(
            object=Order,
            query_params=query_params
        )

        result = await db.execute(transaction)
        orders = result.scalars().all()
        if not orders:
            raise HTTPException(status_code=404, detail=f"orders not found")

        await Redis.set_redis_data(cache_key, data=orders)
        return orders

