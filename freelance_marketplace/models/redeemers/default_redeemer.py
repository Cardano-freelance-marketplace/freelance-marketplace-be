from pycardano import PlutusData

class Redeemer(PlutusData):
    CONSTR_ID = 0  # Constructor index for Redeemer type in your contract
    signer: bytes
    action: ConstrPlutusData  # nested Action enum
    is_client: bool
    is_freelancer: bool

class Action(PlutusData):
    # Map your Action constructors indexes, e.g.,
    APPROVE_MILESTONE = 0
    REDEEM_MILESTONE = 1
    REFUND = 2

    CONSTR_ID: int

    def __init__(self, constr_id):
        self.CONSTR_ID = constr_id