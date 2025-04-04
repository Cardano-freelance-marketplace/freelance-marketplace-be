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