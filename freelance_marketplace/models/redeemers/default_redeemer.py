from pycardano import PlutusData
from dataclasses import dataclass

@dataclass
class ApproveMilestone(PlutusData):
    CONSTR_ID = 0

@dataclass
class RedeemMilestone(PlutusData):
    CONSTR_ID = 1

@dataclass
class Refund(PlutusData):
    CONSTR_ID = 2

# Union type for Action
Action = ApproveMilestone | RedeemMilestone | Refund


@dataclass
class DefaultRedeemer(PlutusData):
    CONSTR_ID = 0
    signer: bytes
    action: Action
    is_client: int
    is_freelancer: int