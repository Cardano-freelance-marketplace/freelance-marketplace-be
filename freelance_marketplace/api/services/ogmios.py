from pycardano import OgmiosChainContext, Address
from freelance_marketplace.core.config import settings


class Ogmios:

    def __init__(self):
        self.context = OgmiosChainContext(settings.blockchain.ogmios_url)

    @staticmethod
    async def get_context():
        return OgmiosChainContext(settings.blockchain.ogmios_url)


    async def get_utxo_by_milestone(self, milestone_id: int, script_address: Address):
        utxos = self.context.utxos(address=script_address)
        utxo = map((lambda utxo: utxo.milestone_id == milestone_id), utxos)
        return utxo