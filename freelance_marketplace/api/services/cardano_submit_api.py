from fastapi import HTTPException
from pycardano import Transaction
import requests
from freelance_marketplace.core.config import settings


class SubmitAPI:
    def __init__(self):
        self.submit_api_url = settings.blockchain.submit_api_url

    async def is_transaction_signed(self, tx: Transaction) -> bool:
        witnesses = tx.transaction_witness_set
        if not witnesses or not witnesses.vkey_witnesses:
            return False

        return len(witnesses.vkey_witnesses) > 0

    async def submit_transaction(self, tx: Transaction) -> bool:
        try:
            if not self.is_transaction_signed(tx=tx):
                raise HTTPException(500, "Transaction was not signed.")

            tx_bytes: bytes = tx.to_cbor()
            headers = {"content-type": "application/cbor"}
            response = requests.post(self.submit_api_url, data=tx_bytes, headers=headers)

            if response.status_code != 200:
                raise HTTPException(500, "Failed to submit transaction")
            else:
                return True
        except Exception as e:
            print(f"Failed to submit transaction: {e}")
            raise e
