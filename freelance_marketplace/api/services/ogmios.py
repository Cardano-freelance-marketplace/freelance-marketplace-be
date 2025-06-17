from pycardano import OgmiosChainContext
from freelance_marketplace.core.config import settings


class Ogmios:

    def __init__(self):
        self.context = OgmiosChainContext(settings.blockchain.ogmios_url)

    @staticmethod
    async def get_context():
        return OgmiosChainContext(settings.blockchain.ogmios_url)