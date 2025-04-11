from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from freelance_marketplace.api.routes.requests.requestsLogic import RequestsLogic
from freelance_marketplace.db.sql.database import get_sql_db
from freelance_marketplace.models.enums.requestStatus import RequestStatus
from freelance_marketplace.models.sql.request_model.RequestRequest import RequestRequest

router = APIRouter()

@router.get("/request", tags=["requests"])
async def get_request(
        db: AsyncSession = Depends(get_sql_db),
        request_id: int = Query(...)
):
    return await RequestsLogic.get_request(db=db, request_id=request_id)

@router.get("/requests", tags=["requests"])
async def get_request(
        db: AsyncSession = Depends(get_sql_db),
):
    return await RequestsLogic.get_requests(db=db)

@router.get("/requests", tags=["requests"])
async def get_requests(
        db: AsyncSession = Depends(get_sql_db),
):
    return await RequestsLogic.get_requests(db=db)

@router.get("/user/requests", tags=["requests"])
async def get_user_requests(
        db: AsyncSession = Depends(get_sql_db),
        client_id: int = Query(...)
):
    return await RequestsLogic.get_user_requests(db=db, client_id=client_id)

@router.get("/sub-category/requests", tags=["requests"])
async def get_sub_category_requests(
        db: AsyncSession = Depends(get_sql_db),
        sub_category_id: int = Query(...)
):
    return await RequestsLogic.get_sub_category_requests(db=db, sub_category_id=sub_category_id)

@router.patch("/request", tags=["requests"])
async def update_request(
        request_data: RequestRequest,
        request_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await RequestsLogic.update(db=db, request_id=request_id, request_data=request_data)

@router.patch("/request/status", tags=["requests"])
async def update_status(
        request_id: int = Query(...),
        request_status_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    try:
        request_status = RequestStatus(request_status_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Request_status value")

    return await RequestsLogic.change_status(db=db, request_id=request_id, request_status=request_status)

@router.post("/request", tags=["requests"])
async def create_request(
        request_data: RequestRequest,
        client_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await RequestsLogic.create(db=db, request_data=request_data, client_id=client_id)

@router.delete("/request", tags=["requests"])
async def delete_request(
        request_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await RequestsLogic.delete(db=db, request_id=request_id)