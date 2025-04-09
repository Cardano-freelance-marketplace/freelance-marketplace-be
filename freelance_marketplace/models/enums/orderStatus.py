from enum import Enum

class OrderStatus(Enum):
    CANCELED = 0
    DRAFT = 1
    PENDING = 2
    ACCEPTED = 3
    IN_PROGRESS = 4
    COMPLETED = 5
    DENIED_BY_FREELANCER = 6
