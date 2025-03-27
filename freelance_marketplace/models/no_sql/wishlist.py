from datetime import datetime
from typing import List, Dict
from pydantic import BaseModel
from beanie import Document


class WishListItems(BaseModel):
    services: List[int]  # List of job IDs under "services"
    requests: List[int]  # List of job IDs under "requests"

class WishListData(BaseModel):
    creation_date: datetime
    description: str
    lists: Dict[str, WishListItems]


class Wishlist(Document):
    user_id: int
    lists: Dict[str, WishListData]

    class Settings:
        collection = "wishlists"
