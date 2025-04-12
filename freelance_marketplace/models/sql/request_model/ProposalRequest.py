from pydantic import BaseModel


class ProposalRequest(BaseModel):
    freelancer_id: int