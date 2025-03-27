from sqlalchemy import Enum

class UserType(Enum):
    Unknown = 0
    Freelancer = 1
    Client = 2
