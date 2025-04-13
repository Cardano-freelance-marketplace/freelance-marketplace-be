from fastapi import APIRouter, HTTPException, Depends
from fastapi.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect

from freelance_marketplace.api.routes.conversations.conversationsLogic import ConversationsLogic
from freelance_marketplace.api.services.sockets import manager

router = APIRouter()

@router.websocket("/ws/message/{connected_user_id}")
async def message(
        websocket: WebSocket,
        connected_user_id: int
):
    connected_user_id = int(connected_user_id)
    await manager.connect(connected_user_id, websocket)

    try:
        while True:
            message = await websocket.receive_json()
            receiver_id = message.get("receiver_id")
            await ConversationsLogic.save_message(
                message=message,
                sender_id=connected_user_id,
                receiver_id=receiver_id
            )
            await ConversationsLogic.send_message(
                message=message,
                receiver_id=receiver_id,
            )
    except WebSocketDisconnect:
        manager.disconnect(connected_user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{with_user_id}")
async def get_conversation(
        with_user_id: int,
        # current_user_id: int = Depends(get_current_user_id)
):
    ## TODO IMPLEMENT GET USER_ID FROM TOKEN WHEN TOKEN IS IMPLEMENTED

    """
    Returns all messages between the current user and the target user.
    """
    current_user_id = 1
    return await ConversationsLogic.get_conversation_history(
        user1=current_user_id,
        user2=with_user_id
    )

@router.get("/conversations")
async def list_conversations(
        # current_user_id: int = Depends(get_current_user_id)
):
    ## TODO IMPLEMENT GET USER_ID FROM TOKEN WHEN TOKEN IS IMPLEMENTED

    """
    Returns a list of conversations the user is involved in.
    """
    current_user_id = 1
    return await ConversationsLogic.list_user_conversations(
        user_id=current_user_id
    )

@router.post("/conversations/{with_user_id}/mark_viewed")
async def mark_viewed(
        with_user_id: int,
        # current_user_id: int = Depends(get_current_user_id)
):
    ## TODO IMPLEMENT GET USER_ID FROM TOKEN WHEN TOKEN IS IMPLEMENTED
    """
    Marks all messages between these users as viewed.
    """
    current_user_id = 1
    await ConversationsLogic.mark_messages_as_viewed(current_user_id, with_user_id)