from typing import Optional

from pydantic import BaseModel

class UserRequest(BaseModel):
    wallet_public_address: str
    wallet_type_id: Optional[int] = None
