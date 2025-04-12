from pydantic import BaseModel

class ReviewRequest(BaseModel):
    reviewee_id: int
    rating: float
    comment: str = None