from enum import Enum

class RequestStatus(Enum):
    CANCELED = 0
    DRAFT = 1
    REQUESTING_FREELANCER = 2
    IN_PROGRESS = 3
    COMPLETED = 4
