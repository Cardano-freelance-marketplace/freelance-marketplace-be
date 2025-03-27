from sqlalchemy import Enum

class UserRole(Enum):
    Admin = 0
    User = 1
    Guest = 2
