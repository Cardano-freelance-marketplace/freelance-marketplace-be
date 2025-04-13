from typing import Any

from fastapi import HTTPException
from sqlalchemy import select, Select, update, Result, CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from freelance_marketplace.models.sql.sql_tables import Order, Proposal, Requests, Services
from freelance_marketplace.models.enums.orderStatus import OrderStatus as OrderStatusEnum


async def build_transaction_query(object, query_params: dict) ->  Select[tuple[Any]] | Select:
    try:
        transaction = select(object)
        for key, value in query_params.items():
            if value is None:
                continue
            column_attr = getattr(object, key, None)
            if column_attr is None:
                continue

            if isinstance(value, str):
                transaction = transaction.where(column_attr == value.lower())
            else:
                transaction = transaction.where(column_attr == value)
        return transaction
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def soft_delete(
        object,
        attribute: str,
        object_id: int,
        db: AsyncSession
) -> Result | CursorResult:

    object_id_column_attr = getattr(object, attribute, None)
    if object_id_column_attr is None:
        raise ValueError(f"Object does not have attribute {attribute}")

    status_id = f"{attribute.split('_')[0]}_status_id"
    status_id_column_attr = getattr(object, status_id, None)
    if status_id_column_attr is None:
        raise ValueError(f"Object does not have status attribute {status_id}")

    stmt = (
        update(object)
        .where(object_id_column_attr == object_id)
        .values(deleted=True)
    )

    if issubclass(object, (Order, Proposal, Requests, Services)):
        stmt = stmt.values({status_id_column_attr.key: OrderStatusEnum.CANCELED.value})
    result = await db.execute(stmt)
    await db.commit()
    return result
