from pydantic import BaseModel

class MilestoneRequest(BaseModel):
    milestone_tx_hash: str
    client_id: int
    freelancer_id: int
    milestone_text: str
    reward_amount: float