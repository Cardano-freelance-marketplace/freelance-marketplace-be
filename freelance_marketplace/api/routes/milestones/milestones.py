from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from freelance_marketplace.api.routes.milestones.milestonesLogic import MilestonesLogic
from freelance_marketplace.db.sql.database import get_sql_db
from freelance_marketplace.models.sql.request_model.MilestoneApproveStatusRequest import MilestoneApproveStatusRequest
from freelance_marketplace.models.sql.request_model.MilestoneRequest import MilestoneRequest

router = APIRouter()

@router.get("/milestone", tags=["milestones"])
async def get_milestone(
        db: AsyncSession = Depends(get_sql_db),
        milestone_id: int = Query(...)
):
    return await MilestonesLogic.get(db=db, milestone_id=milestone_id)

@router.get("/milestones", tags=["milestones"])
async def get_all(
        db: AsyncSession = Depends(get_sql_db),
        service_id: int | None = Query(None, description="Filter by service_id"),
        request_id: int | None = Query(None, description="Filter by client_id"),
        proposal_id: int | None = Query(None, description="Filter by proposal_id"),
        order_id: int | None = Query(None, description="Filter by order_id"),
        milestone_status_id: int | None = Query(None,
                                            description="Filter by milestone_status_id (DRAFT = 0, IN_PROGRESS = 1, COMPLETED = 2)"),
        client_id: int | None = Query(None, description="Filter by client_id"),
        freelancer_id: int | None = Query(None, description="Filter by freelancer_id"),
        client_approved: int | None = Query(None, description="Filter by client_approved"),
        freelancer_approved: int | None = Query(None, description="Filter by freelancer_approved"),
        deleted: bool | None = Query(False, description="Filter by deleted")
):
    query_params: dict = {
        'milestone_status_id': milestone_status_id,
        'service_id': service_id,
        'request_id': request_id,
        'proposal_id': proposal_id,
        'order_id': order_id,
        "client_id": client_id,
        "freelancer_id": freelancer_id,
        "client_approved": client_approved,
        "freelancer_approved": freelancer_approved,
        "deleted": deleted,
    }
    return await MilestonesLogic.get_all(db=db, query_params=query_params)

@router.patch("/milestone", tags=["milestones"])
async def update_milestone(
        milestone_data: MilestoneRequest,
        milestone_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await MilestonesLogic.update(db=db, milestone_id=milestone_id, milestone_data=milestone_data)

@router.patch("/milestone/status", tags=["milestones"])
async def update_milestone_status(
        milestone_status_data: MilestoneApproveStatusRequest,
        milestone_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    if milestone_status_data.is_client == milestone_status_data.is_freelancer:
        raise HTTPException(status_code=400, detail="Please select a freelancer or client.")

    return await MilestonesLogic.update_status(db=db, milestone_id=milestone_id, milestone_status_data=milestone_status_data)

@router.post("/milestone", tags=["milestones"])
async def create(
        milestone_data: MilestoneRequest,
        proposal_id: int | None = Query(None),
        order_id: int | None = Query(None),
        service_id: int | None = Query(None),
        request_id: int | None = Query(None),
        db: AsyncSession = Depends(get_sql_db),
):
    ids_to_validate = {
        "proposal_id": proposal_id,
        "order_id": order_id,
        "service_id": service_id,
        "request_id": request_id,
    }
    populated_values = {key:value for key, value in ids_to_validate.items() if value is not None}
    if len(populated_values) != 1:
        raise HTTPException(
            status_code=400,
            detail="Exactly one of service_id, request_id, proposal_id, or order_id must be provided."
        )

    create_key, create_value = next(iter(populated_values.items()))
    return await MilestonesLogic.create(db=db, milestone_data=milestone_data, create_key=create_key, create_value=create_value)

@router.delete("/milestone", tags=["milestones"])
async def delete_milestone(
        milestone_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await MilestonesLogic.delete(db=db, milestone_id=milestone_id)