from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from freelance_marketplace.api.routes.reviews.reviewsLogic import ReviewsLogic
from freelance_marketplace.db.sql.database import get_sql_db
from freelance_marketplace.models.sql.request_model.ReviewRequest import ReviewRequest

router = APIRouter()

@router.get("/review", tags=["reviews"])
async def get_review(
        db: AsyncSession = Depends(get_sql_db),
        review_id: int = Query(...)
):
    return await ReviewsLogic.get(db=db, review_id=review_id)

@router.get("/reviews", tags=["reviews"])
async def get_all(
        db: AsyncSession = Depends(get_sql_db),
        deleted: int | None = Query(None, description="Filter by deleted"),
        ## TODO comment: str | None = Query(None,description="Filter by comment"),
        rating: float | None = Query(None, description="Filter by rating"),
        ## TODO max_rating: float | None = Query(None, description="Filter by max_rating value"),
        ## TODO min_rating: float | None = Query(None, description="Filter by min_rating value"),
        reviewer_id: int | None = Query(None, description="Filter by reviewer_id"),
        reviewee_id: bool | None = Query(False, description="Filter by reviewee_id")
):
    query_params: dict = {
        'rating': rating,
        'reviewer_id': reviewer_id,
        "reviewee_id": reviewee_id,
        "deleted": deleted,
    }
    return await ReviewsLogic.get_all(db=db, query_params=query_params)

@router.patch("/review", tags=["reviews"])
async def update_review(
        review_data: ReviewRequest,
        review_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await ReviewsLogic.update(db=db, review_id=review_id, review_data=review_data)

@router.post("/review", tags=["reviews"])
async def create_review(
        review_data: ReviewRequest,
        db: AsyncSession = Depends(get_sql_db),
        reviewer_id: int = Query(...)
):
    return await ReviewsLogic.create(db=db, review_data=review_data, reviewer_id=reviewer_id)

@router.delete("/review", tags=["reviews"])
async def delete_review(
        review_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await ReviewsLogic.delete(db=db, review_id=review_id)