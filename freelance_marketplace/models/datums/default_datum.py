from pycardano import PlutusData, Address
from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class Milestone(PlutusData):
    CONSTR_ID = 0  # optional, used if your on-chain type uses constructor indexing
    reward: int
    approved_by_freelancer: int
    approved_by_client: int
    paid: int

@dataclass
class JobAgreement(PlutusData):
    CONSTR_ID = 0
    freelancer: bytes  # pubkey hash as bytes
    client: bytes
    milestone: Milestone


class MilestoneModel(BaseModel):
    reward: int
    approved_by_freelancer: int
    approved_by_client: int
    paid: int

class DatumModel(BaseModel):
    freelancer: Address
    client: Address
    milestone: MilestoneModel

    class Config:
        arbitrary_types_allowed = True  # For Pydantic v1