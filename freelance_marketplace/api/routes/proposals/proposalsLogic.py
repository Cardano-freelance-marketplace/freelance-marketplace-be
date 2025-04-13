from typing import Sequence
from fastapi import HTTPException
from sqlalchemy import update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from freelance_marketplace.api.utils.redis import Redis
from freelance_marketplace.api.utils.sql_util import build_transaction_query, soft_delete
from freelance_marketplace.models.sql.request_model.ProposalRequest import ProposalRequest
from freelance_marketplace.models.sql.sql_tables import Proposal


class ProposalsLogic:

    @staticmethod
    async def create(
            db : AsyncSession,
            proposal_data: ProposalRequest,
            request_id: int
    ) -> bool:
        try:
            await Proposal.create(db=db, request_id=request_id, **proposal_data.model_dump())
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def delete(
            db: AsyncSession,
            proposal_id: int
    )-> bool:
        try:
            result = await soft_delete(db=db, object=Proposal, attribute="proposal_id", object_id=proposal_id)
            if result.rowcount > 0:
                return True
            else:
                raise HTTPException(status_code=404, detail="Notification not found or already deleted")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def update(
            db: AsyncSession,
            proposal_id: int,
            proposal_data: ProposalRequest
    ) -> bool:
        try:
            stmt = (
                update(Proposal)
                .where(Proposal.proposal_id == proposal_id)
                .values(**proposal_data.model_dump())
                .execution_options(synchronize_session="fetch")
            )
            await db.execute(stmt)
            await db.commit()
            return True

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=f"{str(e)}")
    @staticmethod
    async def get(
            db: AsyncSession,
            proposal_id: int
    ) -> Proposal:
        try:
            cache_key = f"proposals:{proposal_id}"
            redis_data = await Redis.get_redis_data(cache_key)
            if redis_data:
                return redis_data

            result = await db.execute(
                select(Proposal)
                .where(Proposal.proposal_id == proposal_id)
            )
            proposal = result.scalars().first()
            if not proposal:
                raise HTTPException(status_code=404, detail=f"Proposal not found")

            await Redis.set_redis_data(cache_key, proposal)
            return proposal

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def get_all(
            db: AsyncSession,
            query_params: dict
    ) -> Sequence[Proposal]:
        try:
            transaction = await build_transaction_query(
                object=Proposal,
                query_params=query_params
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

        result = await db.execute(transaction)
        proposals = result.scalars().all()
        if not proposals:
            raise HTTPException(status_code=404, detail=f"proposals not found")
        return proposals

