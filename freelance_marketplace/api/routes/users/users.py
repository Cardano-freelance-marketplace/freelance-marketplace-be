from typing import List, Any, Type, Coroutine

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Result
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.routes.users.users_logic import UsersLogic
from freelance_marketplace.db.sql.database import get_sql_db
from freelance_marketplace.models.sql.models.userModel import UserModel
from freelance_marketplace.models.sql.request_model.UserRequest import UserRequest
from freelance_marketplace.models.sql.sql_tables import User

router = APIRouter()

@router.post("/user", tags=["users"])
async def create_user(
        user: UserRequest,
        db: AsyncSession = Depends(get_sql_db)
) -> bool:
    return await UsersLogic.create(db=db, user=user)

@router.delete("/user", tags=["users"])
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_sql_db)
):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    return await UsersLogic.delete(db=db, user_id=user_id)

@router.patch("/user", tags=["users"])
async def update_user(
        user: UserRequest,
        user_id: int,
        db: AsyncSession = Depends(get_sql_db)
):
    return await UsersLogic.update(db=db, user_id=user_id, user=user)

@router.get("/user", tags=["users"])
async def get_single_user(
        user_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
) -> Type[User]:
    return await UsersLogic.get_user(
        db=db,
        user_id=user_id
    )

@router.get("/user", tags=["users"])
async def get_all(
        db: AsyncSession = Depends(get_sql_db)
) -> Result[tuple[User]]:
    return await UsersLogic.get_all(db=db)

@router.get("/user", tags=["users"])
async def get_users_by_job(
        job_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
) -> List[UserModel]:
    return await UsersLogic.get_user_by_job(db=db, job_id=job_id)