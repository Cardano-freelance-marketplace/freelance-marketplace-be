from typing import List
from beanie import Document
from freelance_marketplace.models.no_sql.message import Message


class Conversation(Document):
    participants: List[int]
    messages: List[Message]

    class Settings:
        name = "conversations"