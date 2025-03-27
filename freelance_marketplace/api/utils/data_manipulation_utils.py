from bson import ObjectId
from fastapi import HTTPException


def get_object_id(id: str):
    try:
        return ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid notification ID format")