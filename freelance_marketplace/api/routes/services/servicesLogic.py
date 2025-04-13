from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.api.services.redis import Redis
from freelance_marketplace.api.utils.sql_util import soft_delete, build_transaction_query
from freelance_marketplace.models.enums.serviceStatus import ServiceStatus
from freelance_marketplace.models.sql.request_model.ServiceRequest import ServiceRequest
from freelance_marketplace.models.sql.sql_tables import Services


class ServicesLogic:

    @staticmethod
    async def create(
            db : AsyncSession,
            freelancer_id: int,
            service_data: ServiceRequest
    ) -> bool:
        try:
            await Services.create(db=db, freelancer_id=freelancer_id, **service_data.model_dump())
            await Redis.invalidate_cache("services")
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")


    @staticmethod
    async def delete(
            db: AsyncSession,
            service_id: int
    )-> bool:
        result = await soft_delete(db=db, object=Services, attribute="service_id", object_id=service_id)
        if result.rowcount > 0:
            await Redis.invalidate_cache("services")
            return True
        else:
            raise HTTPException(status_code=404, detail="Service not found or already deleted")


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
            await Redis.invalidate_cache("services")
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
            await Redis.invalidate_cache("services")
            return True

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=f"{str(e)}")

    @staticmethod
    async def get_service(
            db: AsyncSession,
            service_id: int
    ) -> Services:
        redis_data, cache_key = await Redis.get_redis_data(match=f"services:{service_id}")
        if redis_data:
            return redis_data

        result = await db.execute(select(Services).where(Services.service_id == service_id))
        service = result.scalars().first()
        if not service:
            raise HTTPException(status_code=404, detail=f"Service not found")
        return service

    @staticmethod
    async def get_services(
            db: AsyncSession,
            query_params: dict
    ) -> Sequence[Services]:
        redis_data, cache_key = await Redis.get_redis_data(prefix="services", query_params=query_params)
        if redis_data:
            return redis_data

        transaction = await build_transaction_query(
            object=Services,
            query_params=query_params
        )

        result = await db.execute(transaction)
        services = result.scalars().all()

        if not services:
            raise HTTPException(status_code=404, detail=f"Services not found")
        await Redis.set_redis_data(cache_key=cache_key, data=services)
        return services


    @staticmethod
    async def get_user_services(
            db: AsyncSession,
            freelancer_id: int
    ) -> Sequence[Services]:
        result = await db.execute(
            select(Services)
            .where(Services.freelancer_id == freelancer_id)
        )
        services = result.scalars().all()

        if not services:
            raise HTTPException(status_code=404, detail=f"Services not found")
        return services


    @staticmethod
    async def get_sub_category_services(
            db: AsyncSession,
            sub_category_id: int
    ) -> Sequence[Services]:
        result = await db.execute(
            select(Services)
            .where(Services.sub_category_id == sub_category_id)
        )
        services = result.scalars().all()

        if not services:
            raise HTTPException(status_code=404, detail=f"Services not found")
        return services

