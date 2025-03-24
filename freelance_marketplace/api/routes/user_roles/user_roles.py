from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.routes.user_roles.user_roles_logic import UserRolesLogic
from freelance_marketplace.db.sql.database import get_sql_db

router = APIRouter()

@router.post("/roles", tags=["roles"])
async def get_roles(
        db: AsyncSession = Depends(get_sql_db)
):
    return await UserRolesLogic.get_all(db)