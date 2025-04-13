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
async def get_all(
        db: AsyncSession = Depends(get_sql_db),
        sub_category_id: int | None = Query(None, description="Filter by sub_category_id"),
        request_status_id: int | None = Query(None, description="Filter by request_status_id (CANCELED = 0, DRAFT = 1, REQUESTING_FREELANCER = 2, IN_PROGRESS = 3, COMPLETED = 4)"),
        client_id: int | None = Query(None, description="Filter by client_id"),
        deleted: bool | None = Query(False, description="Filter by deleted")
):
    query_params: dict = {
        'request_status_id': request_status_id,
        "client_id": client_id,
        "deleted": deleted,
        "sub_category_id": sub_category_id
    }
    return await RequestsLogic.get_sub_category_requests(db=db, query_params=query_params)

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