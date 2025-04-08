from datetime import datetime
from typing import List, Dict
from beanie import Document
from pydantic import BaseModel

class Attachment(BaseModel):
    file_name: str
    file_type: str
    file_data: str  # Base64 or encoded file data

# Model for images
class Image(BaseModel):
    image_name: str
    file_type: str
    file_data: str

class Portfolio(Document):
    user_id: int
    portfolio_id: int
    project_title: str
    description: str
    start_date: datetime
    completion_date: datetime
    tech_stack: List[str]
    attachments: List[Dict[str, str]]


    class Settings:
        collection = "portfolios"