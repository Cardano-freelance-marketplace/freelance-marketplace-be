from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.exceptions import HTTPException
from sqlalchemy import select
from freelance_marketplace.models.sql.sql_tables import Role, User


class UserRolesLogic:

    @staticmethod
    async def get_all(db: AsyncSession):
        result = await db.execute(select(Role))
        roles = result.scalars().all()
        if not roles:
            raise HTTPException(status_code=204, detail="Roles not found")

        return roles


    @staticmethod
    async def get_user_role(
            db: AsyncSession,
            user_id: int
    ):
        result = await db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.user_id == user_id)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=204, detail="Roles not found")

        return user.role