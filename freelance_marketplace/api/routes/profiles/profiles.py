from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from freelance_marketplace.api.routes.profiles.profilesLogic import ProfilesLogic
from freelance_marketplace.db.sql.database import get_sql_db
from freelance_marketplace.models.sql.request_model.ProfileRequests import ProfileRequest
from freelance_marketplace.api.services.fileStorage import FileStorage 

router = APIRouter()

@router.get("/user/profile", tags=["profile"])
async def get_user_profile(
        db: AsyncSession = Depends(get_sql_db),
        user_id: int = Query(...)
):
    return await ProfilesLogic.get_profile(db=db, user_id=user_id)

@router.patch("/user/profile", tags=["profile"])
async def update_user_profile(
        profile_data: ProfileRequest,
        user_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await ProfilesLogic.update(db=db, user_id=user_id, profile=profile_data)

@router.post("/user/profile", tags=["profile"])
async def create_user_profile(
        profile_data: ProfileRequest,
        user_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    ## TODO test if a user can create multiple profiles.
    return await ProfilesLogic.create(db=db, profile=profile_data, user_id=user_id)

@router.delete("/user/profile", tags=["profile"])
async def delete_user_profile(
        user_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await ProfilesLogic.delete(db=db, user_id=user_id)

@router.post("/user/profile/picture", tags=["profile"])
async def upload_profile_picture(
    user_id: int = Query(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_sql_db)
):
    return await ProfilesLogic.update_profile_picture(user_id=user_id, file=file, db=db)