from pydantic import BaseModel

class RequestRequest(BaseModel):
    title: str
    description: str
    sub_category_id: int
    total_price: float
    tags: list[str]