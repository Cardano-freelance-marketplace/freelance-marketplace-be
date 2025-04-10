from typing import Any, Coroutine, Sequence

from fastapi import HTTPException
from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession

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
            await db.execute(transaction)
            await db.commit()
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def update(
            db: AsyncSession,
            category_id: int,
            category: CategoryRequest
    ) -> bool:

        # TODO WHEN UPDATING A USER SET, UPDATED_AT TO NOW()
        try:
            stmt = (
                update(Category)
                .where(Category.category_id == category_id)
                .values(**category.model_dump())
                .execution_options(synchronize_session="fetch")
            )
            await db.execute(stmt)
            await db.commit()

            return True
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="This feature is not implemented yet")

    @staticmethod
    async def get(
            db: AsyncSession,
            category_id: int
    ) -> Category:
        try:
            result = await db.execute(select(Category).where(Category.category_id == category_id))
            category = result.scalars().first()
            if not category:
                raise HTTPException(status_code=204, detail=f"category for with id : {category_id} \n not found")
            return category

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def get_all(
            db: AsyncSession,
    ) -> Sequence[Category]:
        try:
            result = await db.execute(select(Category))
            categories = result.scalars().all()
            if not categories:
                raise HTTPException(status_code=404, detail=f"categories not found")
            return categories

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")