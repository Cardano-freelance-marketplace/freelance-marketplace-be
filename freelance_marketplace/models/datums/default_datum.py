from pycardano import PlutusData
from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class Milestone(PlutusData):
    CONSTR_ID = 0  # optional, used if your on-chain type uses constructor indexing
    reward: int
    approved_by_freelancer: bool
    approved_by_client: bool
    paid: bool

@dataclass
class JobAgreement(PlutusData):
    CONSTR_ID = 0
    freelancer: bytes  # pubkey hash as bytes
    client: bytes
    milestone: Milestone


class MilestoneModel(BaseModel):
    reward: int
    approved_by_freelancer: bool
    approved_by_client: bool
    paid: bool

class DatumModel(BaseModel):
    freelancer: str  # hex string
    client: str      # hex string
    milestone: MilestoneModel