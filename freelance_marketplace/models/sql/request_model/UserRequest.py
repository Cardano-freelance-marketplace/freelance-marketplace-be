from pydantic import BaseModel

from freelance_marketplace.models.enums.walletType import WalletType


class UserRequest(BaseModel):
    wallet_public_address: str
    wallet_type: WalletType
