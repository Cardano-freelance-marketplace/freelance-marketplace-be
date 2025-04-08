from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from freelance_marketplace.api.routes.user_types.user_types_logic import UserTypesLogic
from freelance_marketplace.db.sql.database import get_sql_db
from freelance_marketplace.models.enums.userType import UserType as UserTypeEnum

router = APIRouter()

@router.post("/types", tags=["types"])
async def get_types(
        db: AsyncSession = Depends(get_sql_db)
):
    return await UserTypesLogic.get_all(db)

@router.post("/user/type", tags=["types"])
async def get_user_type(
        user_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):

    return await UserTypesLogic.get_user_type(
        db=db,
        user_id=user_id
    )

@router.patch("/user/type", tags=["types"])
async def update_user_type(
        user_id: int = Query(...),
        type_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    try:
        user_type = UserTypeEnum(type_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid user type value")

    return await UserTypesLogic.update_user_type(
        db=db,
        type=user_type,
        user_id=user_id
    )