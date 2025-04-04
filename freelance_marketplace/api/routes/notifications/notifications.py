from typing import Optional, Any, Coroutine

from fastapi import APIRouter, HTTPException, Query
from pymongo.results import DeleteResult

from freelance_marketplace.api.utils.data_manipulation_utils import get_object_id
from freelance_marketplace.db.no_sql.mongo import Mongo
from freelance_marketplace.models.no_sql.notification import Notification

router = APIRouter()

@router.post("/notification", tags=["notifications"])
async def create_notification(
        notification: Notification
  ) -> bool:
    await notification.create()
    return True


@router.get("/notification", tags=["notifications"])
async def get_notification(
        notification_id: str
      ) -> Notification:
    notification_result = await Notification.find_one(Notification.id == get_object_id(notification_id))
    return notification_result

@router.get("/user/notifications", tags=["notifications"])
async def get_notifications(
        is_notified: Optional[bool] = Query(None),
        user_id: Optional[str] = Query(None)
):
    query = {}
    if is_notified is not None:
        query["is_notified"] = is_notified
    if user_id is not None:
        query["user_id"] = user_id

    notifications = await Notification.find(query).to_list()
    return notifications


@router.patch("/notification", tags=["notifications"])
async def update_notification(
        notification: Notification,
        notification_id: str = Query(...)
      ) -> bool:
    notification_result = await Notification.find_one(Notification.id == get_object_id(notification_id))

    if not notification_result:
        raise HTTPException(status_code=404, detail="Notification not found")

    await Mongo.replace_item(notification_result, notification)
    return True

@router.delete("/notification", tags=["notifications"])
async def delete_notification(
        notification_id: str = Query(...)
) -> bool:
    result = await Notification.find(Notification.id == get_object_id(notification_id)).delete()
    if result.deleted_count > 0:
        return True
    else:
        raise HTTPException(status_code=404, detail="Notification not found or already deleted")