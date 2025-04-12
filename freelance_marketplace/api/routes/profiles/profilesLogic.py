from fastapi import HTTPException
from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.models.sql.request_model.ProfileRequests import ProfileRequest
from freelance_marketplace.models.sql.sql_tables import Profiles


class ProfilesLogic:

    @staticmethod
    async def create(
            db : AsyncSession,
            user_id: int,
            profile: ProfileRequest
    ) -> bool:
        try:
            await Profiles.create(db=db, user_id=user_id, **profile.model_dump())
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def delete(
            db: AsyncSession,
            user_id: int
    )-> bool:
        try:
            transaction = delete(Profiles).where(Profiles.user_id == user_id)
            result = await db.execute(transaction)
            await db.commit()
            if result.rowcount > 0:
                return True
            else:
                return False
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def update(
            db: AsyncSession,
            user_id: int,
            profile: ProfileRequest
    ) -> bool:

        # TODO WHEN UPDATING A USER SET, UPDATED_AT TO NOW()
        try:
            stmt = (
                update(Profiles)
                .where(Profiles.user_id == user_id)
                .values(**profile.model_dump())
                .execution_options(synchronize_session="fetch")
            )
            await db.execute(stmt)
            await db.commit()

            return True
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="This feature is not implemented yet")

    @staticmethod
    async def get_profile(
            db: AsyncSession,
            user_id
    ) -> Profiles:
        try:
            result = await db.execute(select(Profiles).where(Profiles.user_id == user_id))
            profile = result.scalars().first()
            if not profile:
                raise HTTPException(status_code=404, detail=f"User profile not found")
            return profile

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")