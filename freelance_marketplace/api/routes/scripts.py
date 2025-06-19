from fastapi import APIRouter
from pycardano import Address, OgmiosChainContext, Network, TransactionBody, Transaction

from freelance_marketplace.api.services.cardano_submit_api import SubmitAPI
from freelance_marketplace.api.services.ogmios import Ogmios
from freelance_marketplace.api.services.transaction_builder import TransactionOrchestrator
from freelance_marketplace.api.utils.blockchain.key_utils import build_addr_from_vkey, get_vkey
from freelance_marketplace.core.config import settings
from freelance_marketplace.models.enums.transaction_types import TransactionTypes

router = APIRouter()

@router.get("/test", tags=["testing"])
async def test():
    # Connect to Ogmios (Make sure it's running locally)
    context = OgmiosChainContext(host=settings.ogmios.host, port=settings.ogmios.port, network=Network.TESTNET)
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

@router.get("/create_script", tags=["script"])
async def create_script():
    tx_builder: TransactionOrchestrator = TransactionOrchestrator()
    verification_key = await get_vkey()
    signer_address: Address = await build_addr_from_vkey(vkey=verification_key)
    client_address: Address = signer_address
    freelancer_address: Address = signer_address
    milestone_id: int = 0
    milestone: dict = {
        "milestone_id": milestone_id,
        "reward": 0,
        "approved_by_freelancer": 0,
        "approved_by_client": 0,
        "paid": 0,
    }
    unsigned_tx: TransactionBody = await tx_builder.build_unsigned_tx(
        signer_address=signer_address,
        client_address=client_address,
        freelancer_address=freelancer_address,
        milestone=milestone,
        milestone_id=milestone_id,
        transaction_type=TransactionTypes.locking_transaction
    )
    signed_tx: Transaction = await tx_builder.sign_tx(unsigned_tx)
    await Ogmios().submit_transaction(signed_tx)
