from sqlalchemy import Enum

class WalletType(Enum):
    Lace = 0
    Yoroi = 1
    Daedalus = 2
    Nami = 3
    Flint = 4
    WalletConnect = 5
    Exodus = 6
    AdaLite = 7
    CardanoWalletConnect = 8
    TrustWallet = 9
    Typhon = 10
    Blockfrost = 11
    GeroWallet = 12


