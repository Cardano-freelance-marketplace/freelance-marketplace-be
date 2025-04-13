from fastapi import HTTPException
from starlette.websockets import WebSocket

from freelance_marketplace.api.services.sockets import manager
from freelance_marketplace.models.no_sql.conversation import Conversation
from freelance_marketplace.models.no_sql.message import Message


class ConversationsLogic:

    @classmethod
    async def save_message(
            cls,
            message: Message,
            receiver_id: int,
            sender_id: int
    ):
        participants = sorted([sender_id, receiver_id])
        conversation = await Conversation.find_one(
            {"participants": {"$all": participants}}
        )
        if conversation:
            # Add the new message to the existing conversation
            conversation.messages.append(message)
            await conversation.save()
        else:
            # Create a new conversation document
            conversation = Conversation(
                participants=participants,
                messages=[message]
            )
            await conversation.insert()

    @classmethod
    async def send_message(
            cls,
            message: Message,
            receiver_id: int
    ):
        message_dict = message.model_dump()
        await manager.send_object(receiver_id, message_dict)

    @classmethod
    async def get_conversation_history(
            cls,
            user1: int,
            user2: int,
    ):
        raise HTTPException(status_code=404, detail="Not implemented")
        ## TODO IMPLEMENT LATER WHEN FRONTEND IS BUILT

    @classmethod
    async def list_user_conversations(
            cls,
            user_id: int
    ):
        raise HTTPException(status_code=404, detail="Not implemented")
        ## TODO IMPLEMENT LATER WHEN FRONTEND IS BUILT

    @classmethod
    async def mark_messages_as_viewed(
            cls,
            with_user_id: int,
            current_user_id: int,
    ):
        raise HTTPException(status_code=404, detail="Not implemented")
        ## TODO IMPLEMENT LATER WHEN FRONTEND IS BUILT

