from typing import Any, Coroutine, Sequence

from fastapi import HTTPException
from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.models.sql.request_model.CategoryRequest import CategoryRequest
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
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def delete(
            db: AsyncSession,
            sub_category_id: int
    )-> bool:
        try:
            transaction = delete(SubCategory).where(SubCategory.sub_category_id == sub_category_id)
            await db.execute(transaction)
            await db.commit()
            return True
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

            return True
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def get(
            db: AsyncSession,
            sub_category_id: int
    ) -> SubCategory:
        try:
            result = await db.execute(select(SubCategory).where(SubCategory.sub_category_id == sub_category_id))
            sub_category = result.scalars().first()
            if not sub_category:
                raise HTTPException(status_code=204, detail=f"sub category with id : {sub_category_id} \n not found")
            return sub_category

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def get_all(
            db: AsyncSession,
    ) -> Sequence[SubCategory]:
        try:
            result = await db.execute(select(SubCategory))
            sub_categories = result.scalars().all()
            if not sub_categories:
                raise HTTPException(status_code=404, detail=f"Sub-categories not found")
            return sub_categories

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def get_all_by_category(
            db: AsyncSession,
            category_id: int
    ) -> Sequence[SubCategory]:
        try:
            result = await db.execute(
                select(SubCategory)
                .where(SubCategory.category_id == category_id)
            )
            sub_categories = result.scalars().all()
            if not sub_categories:
                raise HTTPException(status_code=404, detail=f"Sub-categories not found")
            return sub_categories

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")