from typing import Sequence
from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.utils.redis import Redis
from freelance_marketplace.api.utils.sql_util import build_transaction_query, soft_delete
from freelance_marketplace.models.sql.request_model.TransactionRequest import TransactionRequest
from freelance_marketplace.models.sql.sql_tables import Transaction


class TransactionsLogic:

    @staticmethod
    async def create(
            db : AsyncSession,
            transaction_data: TransactionRequest,
            milestone_id: int
    ) -> bool:
        try:
            await Transaction.create(db=db, milestone_id=milestone_id, **transaction_data.model_dump())
            await Redis.invalidate_cache("transactions")
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def delete(
            db: AsyncSession,
            transaction_id: int
    )-> bool:
        try:
            result = await soft_delete(db=db, object=Transaction, attribute="transaction_id", object_id=transaction_id)
            if result.rowcount > 0:
                await Redis.invalidate_cache("transactions")
                return True
            else:
                raise HTTPException(status_code=404, detail="Transaction not found or already deleted")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def update(
            db: AsyncSession,
            transaction_id: int,
            transaction_data: TransactionRequest
    ) -> bool:
        try:
            stmt = (
                update(Transaction)
                .where(Transaction.transaction_id == transaction_id)
                .values(**transaction_data.model_dump())
                .execution_options(synchronize_session="fetch")
            )
            await db.execute(stmt)
            await db.commit()
            await Redis.invalidate_cache("transactions")
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
            query_params: dict
    ):
        redis_data, cache_key = await Redis.get_redis_data(prefix=f"transactions")
        if redis_data:
            return redis_data

        transaction = await build_transaction_query(
            object=Transaction,
            query_params=query_params
        )

        result = await db.execute(transaction)
        transaction = result.scalars().all()
        if not transaction:
            raise HTTPException(status_code=404, detail=f"Transaction not found")

        await Redis.set_redis_data(cache_key, transaction)
        return transaction

    @staticmethod
    async def get_all(
            db: AsyncSession,
            query_params: dict
    ) -> Sequence[Transaction]:
        redis_data, cache_key = await Redis.get_redis_data(prefix="transactions", query_params=query_params)
        if redis_data:
            return redis_data

        transaction = await build_transaction_query(
            object=Transaction,
            query_params=query_params
        )

        result = await db.execute(transaction)
        transactions = result.scalars().all()
        if not transactions:
            raise HTTPException(status_code=404, detail=f"Transactions not found")

        await Redis.set_redis_data(cache_key, data=transactions)
        return transactions

