from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from freelance_marketplace.api.routes.reviews.reviewsLogic import ReviewsLogic
from freelance_marketplace.db.sql.database import get_sql_db
from freelance_marketplace.models.sql.request_model.ReviewRequest import ReviewRequest

router = APIRouter()

@router.get("/user/review", tags=["reviews"])
async def get_review(
        db: AsyncSession = Depends(get_sql_db),
        review_id: int = Query(...)
):
    return await ReviewsLogic.get(db=db, review_id=review_id)

@router.get("/user/reviews", tags=["reviews"])
async def get_all_reviews_by_user(
        db: AsyncSession = Depends(get_sql_db),
        user_id: int = Query(...)
):
    return await ReviewsLogic.get_all_by_user(db=db, user_id=user_id)

@router.patch("/user/review", tags=["reviews"])
async def update_review(
        review_data: ReviewRequest,
        review_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await ReviewsLogic.update(db=db, review_id=review_id, review_data=review_data)

@router.post("/user/review", tags=["reviews"])
async def create_review(
        review_data: ReviewRequest,
        db: AsyncSession = Depends(get_sql_db),
        reviewer_id: int = Query(...)
):
    return await ReviewsLogic.create(db=db, review_data=review_data, reviewer_id=reviewer_id)

@router.delete("/user/review", tags=["reviews"])
async def delete_review(
        review_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await ReviewsLogic.delete(db=db, review_id=review_id)