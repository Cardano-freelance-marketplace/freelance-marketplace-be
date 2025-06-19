from typing import Optional
from pycardano import OgmiosChainContext, Address, UTxO, Transaction, TransactionBuilder
from freelance_marketplace.core.config import settings


class Ogmios:
    def __init__(self):
        self.context = OgmiosChainContext(settings.blockchain.ogmios_url)

    @staticmethod
    async def get_context():
        return OgmiosChainContext(settings.blockchain.ogmios_url)

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
        utxos = self.context.utxos(address=wallet_address)
        for utxo in utxos:
            lovelace_amount = sum(
                int(amt['quantity']) for amt in utxo['amount'] if amt['unit'] == 'lovelace'
            )
            has_only_ada = len(utxo['amount']) == 1 and utxo['amount'][0]['unit'] == 'lovelace'

            if has_only_ada and lovelace_amount >= 5_000_000:  # at least 5 ADA
                return utxo
        return None

    async def is_valid_transaction(self, tx: Transaction) -> bool:
        try:
            self.context.evaluate_tx(tx)
            return True
        except Exception as e:
            print(f"Transaction validation failed: {e}")
            return False