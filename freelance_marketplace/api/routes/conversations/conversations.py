from fastapi import APIRouter, HTTPException
from fastapi.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect

from freelance_marketplace.api.routes.conversations.conversationsLogic import ConversationsLogic
from freelance_marketplace.api.services.sockets import manager

router = APIRouter()

@router.websocket("/ws/message/{receiver_id}")
async def receive_message(
        websocket: WebSocket,
        receiver_id: int
):
    receiver_id = int(receiver_id)
    await manager.connect(receiver_id, websocket)

    try:
        while True:
            message = await websocket.receive_json()
            sender_id = message.get('sender_id')
            await ConversationsLogic.save_message(
                message=message,
                receiver_id=receiver_id,
                sender_id=sender_id
            )
            await ConversationsLogic.send_message(
                message=message,
                receiver_id=receiver_id,
            )
    except WebSocketDisconnect:
        manager.disconnect(receiver_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))