from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from freelance_marketplace.api.routes.services.servicesLogic import ServicesLogic
from freelance_marketplace.db.sql.database import get_sql_db
from freelance_marketplace.models.enums.serviceStatus import ServiceStatus
from freelance_marketplace.models.sql.request_model.ServiceRequest import ServiceRequest

router = APIRouter()

@router.get("/service", tags=["services"])
async def get_service(
        db: AsyncSession = Depends(get_sql_db),
        service_id: int = Query(...)
):
    return await ServicesLogic.get_service(db=db, service_id=service_id)

@router.get("/services", tags=["services"])
async def get_services(
        db: AsyncSession = Depends(get_sql_db),
        service_status_id: int | None = Query(None,
                                            description="Filter by service_status_id (CANCELED = 0, DRAFT = 1, AVAILABLE = 2, CLOSED = 3)"),
        service_id: int | None = Query(None, description="Filter by service_id"),
        title: int | None = Query(None, description="Filter by title"),
        description: bool | None = Query(False, description="Filter by description"),
        sub_category_id: bool | None = Query(False, description="Filter by sub_category_id"),
        total_price: bool | None = Query(False, description="Filter by total_price"),
        ## TODO tags: bool | None = Query(False, description="Filter by tags"),
        deleted: bool | None = Query(False, description="Filter by deleted"),
        freelancer_id: bool | None = Query(False, description="Filter by freelancer_id"),
):
    query_params: dict = {
        'service_status_id': service_status_id,
        'service_id': service_id,
        "title": title,
        "description": description,
        "sub_category_id": sub_category_id,
        "total_price": total_price,
        "deleted": deleted,
        "freelancer_id": freelancer_id
    }
    return await ServicesLogic.get_services(db=db, query_params=query_params)

@router.patch("/service", tags=["services"])
async def update_service(
        service_data: ServiceRequest,
        service_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await ServicesLogic.update(db=db, service_id=service_id, service_data=service_data)

@router.patch("/service/status", tags=["services"])
async def update_status(
        service_id: int = Query(...),
        service_status_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    try:
        service_status = ServiceStatus(service_status_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid service_status value")

    return await ServicesLogic.change_status(db=db, service_id=service_id, service_status=service_status)

@router.post("/service", tags=["services"])
async def create_service(
        service_data: ServiceRequest,
        freelancer_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await ServicesLogic.create(db=db, service_data=service_data, freelancer_id=freelancer_id)

@router.delete("/service", tags=["services"])
async def delete_service(
        service_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await ServicesLogic.delete(db=db, service_id=service_id)