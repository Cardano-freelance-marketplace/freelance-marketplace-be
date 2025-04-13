from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from freelance_marketplace.api.routes.sub_categories.subCategoriesLogic import SubCategoriesLogic
from freelance_marketplace.db.sql.database import get_sql_db
from freelance_marketplace.models.sql.request_model.SubCategoryRequest import SubCategoryRequest

router = APIRouter()

@router.get("/sub-category", tags=["sub-categories"])
async def get_sub_category(
        db: AsyncSession = Depends(get_sql_db),
        sub_category_id: int = Query(...)
):
    return await SubCategoriesLogic.get(db=db, sub_category_id=sub_category_id)

@router.get("/sub-categories", tags=["sub-categories"])
async def get_all(
        db: AsyncSession = Depends(get_sql_db),
        sub_category_name: int | None = Query(None, description="Filter by sub_category_name"),
        sub_category_description: int | None = Query(None, description="Filter by sub_category_description"),
        category_id: int | None = Query(None, description="Filter by category_id"),
        deleted: bool | None = Query(False, description="Filter by deleted")
):
    query_params: dict = {
        'sub_category_name': sub_category_name,
        'sub_category_description': sub_category_description,
        "category_id": category_id,
        "deleted": deleted
    }
    return await SubCategoriesLogic.get_all(db=db, query_params=query_params)

@router.delete("/sub-category", tags=["sub-categories"])
async def delete_sub_category(
        sub_category_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await SubCategoriesLogic.delete(db=db, sub_category_id=sub_category_id)

@router.patch("/sub-category", tags=["sub-categories"])
async def update_sub_category(
        sub_category_data: SubCategoryRequest,
        sub_category_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await SubCategoriesLogic.update(db=db, sub_category_id=sub_category_id, sub_category_data=sub_category_data)

@router.post("/sub-category", tags=["sub-categories"])
async def create_sub_category(
        sub_category_data: SubCategoryRequest,
        db: AsyncSession = Depends(get_sql_db)
):
    return await SubCategoriesLogic.create(db=db, sub_category_data=sub_category_data)

