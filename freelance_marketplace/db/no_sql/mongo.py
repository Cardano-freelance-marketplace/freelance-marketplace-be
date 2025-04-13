from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from freelance_marketplace.core.config import settings
from freelance_marketplace.models.no_sql.conversation import Conversation
from freelance_marketplace.models.no_sql.notification import Notification
from freelance_marketplace.models.no_sql.portfolio import Portfolio
from freelance_marketplace.models.no_sql.wishlist import Wishlist


class Mongo:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.mongo.connection_string)
        self.database = self.client.get_database(settings.mongo.database_name)

    async def init_mongo(self):
        await init_beanie(database=self.database, document_models=[Wishlist, Notification, Portfolio, Conversation])

    @staticmethod
    async def replace_item(existing_item, new_item):
        new_item = new_item.dict(exclude_unset=True)
        for key, value in new_item.items():
            setattr(existing_item, key, value)
        await existing_item.save()

mongo_session = Mongo()