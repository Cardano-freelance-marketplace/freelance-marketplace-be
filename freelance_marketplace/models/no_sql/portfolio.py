from datetime import datetime
from typing import List
from beanie import Document
from pydantic import BaseModel

class File(BaseModel):
    file_storage_identifier: str
    file_type: str

class Projects(Document):
    images: List[File]
    attachments: List[File]
    project_title: str
    description: str
    start_date: datetime
    completion_date: datetime
    tech_stack: List[str]

class Portfolio(Document):
    user_id: int
    projects: List[Projects]

    class Settings:
        collection = "portfolios"