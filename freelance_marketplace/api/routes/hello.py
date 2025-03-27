from bson import ObjectId
from fastapi import APIRouter, Form, HTTPException
from pycardano import Address, OgmiosChainContext, Network

from freelance_marketplace.api.utils.data_manipulation_utils import get_object_id
from freelance_marketplace.core.config import settings
from freelance_marketplace.db.no_sql.mongo import Mongo
from freelance_marketplace.models.no_sql.notification import Notification

router = APIRouter()

@router.get("/test", tags=["testing"])
async def test():
    # Connect to Ogmios (Make sure it's running locally)
    context = OgmiosChainContext(host="localhost", port=1337, network=Network.TESTNET)
    public_address = settings.test.addr

    try:
        addr_obj = Address.from_primitive(public_address)
    except Exception as e:
        print("Invalid address:", e)
        raise e

    try:
        utxos = context.utxos(addr_obj)
        
        if utxos:
            print(f"UTXOs for {public_address}:")
            for utxo in utxos:
                print(f"TxHash: {utxo.input.transaction_id}, Amount: {utxo.output.amount}")
        else:
            return "No UTXOs found for this address."

    except Exception as e:
        print(f"Error fetching UTXOs: {e}")

@router.post("/notification", tags=["testing"])
async def create_notification(
        notification: Notification
      ):
    await notification.create()


@router.get("/notification", tags=["testing"])
async def get_notification(
        notification_id: str
      ):
    notification_result = await Notification.find_one(Notification.id == get_object_id(notification_id))
    return notification_result


@router.patch("/notification", tags=["testing"])
async def update_notification(
        notification_id: str,
        notification: Notification
      ):
    notification_result = await Notification.find_one(Notification.id == get_object_id(notification_id))

    if not notification_result:
        raise HTTPException(status_code=404, detail="Notification not found")

    await Mongo.replace_item(notification_result, notification)
    return True