from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from freelance_marketplace.models.enums.userRole import UserRole
from freelance_marketplace.models.enums.userType import UserType
from freelance_marketplace.models.enums.walletType import WalletType

# Pydantic model for Profile (Nested model for when it exists)
class ProfileBase(BaseModel):
    profile_id: int
    first_name: str
    last_name: str
    bio: Optional[str] = None

# Pydantic model for Skills (Nested model for when they exist)
class SkillBase(BaseModel):
    skill_id: int
    skill: str

# Pydantic model for Role
class RoleBase(BaseModel):
    role_id: int
    role_name: str
    role_description: Optional[str] = None

# Pydantic model for User (Main API Response)
class UserModel(BaseModel):
    user_id: int
    creation_date: datetime
    updated_at: Optional[datetime]
    active: bool
    wallet_public_address: str
    wallet_type: WalletType
    last_login: datetime
    user_type: UserType
    role: UserRole
    profile: Optional[ProfileBase] = None
    skills: Optional[List[SkillBase]] = []

