from typing import Sequence
from fastapi import HTTPException
from sqlalchemy import delete, update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.utils.redis import Redis
from freelance_marketplace.models.sql.request_model.CategoryRequest import CategoryRequest
from freelance_marketplace.models.sql.sql_tables import Category


class CategoriesLogic:

    @staticmethod
    async def create(
            db : AsyncSession,
            category: CategoryRequest
    ) -> bool:
        try:
            await Category.create(db=db, **category.model_dump())
            await Redis.invalidate_cache(prefix='categories')
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def delete(
            db: AsyncSession,
            category_id: int
    )-> bool:
        try:
            transaction = delete(Category).where(Category.category_id == category_id)
            result = await db.execute(transaction)
            await db.commit()
            if result.rowcount > 0:
                await Redis.invalidate_cache(prefix='categories')
                return True
            else:
                raise HTTPException(status_code=404, detail="Notification not found or already deleted")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def update(
            db: AsyncSession,
            category_id: int,
            category: CategoryRequest
    ) -> bool:
        try:
            stmt = (
                update(Category)
                .where(Category.category_id == category_id)
                .values(**category.model_dump())
                .execution_options(synchronize_session="fetch")
            )
            await db.execute(stmt)
            await db.commit()
            await Redis.invalidate_cache(prefix='categories')

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
            category_id: int
    ) -> Category:
        try:
            result = await db.execute(select(Category).where(Category.category_id == category_id))
            category = result.scalars().first()
            if not category:
                raise HTTPException(status_code=404, detail=f"Category not found")
            return category

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def get_all(
            db: AsyncSession,
    ) -> Sequence[Category]:
        try:
            cache_key = 'categories:all'
            redis_data = await Redis.get_redis_data(cache_key)
            if redis_data:
                return redis_data

            result = await db.execute(select(Category))
            categories = result.scalars().all()
            if not categories:
                raise HTTPException(status_code=404, detail=f"categories not found")

            await Redis.set_redis_data(cache_key, data=categories)
            return categories

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")