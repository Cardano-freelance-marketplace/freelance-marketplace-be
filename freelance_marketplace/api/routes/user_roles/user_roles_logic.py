from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from sqlalchemy import select
from freelance_marketplace.models.sql_roles import Roles


class UserRolesLogic:

    @staticmethod
    async def get_all(db: AsyncSession):
        result = await db.execute(select(Roles))
        roles = result.scalars().all()
        if not roles:
            raise HTTPException(status_code=204, detail="Roles not found")

        return roles