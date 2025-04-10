from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.routes.categories.categoriesLogic import CategoriesLogic
from freelance_marketplace.db.sql.database import get_sql_db
from freelance_marketplace.models.sql.request_model.CategoryRequest import CategoryRequest

router = APIRouter()

@router.get("/category", tags=["categories"])
async def get_category(
        db: AsyncSession = Depends(get_sql_db),
        category_id: int = Query(...)
):
    return await CategoriesLogic.get(db=db, category_id=category_id)

@router.get("/categories", tags=["categories"])
async def get_all_categories(
        db: AsyncSession = Depends(get_sql_db),
):
    return await CategoriesLogic.get_all(db=db)

@router.patch("/category", tags=["categories"])
async def update_category(
        category_data: CategoryRequest,
        category_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await CategoriesLogic.update(db=db, category_id=category_id, category=category_data)

@router.post("/category", tags=["categories"])
async def create_category(
        category_data: CategoryRequest,
        db: AsyncSession = Depends(get_sql_db)
):
    return await CategoriesLogic.create(db=db, category=category_data)

@router.delete("/category", tags=["categories"])
async def delete_category(
        category_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await CategoriesLogic.delete(db=db, category_id=category_id)