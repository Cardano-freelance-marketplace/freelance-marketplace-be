from typing import Optional
from pydantic import BaseModel


class ProfileRequest(BaseModel):
    bio: Optional[str]
    last_name: str
    first_name: str