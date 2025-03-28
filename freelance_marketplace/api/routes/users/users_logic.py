from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from freelance_marketplace.models.sql.request_model.UserRequest import UserRequest
from freelance_marketplace.models.sql.sql_tables import User


class UsersLogic:

    @staticmethod
    async def create(
            db : AsyncSession,
            user: UserRequest
    ):
        return await User.create(db=db, **user.model_dump())

    @staticmethod
    async def delete(
            db: AsyncSession,
            user_id: int
    ):
        try:
            transaction = delete(User).where(User.user_id == user_id)
            await db.execute(transaction)
            await db.commit()
            return "User deleted successfully"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def update():
        raise HTTPException(status_code=500, detail="This feature is not implemented yet")

    @staticmethod
    async def get_all():
        raise HTTPException(status_code=500, detail="This feature is not implemented yet")

    @staticmethod
    async def get_user(user_id):
        raise HTTPException(status_code=500, detail="This feature is not implemented yet")

    @staticmethod
    async def get_user_by_job(job_id):
        raise HTTPException(status_code=500, detail="This feature is not implemented yet")