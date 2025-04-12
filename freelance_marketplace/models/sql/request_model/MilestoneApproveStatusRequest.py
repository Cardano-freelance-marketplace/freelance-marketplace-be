from pydantic import BaseModel

class MilestoneApproveStatusRequest(BaseModel):
    milestone_status: bool
    is_client: bool
    is_freelancer: bool