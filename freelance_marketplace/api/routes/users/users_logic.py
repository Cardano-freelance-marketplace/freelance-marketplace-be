from typing import Sequence
from fastapi import HTTPException
from sqlalchemy import update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.services.redis import Redis
from freelance_marketplace.api.utils.sql_util import soft_delete, build_transaction_query
from freelance_marketplace.models.sql.request_model.UserRequest import UserRequest
from freelance_marketplace.models.sql.sql_tables import User


class UsersLogic:
    @staticmethod
    async def create(
            db : AsyncSession,
            user: UserRequest
    ) -> bool:
        try:
            await User.create(db=db, **user.model_dump())
            await Redis.invalidate_cache("users")
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def delete(
            db: AsyncSession,
            user_id: int
    )-> bool:
        result = await soft_delete(db=db, object=User, attribute="user_id", object_id=user_id)
        if result.rowcount > 0:
            await Redis.invalidate_cache("users")
            return True
        else:
            raise HTTPException(status_code=404, detail="User not found or already deleted")


    @staticmethod
    async def update(
            db: AsyncSession,
            user_id: int,
            user: UserRequest
    ) -> bool:
        try:
            stmt = (
                update(User)
                .where(User.user_id == user_id)
                .values(**user.model_dump())
                .execution_options(synchronize_session="fetch")
            )
            await db.execute(stmt)
            await db.commit()
            await Redis.invalidate_cache("users")
            return True
        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to update user")

    @staticmethod
    async def get_all(
            db: AsyncSession,
            query_params: dict
    ) -> Sequence[User]:
        redis_data, cache_key = await Redis.get_redis_data(prefix="users", query_params=query_params)
        if redis_data:
            return redis_data

        transaction = await build_transaction_query(
            object=User,
            query_params=query_params
        )

        result = await db.execute(transaction)
        users = result.scalars().all()

        if not users:
            raise HTTPException(status_code=404, detail="Users not found")
        await Redis.set_redis_data(cache_key=cache_key, data=users)
        return users

    @staticmethod
    async def get_user(
            db: AsyncSession,
            user_id
    ) -> User:
        redis_data, cache_key = await Redis.get_redis_data(match=f"users:{user_id}")
        if redis_data:
            return redis_data

        result = await db.execute(
            select(User)
            .where(User.user_id == user_id)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found")
        await Redis.set_redis_data(cache_key=cache_key, data=user)
        return user

    @staticmethod
    async def get_user_by_wallet_address(
            db: AsyncSession,
            wallet_public_address: str
    ) -> User | None:
        result = await db.execute(
            select(User)
            .where(User.wallet_public_address == wallet_public_address)
        )
        user = result.scalars().first()
        if not user:
            return None
        return user