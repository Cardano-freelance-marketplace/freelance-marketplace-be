from pydantic import BaseModel


from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

# Enum Definitions for WalletType and UserType (You should replace these with actual values from your code)
class WalletType(str, Enum):
    TYPE_A = "type_a"
    TYPE_B = "type_b"

class UserType(str, Enum):
    ADMIN = "admin"
    USER = "user"

# Pydantic model for Profile (Nested model for when it exists)
class ProfileBase(BaseModel):
    profile_id: int
    first_name: str
    last_name: str
    bio: Optional[str] = None

    class Config:
        orm_mode = True

# Pydantic model for Skills (Nested model for when they exist)
class SkillBase(BaseModel):
    skill_id: int
    skill: str

    class Config:
        orm_mode = True

# Pydantic model for Role
class RoleBase(BaseModel):
    role_id: int
    role_name: str
    role_description: Optional[str] = None

    class Config:
        orm_mode = True

# Pydantic model for User (Main API Response)
class UserBase(BaseModel):
    user_id: int
    creation_date: datetime
    updated_at: Optional[datetime]
    is_active: bool
    wallet_public_address: str
    wallet_type: WalletType
    last_login: datetime
    user_type: UserType
    role: RoleBase  # User has a single Role
    profile: Optional[ProfileBase] = None  # Profile may not exist
    skills: Optional[List[SkillBase]] = []  # Skills may not exist

    class Config:
        orm_mode = True

# In case you need a model for creating users or for validation before inserting into the DB
class UserCreate(BaseModel):
    wallet_public_address: str
    wallet_type: WalletType
    user_type: UserType
    role_id: int  # Role will be assigned at creation

    class Config:
        orm_mode = True
