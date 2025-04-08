from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.exceptions import HTTPException
from sqlalchemy import select
from freelance_marketplace.models.sql.sql_tables import User, UserType
from freelance_marketplace.models.enums.userType import UserType as UserTypeEnum



class UserTypesLogic:

    @staticmethod
    async def get_all(
            db: AsyncSession
    ):
        result = await db.execute(select(UserType))
        types = result.scalars().all()
        if not types:
            raise HTTPException(status_code=204, detail="Types not found")

        return types


    @staticmethod
    async def get_user_type(
            db: AsyncSession,
            user_id: int
    ):
        result = await db.execute(
            select(User)
            .options(selectinload(User.type))
            .where(User.user_id == user_id)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=204, detail="User Type not found")

        return user.type

    @staticmethod
    async def update_user_type(
            db: AsyncSession,
            type: UserTypeEnum,
            user_id: int
    ) -> bool:
        try:
            result = await db.execute(
                select(User)
                .where(User.user_id == user_id)
            )
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=204, detail="User not found")

            user.type_id = type.value
            await db.commit()
            return True
        except Exception as e:
            raise e
