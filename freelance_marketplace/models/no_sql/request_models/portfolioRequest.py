from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel

class OptionalAttachment(BaseModel):
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    file_data: Optional[str] = None  # Base64 or encoded file data

class OptionalImage(BaseModel):
    image_name: Optional[str] = None
    file_type: Optional[str] = None
    file_data: Optional[str] = None

class PortfolioRequest(BaseModel):
    user_id: Optional[int] = None
    portfolio_id: Optional[int] = None
    project_title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    tech_stack: Optional[List[str]] = None
    attachments: Optional[List[Dict[str, str]]] = None  # or use Optional[List[OptionalAttachment]] if strongly typed
