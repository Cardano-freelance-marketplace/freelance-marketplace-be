from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.services.redis import Redis
from freelance_marketplace.api.utils.sql_util import soft_delete, build_transaction_query
from freelance_marketplace.models.sql.request_model.SubCategoryRequest import SubCategoryRequest
from freelance_marketplace.models.sql.sql_tables import Category, SubCategory


class SubCategoriesLogic:

    @staticmethod
    async def create(
            db : AsyncSession,
            sub_category_data: SubCategoryRequest
    ) -> bool:
        try:
            await SubCategory.create(db=db, **sub_category_data.model_dump())
            await Redis.invalidate_cache(prefix="subcategories")
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def delete(
            db: AsyncSession,
            sub_category_id: int
    )-> bool:
        try:
            result = await soft_delete(db=db, object=Category, attribute="sub_category_id", object_id=sub_category_id)
            if result.rowcount > 0:
                await Redis.invalidate_cache(prefix="subcategories")
                return True
            else:
                raise HTTPException(status_code=404, detail="Sub category not found or already deleted")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def update(
            db: AsyncSession,
            sub_category_id: int,
            sub_category_data: SubCategoryRequest
    ) -> bool:
        try:
            stmt = (
                update(SubCategory)
                .where(SubCategory.sub_category_id == sub_category_id)
                .values(**sub_category_data.model_dump())
                .execution_options(synchronize_session="fetch")
            )
            await db.execute(stmt)
            await db.commit()
            await Redis.invalidate_cache(prefix="subcategories")

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
            sub_category_id: int
    ) -> SubCategory:
        try:
            redis_data, cache_key = await Redis.get_redis_data(match=f'subcategories:{sub_category_id}')
            if redis_data:
                return redis_data

            result = await db.execute(select(SubCategory).where(SubCategory.sub_category_id == sub_category_id))
            sub_category = result.scalars().first()
            if not sub_category:
                raise HTTPException(status_code=404, detail=f"Sub-Category not found")

            await Redis.set_redis_data(cache_key, data=sub_category)
            return sub_category

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def get_all(
            db: AsyncSession,
            query_params: dict
    ) -> Sequence[SubCategory]:
        try:
            redis_data, cache_key = await Redis.get_redis_data(prefix='subcategories', query_params=query_params)
            if redis_data:
                return redis_data

            transaction = await build_transaction_query(
                object=SubCategory,
                query_params=query_params
            )

            result = await db.execute(transaction)
            sub_categories = result.scalars().all()
            if not sub_categories:
                raise HTTPException(status_code=404, detail=f"Sub-categories not found")

            await Redis.set_redis_data(cache_key, data=sub_categories)
            return sub_categories

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")