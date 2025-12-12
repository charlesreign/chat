from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect
from typing import List
from app.models.chat import ChatCreate, ChatResponse, ChatType
from app.services.chat_service import connection_manager, chat_service
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chats", tags=["chats"])

# In-memory chat storage
chats_db = {}
chat_members_db = {}
chat_id_counter = 1


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(chat: ChatCreate, current_user_id: int = 1):
    """Create a new chat (one-on-one or group)."""
    global chat_id_counter
    
    # Validate members
    if chat.chat_type == ChatType.ONE_TO_ONE:
        if len(chat.member_ids) != 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One-on-one chat must have exactly 2 members"
            )
        if current_user_id not in chat.member_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current user must be a member of the chat"
            )
    else:  # GROUP
        if current_user_id not in chat.member_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current user must be a member of the chat"
            )
        if len(chat.member_ids) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group chat must have at least 2 members"
            )
    
    chat_id = chat_id_counter
    chat_id_counter += 1
    
    chats_db[chat_id] = {
        "id": chat_id,
        "name": chat.name,
        "chat_type": chat.chat_type,
        "created_by": current_user_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    chat_members_db[chat_id] = set(chat.member_ids)
    
    # Initialize chat service
    chat_service.create_chat(chat_id, chat.chat_type, chat.member_ids, chat.name)
    
    return {
        "id": chat_id,
        "name": chat.name,
        "chat_type": chat.chat_type,
        "created_by": current_user_id,
        "created_at": chats_db[chat_id]["created_at"],
        "members": list(chat_members_db[chat_id])
    }


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(chat_id: int):
    """Get chat details."""
    if chat_id not in chats_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    chat = chats_db[chat_id]
    return {
        "id": chat_id,
        "name": chat["name"],
        "chat_type": chat["chat_type"],
        "created_by": chat["created_by"],
        "created_at": chat["created_at"],
        "members": list(chat_members_db.get(chat_id, set()))
    }


@router.get("/user/{user_id}")
async def get_user_chats(user_id: int):
    """Get all chats for a specific user."""
    user_chats = []
    for chat_id, members in chat_members_db.items():
        if user_id in members:
            chat = chats_db.get(chat_id)
            if chat:
                user_chats.append({
                    "id": chat_id,
                    "name": chat["name"],
                    "chat_type": chat["chat_type"],
                    "created_by": chat["created_by"],
                    "created_at": chat["created_at"],
                    "members": list(members)
                })
    return user_chats


@router.get("/{chat_id}/messages")
async def get_chat_messages(chat_id: int, limit: int = 50):
    """Get chat message history."""
    if chat_id not in chats_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    messages = chat_service.get_messages(chat_id, limit)
    return messages


@router.get("/{chat_id}/active-users")
async def get_active_users(chat_id: int):
    """Get list of active users in a chat."""
    if chat_id not in chats_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    active_users = connection_manager.get_active_users(chat_id)
    return {"chat_id": chat_id, "active_users": active_users}


@router.websocket("/ws/{chat_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int, user_id: int):
    """WebSocket endpoint for real-time chat."""
    
    if chat_id not in chats_db:
        await websocket.close(code=4004, reason="Chat not found")
        return
    
    if user_id not in chat_members_db.get(chat_id, set()):
        await websocket.close(code=4003, reason="User not a member of this chat")
        return
    
    try:
        await websocket.accept()
        await connection_manager.connect(chat_id, user_id, websocket)
        logger.info(f"WebSocket connected for user {user_id} in chat {chat_id}")
        
        # Notify others that user is online
        active_users = connection_manager.get_active_users(chat_id)
        await connection_manager.broadcast(chat_id, {
            "type": "user_online",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "active_users": active_users
        })
        
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Validate message content
                content = message_data.get("content", "").strip()
                if not content:
                    continue
                
                # Generate unique message ID
                message_id = chat_service.get_next_message_id(chat_id)
                
                # Store message
                message = {
                    "id": message_id,
                    "chat_id": chat_id,
                    "sender_id": user_id,
                    "content": content,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                await chat_service.add_message(chat_id, message)
                logger.info(f"Message {message_id} added to chat {chat_id}")
                
                # Broadcast message to all connected users
                await connection_manager.broadcast(chat_id, {
                    "type": "message",
                    **message
                })
            
            except json.JSONDecodeError:
                logger.error("Invalid JSON received")
                try:
                    if websocket.client_state.name == "CONNECTED":
                        await websocket.send_json({
                            "type": "error",
                            "message": "Invalid message format"
                        })
                except Exception as send_err:
                    logger.debug(f"Could not send error response: {send_err}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                try:
                    if websocket.client_state.name == "CONNECTED":
                        await websocket.send_json({
                            "type": "error",
                            "message": "Error processing message"
                        })
                except Exception as send_err:
                    logger.debug(f"Could not send error response: {send_err}")
                return
    
    except WebSocketDisconnect:
        await connection_manager.disconnect(chat_id, user_id, websocket)
        logger.info(f"WebSocket disconnected for user {user_id} in chat {chat_id}")
        
        # Notify others that user is offline (only if there are other connections)
        active_users = connection_manager.get_active_users(chat_id)
        if active_users:  # Only broadcast if there are other users connected
            await connection_manager.broadcast(chat_id, {
                "type": "user_offline",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "active_users": active_users
            })
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await connection_manager.disconnect(chat_id, user_id, websocket)
        except Exception as cleanup_err:
            logger.debug(f"Error during cleanup: {cleanup_err}")
