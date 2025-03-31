from enum import Enum

class JobStatus(Enum):
    Pending_Approval = 0
    Approved = 1
    Draft = 2
    In_Progress = 3
    Completed = 4
    Canceled = 5