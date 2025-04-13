from datetime import datetime
from typing import Optional
from beanie import Document

class Message(Document):
    sender_id: int
    receiver_id: int
    content: str
    sent_time: datetime
    received_time: Optional[datetime] = None
    is_delivered: bool = False
    is_edited: bool = False
    is_viewed: bool = False

    class Settings:
        collection = "messages"
