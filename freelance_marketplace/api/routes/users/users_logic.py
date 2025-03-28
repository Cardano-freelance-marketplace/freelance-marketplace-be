from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.models.sql.request_model.UserRequest import UserRequest


class UsersLogic:

    @staticmethod
    async def create(db : AsyncSession, user: UserRequest):
        pass

    @staticmethod
    async def delete():
        raise HTTPException(status_code=500, detail="This feature is not implemented yet")

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