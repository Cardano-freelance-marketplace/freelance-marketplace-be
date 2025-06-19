from typing import Optional, List
from pycardano import OgmiosChainContext, Address, UTxO, Transaction
from freelance_marketplace.core.config import settings


class Ogmios:
    def __init__(self):
        self.context = OgmiosChainContext(host=settings.ogmios.host, port=settings.ogmios.port, network=settings.blockchain.network)

    @staticmethod
    async def get_context():
        return OgmiosChainContext(host=settings.ogmios.host, port=settings.ogmios.port, network=settings.blockchain.network)

    async def get_utxo_from_wallet(self, signer_address: Address):
        utxos: List[UTxO] = self.context.utxos(address=signer_address)
        min_lovelace = 5_000_000
        for utxo in utxos:
            ada_amount = utxo.output.amount.coin
            if ada_amount >= min_lovelace:
                return utxo
        return None

    async def get_utxo_by_milestone(self, milestone_id: int, script_address: Address) -> Optional[UTxO]:
        # Fetch UTXOs at the validator address
        utxos = self.context.utxos(str(script_address))

        for utxo in utxos:
            datum = utxo.output.datum
            if datum is not None:
                try:
                    # Check if datum has the milestone_id field
                    if hasattr(datum, "milestone_id") and datum.milestone_id == milestone_id:
                        return utxo
                except Exception as e:
                    continue  # Some datums might be malformed or not PlutusData instances

        return None

    async def get_collateral_utxo(self, wallet_address: Address) -> Optional[UTxO]:
        utxos: list[UTxO] = self.context.utxos(address=wallet_address)

        for utxo in utxos:
            value = utxo.output.amount

            has_only_ada = not value.multi_asset or len(value.multi_asset) == 0
            has_min_ada = value.coin >= 5_000_000  # 5 ADA in lovelace

            if has_only_ada and has_min_ada:
                return utxo

        return None

    async def is_valid_transaction(self, tx: Transaction) -> bool:
        try:
            self.context.evaluate_tx(tx)
            return True
        except Exception as e:
            print(f"Transaction validation failed: {e}")
            return False

    async def submit_transaction(self, tx: Transaction) -> bool:
        self.context.submit_tx(tx.to_cbor())
        return True

