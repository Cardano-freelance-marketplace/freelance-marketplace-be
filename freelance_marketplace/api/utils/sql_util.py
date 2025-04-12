from typing import Any

from fastapi import HTTPException
from sqlalchemy import select, Select


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
