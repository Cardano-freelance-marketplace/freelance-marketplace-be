from datetime import datetime
from beanie import Document

class Notification(Document):
    user_id: int
    content: str
    creation_date: datetime
    is_notified: bool = False


    class Settings:
        collection = "notifications"