from typing import Sequence
from fastapi import HTTPException
from sqlalchemy import delete, update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from freelance_marketplace.api.utils.redis import Redis
from freelance_marketplace.api.utils.sql_util import soft_delete, build_transaction_query
from freelance_marketplace.models.sql.request_model.ReviewRequest import ReviewRequest
from freelance_marketplace.models.sql.sql_tables import Review


class ReviewsLogic:

    @staticmethod
    async def create(
            db : AsyncSession,
            reviewer_id: int,
            review_data: ReviewRequest
    ) -> bool:
        try:
            await Review.create(db=db, reviewer_id=reviewer_id, **review_data.model_dump())
            await Redis.invalidate_cache(prefix="reviews")
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def delete(
            db: AsyncSession,
            review_id: int
    )-> bool:
        try:
            result = await soft_delete(db=db, object=Review, attribute="review_id", object_id=review_id)
            if result.rowcount > 0:
                await Redis.invalidate_cache(prefix="reviews")
                return True
            else:
                raise HTTPException(status_code=404, detail="Notification not found or already deleted")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def update(
            db: AsyncSession,
            review_id: int,
            review_data: ReviewRequest
    ) -> bool:
        try:
            stmt = (
                update(Review)
                .where(Review.review_id == review_id)
                .values(**review_data.model_dump())
                .execution_options(synchronize_session="fetch")
            )
            await db.execute(stmt)
            await db.commit()
            await Redis.invalidate_cache(prefix="reviews")

            return True

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")


        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=f"{str(e)}")
    @staticmethod
    async def get(
            db: AsyncSession,
            review_id: int
    ) -> Review:
        try:
            redis_data, cache_key = await Redis.get_redis_data(match=f"reviews:{review_id}")
            if redis_data:
                return redis_data

            result = await db.execute(select(Review).where(Review.review_id == review_id))
            review = result.scalars().first()
            if not review:
                raise HTTPException(status_code=404, detail=f"review not found")
            await Redis.set_redis_data(cache_key, review)
            return review

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def get_all(
            db: AsyncSession,
            query_params: dict
    ) -> Sequence[Review]:
        try:
            redis_cache, cache_key = await Redis.get_redis_data(prefix="reviews", query_params=query_params)
            if redis_cache:
                return redis_cache

            transaction = await build_transaction_query(
                object=Review,
                query_params=query_params
            )
            result = await db.execute(transaction)
            reviews = result.scalars().all()
            if not reviews:
                raise HTTPException(status_code=404, detail=f"reviews not found")

            await Redis.set_redis_data(cache_key, data=reviews)
            return reviews

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

