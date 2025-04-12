from typing import Sequence
from fastapi import HTTPException
from sqlalchemy import delete, update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from freelance_marketplace.models.enums.requestStatus import RequestStatus
from freelance_marketplace.models.sql.request_model.RequestRequest import RequestRequest
from freelance_marketplace.models.sql.sql_tables import Requests


class RequestsLogic:

    @staticmethod
    async def create(
            db : AsyncSession,
            client_id: int,
            request_data: RequestRequest
    ) -> bool:
        try:
            await Requests.create(db=db, client_id=client_id, **request_data.model_dump())
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def delete(
            db: AsyncSession,
            request_id: int
    )-> bool:
        try:
            transaction = delete(Requests).where(Requests.request_id == request_id)
            result = await db.execute(transaction)
            await db.commit()
            if result.rowcount > 0:
                return True
            else:
                raise HTTPException(status_code=404, detail="Request not found or already deleted")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def update(
            db: AsyncSession,
            request_id: int,
            request_data: RequestRequest
    ) -> bool:
        try:
            stmt = (
                update(Requests)
                .where(Requests.request_id == request_id)
                .values(**request_data.model_dump())
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
    async def change_status(
            db: AsyncSession,
            request_id: int,
            request_status: RequestStatus
    ) -> bool:
        try:
            stmt = (
                update(Requests)
                .where(Requests.request_id == request_id)
                .values(request_status_id=request_status.value)
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
    async def get_request(
            db: AsyncSession,
            request_id: int
    ) -> Requests:
        try:
            result = await db.execute(select(Requests).where(Requests.request_id == request_id))
            request = result.scalars().first()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

        if not request:
            raise HTTPException(status_code=404, detail=f"Service not found")
        return request


    @staticmethod
    async def get_requests(
            db: AsyncSession,
    ) -> Sequence[Requests]:
        try:
            result = await db.execute(
                select(Requests)
            )
            requests = result.scalars().all()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

        if not requests:
            raise HTTPException(status_code=404, detail=f"Requests not found")
        return requests


    @staticmethod
    async def get_user_requests(
            db: AsyncSession,
            client_id: int
    ) -> Sequence[Requests]:
        try:
            result = await db.execute(
                select(Requests)
                .where(Requests.client_id == client_id)
            )
            requests = result.scalars().all()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

        if not requests:
            raise HTTPException(status_code=404, detail=f"Requests not found")
        return requests


    @staticmethod
    async def get_sub_category_requests(
            db: AsyncSession,
            sub_category_id: int
    ) -> Sequence[Requests]:
        try:
            result = await db.execute(
                select(Requests)
                .where(Requests.sub_category_id == sub_category_id)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

        requests = result.scalars().all()
        if not requests:
            raise HTTPException(status_code=404, detail=f"Requests not found")
        return requests

