from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.routes.user_roles.user_roles_logic import UserRolesLogic
from freelance_marketplace.db.sql.database import get_sql_db

router = APIRouter()

@router.post("/roles", tags=["roles"])
async def get_roles(
        db: AsyncSession = Depends(get_sql_db)
):
    return await UserRolesLogic.get_all(db)

@router.post("/user/role", tags=["roles"])
async def get_user_role(
        user_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):

    return await UserRolesLogic.get_user_role(
        db=db,
        user_id=user_id
    )