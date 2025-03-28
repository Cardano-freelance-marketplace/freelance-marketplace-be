from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.routes.users.users_logic import UsersLogic
from freelance_marketplace.db.sql.database import get_sql_db
from freelance_marketplace.models.sql.models.userModel import UserModel
from freelance_marketplace.models.sql.request_model.UserRequest import UserRequest

router = APIRouter()

@router.post("/user", tags=["users"])
async def create_user(
        user: UserRequest,
        db: AsyncSession = Depends(get_sql_db)
) -> UserModel:
    return await UsersLogic.create(db=db, user=user)

@router.delete("/user", tags=["users"])
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_sql_db)
):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    return await UsersLogic.delete(db=db, user_id=user_id)

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