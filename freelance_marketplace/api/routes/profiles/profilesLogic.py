import os
import uuid

from fastapi import HTTPException, UploadFile, File
from sqlalchemy import update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.services.fileStorage import FileStorage
from freelance_marketplace.api.services.redis import Redis
from freelance_marketplace.api.utils.file_manipulation_utils import FileManipulator
from freelance_marketplace.api.utils.sql_util import soft_delete
from freelance_marketplace.core.config import settings
from freelance_marketplace.models.sql.request_model.ProfileRequests import ProfileRequest
from freelance_marketplace.models.sql.sql_tables import Profiles
from io import BytesIO

class ProfilesLogic:

    @staticmethod
    async def create(
            db : AsyncSession,
            user_id: int,
            profile: ProfileRequest
    ) -> bool:
        try:
            await Profiles.create(db=db, user_id=user_id, **profile.model_dump())
            await Redis.invalidate_cache(f"profiles:{user_id}")
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def delete(
            db: AsyncSession,
            user_id: int
    )-> bool:
        try:
            result = await soft_delete(db=db, object=Profiles, attribute="profile_id", object_id=user_id)
            if result.rowcount > 0:
                await Redis.invalidate_cache(f"profiles:{user_id}")
                return True
            else:
                return False
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def update(
            db: AsyncSession,
            user_id: int,
            profile: ProfileRequest
    ) -> bool:
        try:
            stmt = (
                update(Profiles)
                .where(Profiles.user_id == user_id)
                .values(**profile.model_dump())
                .execution_options(synchronize_session="fetch")
            )
            await db.execute(stmt)
            await db.commit()
            await Redis.invalidate_cache(f"profiles:{user_id}")
            return True

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")


        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def get_profile(
            db: AsyncSession,
            user_id
    ):
        try:
            redis_cache, cache_key = await Redis.get_redis_data(match=f"profiles:{user_id}")
            if redis_cache:
                return redis_cache

            result = await db.execute(select(Profiles).where(Profiles.user_id == user_id))
            profile = result.scalars().first()
            if not profile:
                raise HTTPException(status_code=404, detail=f"User profile not found")
            await Redis.set_redis_data(cache_key=cache_key, data=profile)
            return profile

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def update_profile_picture(
        db: AsyncSession,
        file: UploadFile,
        user_id: int
    ):

        file_storage = FileStorage(bucket_name="profile_pictures")
        file_path = await FileManipulator.create_tmp_file(file=file)

        if not FileManipulator.is_image(file_path=file_path):
            raise HTTPException(status_code=400, detail=f"File must be an image")

        await FileManipulator.compress_image(file_path=file_path)
        try:
            file_hash = file_storage.generate_file_hash(file_path=file_path)
            s3_key = f"profile_pictures/{file_hash}_{uuid.uuid4()}"

            # Upload to S3
            file_storage.upload_file(file_path, s3_key)
        finally:
            os.remove(file_path)

        # Update profile in DB
        await Profiles.edit(
            db=db,
            profile_id=user_id,
            data={"profile_picture_identifier": s3_key}
        )

        presigned_url = file_storage.generate_presigned_url(s3_key)
        return {"s3_key": s3_key, "url": presigned_url}