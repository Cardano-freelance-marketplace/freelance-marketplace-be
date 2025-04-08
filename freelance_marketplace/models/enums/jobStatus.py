from enum import Enum

class JobStatus(Enum):
    PENDING_APPROVAL = 0
    APPROVED = 1
    DRAFT = 2
    IN_PROGRESS = 3
    COMPLETED = 4
    CANCELED = 5