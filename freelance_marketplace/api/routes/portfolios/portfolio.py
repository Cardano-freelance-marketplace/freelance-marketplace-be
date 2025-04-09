from fastapi import APIRouter, Query, HTTPException
from freelance_marketplace.db.no_sql.mongo import Mongo
from freelance_marketplace.models.no_sql.portfolio import Portfolio
from freelance_marketplace.models.no_sql.request_models.portfolioRequest import PortfolioRequest

router = APIRouter()

@router.post("/user/portfolio", tags=["portfolio"])
async def create_portfolio(
        portfolio: Portfolio,
        user_id: int = Query(...)
) -> bool:

    ##Check if user already has a portfolio
    if await Portfolio.find_one(Portfolio.user_id == user_id):
        raise HTTPException(status_code=400, detail="User already has a Portfolio")

    await portfolio.create()
    return True

@router.delete("/user/portfolio", tags=["portfolio"])
async def delete_portfolio(
        user_id: int = Query(...),
) -> bool:
    result = await Portfolio.find(Portfolio.user_id == user_id).delete()
    if result.deleted_count > 0:
        return True
    else:
        raise HTTPException(status_code=404, detail="Portfolio not found or already deleted")

@router.patch("/user/portfolio", tags=["portfolio"])
async def update_portfolio(
        user_portfolio: PortfolioRequest,
        user_id: int,
) -> bool:
    portfolio_result = await Portfolio.find_one(Portfolio.user_id == user_id)

    if not portfolio_result:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    await Mongo.replace_item(portfolio_result, user_portfolio)
    return True

@router.get("/user/portfolio", tags=["portfolio"])
async def get_single_portfolio(
        user_id: int = Query(...),
):
    return await Portfolio.find_one(Portfolio.user_id == user_id)