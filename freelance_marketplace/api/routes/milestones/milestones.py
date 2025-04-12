from typing import Sequence
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from freelance_marketplace.api.routes.milestones.milestonesLogic import MilestonesLogic
from freelance_marketplace.db.sql.database import get_sql_db
from freelance_marketplace.models.sql.request_model.MilestoneApproveStatusRequest import MilestoneApproveStatusRequest
from freelance_marketplace.models.sql.request_model.MilestoneRequest import MilestoneRequest
from freelance_marketplace.models.sql.sql_tables import Milestones

router = APIRouter()

@router.get("/milestone", tags=["milestones"])
async def get_milestone(
        db: AsyncSession = Depends(get_sql_db),
        milestone_id: int = Query(...)
):
    return await MilestonesLogic.get(db=db, milestone_id=milestone_id)

@router.get("/service/milestones", tags=["milestones"])
async def get_all_milestones_by_service(
        db: AsyncSession = Depends(get_sql_db),
        service_id: int = Query(...)
):
    return await MilestonesLogic.get_all_by_service(db=db, service_id=service_id)

@router.get("/request/milestones", tags=["milestones"])
async def get_all_milestones_by_request(
        db: AsyncSession = Depends(get_sql_db),
        request_id: int = Query(...)
):
    return await MilestonesLogic.get_all_by_request(db=db, request_id=request_id)

@router.get("/proposal/milestones", tags=["milestones"])
async def get_all_milestones_by_proposal(
        db: AsyncSession = Depends(get_sql_db),
        proposal_id: int = Query(...)
):
    return await MilestonesLogic.get_all_by_proposal(db=db, proposal_id=proposal_id)

@router.get("/order/milestones", tags=["milestones"])
async def get_all_milestones_by_order(
        db: AsyncSession = Depends(get_sql_db),
        order_id: int = Query(...)
):
    return await MilestonesLogic.get_all_by_order(db=db, order_id=order_id)

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

@router.post("/service/milestone", tags=["milestones"])
async def create_service_milestone(
        milestone_data: MilestoneRequest,
        service_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db),
):
    return await MilestonesLogic.create_by_service(db=db, milestone_data=milestone_data, service_id=service_id)

@router.post("/proposal/milestone", tags=["milestones"])
async def create_proposal_milestone(
        milestone_data: MilestoneRequest,
        proposal_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db),
):
    return await MilestonesLogic.create_by_proposal(db=db, milestone_data=milestone_data, proposal_id=proposal_id)

@router.post("/request/milestone", tags=["milestones"])
async def create_request_milestone(
        milestone_data: MilestoneRequest,
        request_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db),
):
    return await MilestonesLogic.create_by_request(db=db, milestone_data=milestone_data, request_id=request_id)

@router.post("/order/milestone", tags=["milestones"])
async def create_order_milestone(
        milestone_data: MilestoneRequest,
        order_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db),
):
    return await MilestonesLogic.create_by_order(db=db, milestone_data=milestone_data, order_id=order_id)

@router.delete("/milestone", tags=["milestones"])
async def delete_milestone(
        milestone_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await MilestonesLogic.delete(db=db, milestone_id=milestone_id)