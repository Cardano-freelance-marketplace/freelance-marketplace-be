from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.routes.users.users_logic import UsersLogic
from freelance_marketplace.db.sql.database import get_sql_db
from freelance_marketplace.models.sql.request_model.UserRequest import UserRequest

router = APIRouter()

@router.get("/user", tags=["users"])
async def create_user(
        user: UserRequest,
        db: AsyncSession = Depends(get_sql_db)
) -> UserModel:
    return await UsersLogic.create(db=db, user=user)

@router.post("/user", tags=["users"])
async def create_user(
        user: UserRequest,
        db: AsyncSession = Depends(get_sql_db)
):
    return await UsersLogic.create(db=db, user=user)

@router.post("/user", tags=["users"])
async def create_user(
        user: UserRequest,
        db: AsyncSession = Depends(get_sql_db)
):
    return await UsersLogic.create(db=db, user=user)

@router.post("/user", tags=["users"])
async def create_user(
        user: UserRequest,
        db: AsyncSession = Depends(get_sql_db)
):
    return await UsersLogic.create(db=db, user=user)

@router.post("/user", tags=["users"])
async def create_user(
        user: UserRequest,
        db: AsyncSession = Depends(get_sql_db)
):
    return await UsersLogic.create(db=db, user=user)