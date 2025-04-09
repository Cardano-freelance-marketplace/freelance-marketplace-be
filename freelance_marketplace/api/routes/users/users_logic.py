from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession
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
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def delete(
            db: AsyncSession,
            user_id: int
    )-> bool:
        try:
            transaction = delete(User).where(User.user_id == user_id)
            await db.execute(transaction)
            await db.commit()
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def update(
            db: AsyncSession,
            user_id: int,
            user: UserRequest
    ) -> bool:

        # TODO WHEN UPDATING A USER SET, UPDATED_AT TO NOW()
        try:
            stmt = (
                update(User)
                .where(User.user_id == user_id)
                .values(**user.model_dump())
                .execution_options(synchronize_session="fetch")
            )
            await db.execute(stmt)
            await db.commit()

            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail="This feature is not implemented yet")

    @staticmethod
    async def get_all(
            db: AsyncSession,
    ) -> Sequence[User]:
        result = await db.execute(select(User))
        users = result.scalars().all()
        if not users:
            raise HTTPException(status_code=204, detail="Users not found")
        return users

    @staticmethod
    async def get_user(
            db: AsyncSession,
            user_id
    ) -> User:
        try:
            result = await db.execute(select(User).where(User.user_id == user_id))
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=204, detail=f"User {user_id} not found")
            return user

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def get_user_by_service(
            db: AsyncSession,
            service_id: int,
    ):
        ##TODO Create get user by job
        # job = await db.execute(select(Job.job_id == job_id))
        # if not job:
        #     raise HTTPException(status_code=204, detail=f"Job {job_id} not found")
        # users = [job.freelancer_id, job.client_id]
        raise HTTPException(status_code=500, detail="This feature is not implemented yet")

    @staticmethod
    async def get_user_by_request(
            db: AsyncSession,
            request_id: int,
    ):
        ##TODO Create get user by job
        # job = await db.execute(select(Job.job_id == job_id))
        # if not job:
        #     raise HTTPException(status_code=204, detail=f"Job {job_id} not found")
        # users = [job.freelancer_id, job.client_id]
        raise HTTPException(status_code=500, detail="This feature is not implemented yet")