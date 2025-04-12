from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.routes.proposals.proposalsLogic import ProposalsLogic
from freelance_marketplace.db.sql.database import get_sql_db
from freelance_marketplace.models.sql.request_model.ProposalRequest import ProposalRequest

router = APIRouter()

@router.get("/proposal", tags=["proposals"])
async def get_proposal(
        db: AsyncSession = Depends(get_sql_db),
        proposal_id: int = Query(...)
):
    return await ProposalsLogic.get(db=db, proposal_id=proposal_id)

@router.get("/proposals", tags=["proposals"])
async def get_all_proposals(
        db: AsyncSession = Depends(get_sql_db),
        proposal_status_id: int | None = Query(None, description="Filter by proposal_status_id (CANCELED = 0, DRAFT = 1, PENDING = 2, ACCEPTED = 3, IN_PROGRESS = 4, COMPLETED = 5, DENIED_BY_FREELANCER = 6)"),
        request_id: int | None = Query(None, description="Filter by request_id"),
        freelancer_id: int | None = Query(None, description="Filter by freelancer_id"),
        deleted: bool | None = Query(False, description="Filter by deleted")
):
    query_params: dict = {
        'proposal_status_id': proposal_status_id,
        'request_id': request_id,
        "freelancer_id": freelancer_id,
        "deleted": deleted
    }
    return await ProposalsLogic.get_all(db=db, query_params=query_params)

@router.patch("/proposal", tags=["proposals"])
async def update_proposal(
        proposal_data: ProposalRequest,
        proposal_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await ProposalsLogic.update(db=db, proposal_id=proposal_id, proposal_data=proposal_data)

@router.post("/proposal", tags=["proposals"])
async def create_proposal(
        proposal_data: ProposalRequest,
        request_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await ProposalsLogic.create(db=db, proposal_data=proposal_data, request_id=request_id)

@router.delete("/proposal", tags=["proposals"])
async def delete_proposal(
        proposal_id: int = Query(...),
        db: AsyncSession = Depends(get_sql_db)
):
    return await ProposalsLogic.delete(db=db, proposal_id=proposal_id)