from typing import Sequence
from fastapi import HTTPException
from sqlalchemy import delete, update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from freelance_marketplace.api.utils.redis import Redis
from freelance_marketplace.api.utils.sql_util import soft_delete, build_transaction_query
from freelance_marketplace.models.sql.request_model.MilestoneApproveStatusRequest import MilestoneApproveStatusRequest
from freelance_marketplace.models.sql.request_model.MilestoneRequest import MilestoneRequest
from freelance_marketplace.models.sql.sql_tables import Milestones


class MilestonesLogic:

    @staticmethod
    async def create(
            db : AsyncSession,
            milestone_data: MilestoneRequest,
            create_key: str,
            create_value: int,
    ) -> bool:
        try:
            await Milestones.create(db=db, **{create_key: create_value}, **milestone_data.model_dump())
            await Redis.invalidate_cache(prefix="milestones")
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def delete(
            db: AsyncSession,
            milestone_id: int
    )-> bool:
        try:
            result = await soft_delete(db=db, object=Milestones, attribute="milestone_id", object_id=milestone_id)
            if result.rowcount > 0:
                await Redis.invalidate_cache(prefix="milestones")
                return True
            else:
                raise HTTPException(status_code=404, detail="Notification not found or already deleted")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def update(
            db: AsyncSession,
            milestone_id: int,
            milestone_data: MilestoneRequest
    ) -> bool:
        try:
            stmt = (
                update(Milestones)
                .where(Milestones.milestone_id == milestone_id)
                .values(**milestone_data.model_dump())
                .execution_options(synchronize_session="fetch")
            )
            await db.execute(stmt)
            await db.commit()
            await Redis.invalidate_cache(prefix="milestones")
            return True

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def update_status(
            db: AsyncSession,
            milestone_id: int,
            milestone_status_data: MilestoneApproveStatusRequest
    ) -> bool:
        try:
            update_data = {}
            if milestone_status_data.is_client:
                update_data["client_approved"] = milestone_status_data.milestone_status
            if milestone_status_data.is_freelancer:
                update_data["freelancer_approved"] = milestone_status_data.milestone_status

            stmt = (
                update(Milestones)
                .where(Milestones.milestone_id == milestone_id)
                .values(**update_data)
                .execution_options(synchronize_session="fetch")
            )
            await db.execute(stmt)
            await db.commit()
            await Redis.invalidate_cache(prefix="milestones")

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
            milestone_id: int
    ) -> Milestones:
        redis_data, cache_key = await Redis.get_redis_data(match=f"milestones:{milestone_id}")
        if redis_data:
            return redis_data

        result = await db.execute(select(Milestones).where(Milestones.milestone_id == milestone_id))
        milestone = result.scalars().first()
        if not milestone:
            raise HTTPException(status_code=404, detail=f"milestone not found")
        await Redis.set_redis_data(cache_key, milestone)
        return milestone

    @staticmethod
    async def get_all(
            db: AsyncSession,
            query_params: dict
    ) -> Sequence[Milestones]:
        redis_data, cache_key = await Redis.get_redis_data(prefix="milestones", query_params=query_params)
        if redis_data:
            return redis_data

        transaction = await build_transaction_query(
            object=Milestones,
            query_params=query_params
        )
        result = await db.execute(transaction)
        milestones = result.scalars().all()
        if not milestones:
            raise HTTPException(status_code=404, detail=f"milestones not found")

        await Redis.set_redis_data(cache_key, data=milestones)
        return milestones