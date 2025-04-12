from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.exceptions import HTTPException
from sqlalchemy import select

from freelance_marketplace.api.utils.redis import Redis
from freelance_marketplace.models.sql.sql_tables import Role, User


class UserRolesLogic:

    @staticmethod
    async def get_all(db: AsyncSession):
        cache_key = f"user_roles:all"
        redis_data = await Redis.get_redis_data(cache_key)
        if redis_data:
            return redis_data

        result = await db.execute(select(Role))
        roles = result.scalars().all()
        if not roles:
            raise HTTPException(status_code=204, detail="Roles not found")

        await Redis.set_redis_data(cache_key, roles)
        return roles


    @staticmethod
    async def get_user_role(
            db: AsyncSession,
            user_id: int
    ):
        cache_key = f"user_roles:{user_id}"
        redis_data = await Redis.get_redis_data(cache_key)
        if redis_data:
            return redis_data

        result = await db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.user_id == user_id)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=204, detail="Roles not found")
        await Redis.set_redis_data(cache_key, user)
        return user.role