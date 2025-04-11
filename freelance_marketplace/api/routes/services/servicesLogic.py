from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.models.enums.serviceStatus import ServiceStatus
from freelance_marketplace.models.sql.request_model.ServiceRequest import ServiceRequest
from freelance_marketplace.models.sql.sql_tables import Profiles, Services


class ServicesLogic:

    @staticmethod
    async def create(
            db : AsyncSession,
            freelancer_id: int,
            service_data: ServiceRequest
    ) -> bool:
        try:
            await Services.create(db=db, freelancer_id=freelancer_id, **service_data.model_dump())
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def delete(
            db: AsyncSession,
            service_id: int
    )-> bool:
        try:
            transaction = delete(Services).where(Services.service_id == service_id)
            await db.execute(transaction)
            await db.commit()
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def update(
            db: AsyncSession,
            service_id: int,
            service_data: ServiceRequest
    ) -> bool:
        try:
            stmt = (
                update(Services)
                .where(Services.service_id == service_id)
                .values(**service_data.model_dump())
                .execution_options(synchronize_session="fetch")
            )
            await db.execute(stmt)
            await db.commit()

            return True
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def change_status(
            db: AsyncSession,
            service_id: int,
            service_status: ServiceStatus
    ) -> bool:
        try:
            stmt = (
                update(Services)
                .where(Services.service_id == service_id)
                .values(service_status_id=service_status.value)
                .execution_options(synchronize_session="fetch")
            )
            await db.execute(stmt)
            await db.commit()

            return True
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def get_service(
            db: AsyncSession,
            service_id: int
    ) -> Services:
        try:
            result = await db.execute(select(Services).where(Services.service_id == service_id))
            service = result.scalars().first()
            if not service:
                raise HTTPException(status_code=204, detail=f"Service not found")
            return service

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def get_services(
            db: AsyncSession,
    ) -> Sequence[Services]:
        try:
            result = await db.execute(
                select(Services)
            )
            services = result.scalars().all()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

        if not services:
            raise HTTPException(status_code=204, detail=f"Services not found")
        return services


    @staticmethod
    async def get_user_services(
            db: AsyncSession,
            freelancer_id: int
    ) -> Sequence[Services]:
        try:
            result = await db.execute(
                select(Services)
                .where(Services.freelancer_id == freelancer_id)
            )
            services = result.scalars().all()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

        if not services:
            raise HTTPException(status_code=204, detail=f"Services not found")
        return services


    @staticmethod
    async def get_sub_category_services(
            db: AsyncSession,
            sub_category_id: int
    ) -> Sequence[Services]:
        try:
            result = await db.execute(
                select(Services)
                .where(Services.sub_category_id == sub_category_id)
            )
            services = result.scalars().all()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

        if not services:
            raise HTTPException(status_code=204, detail=f"Services not found")
        return services

