from fastapi import HTTPException, UploadFile, File
from sqlalchemy import update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.services.redis import Redis
from freelance_marketplace.api.utils.sql_util import soft_delete
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
    async def upload_profile_picture(
        db: AsyncSession,
        file: UploadFile,
        user_id: int
    ):
        file_storage = FileStorage(bucket_name="profile_pictures")

        # Read file content into memory
        content = await file.read()
        file_stream = BytesIO(content)

        # Generate a hash from the content (or the stream)
        file_hash = file_storage.generate_file_hash(content)
        s3_key = f"profile_pictures/{file_hash}_{uuid.uuid4()}"

        # Upload from memory
        file_storage.upload_fileobj(file_stream, s3_key)

        # Update profile in DB
        await Profiles.edit(
            db=db,
            profile_id=user_id,
            data={"profile_picture_identifier": s3_key}
        )

        presigned_url = file_storage.generate_presigned_url(s3_key)
        return {"s3_key": s3_key, "url": presigned_url}

    '''
    @staticmethod
    async def update_profile_picture(
        db: AsyncSession,
        file: UploadFile,
        user_id: int
    ):
    
        file_storage = FileStorage(bucket_name="profile_pictures")

        # Save uploaded file temporarily
        temp_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Generate unique S3 key
        file_hash = file_storage.generate_file_hash(temp_path)
        s3_key = f"profile_pictures/{file_hash}_{uuid.uuid4()}"
        
        # Upload to S3
        try:
            file_storage.upload_file(temp_path, s3_key)
        finally:
            os.remove(temp_path)  # clean up

        # Update profile in DB
        await Profiles.edit(
            db=db,
            profile_id=user_id,
            data={"profile_picture_identifier": s3_key}
        )

        # Optional: return a pre-signed URL
        presigned_url = file_storage.generate_presigned_url(s3_key)
        return {"s3_key": s3_key, "url": presigned_url}
    '''