from datetime import datetime
from beanie import Document
from pydantic import Field

class Message(Document):
    message_id: int
    sender_id: int
    receiver_id: int
    content: str
    sent_time: datetime = Field(default_factory=datetime.utcnow)
    received_time: datetime = None
    is_edited: bool = False
    is_viewed: bool = False

    class Settings:
        collection = "messages"
