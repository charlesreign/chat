from typing import Dict, Set, List
from app.models.chat import ChatType
import logging
import asyncio

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time chat."""
    
    def __init__(self):
        # chat_id -> dict of user_id -> websocket
        self.active_connections: Dict[int, Dict[int, object]] = {}
        # user_id -> set of active chat_ids
        self.user_chats: Dict[int, Set[int]] = {}
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    async def connect(self, chat_id: int, user_id: int, websocket):
        """Register a new WebSocket connection."""
        async with self._lock:
            if chat_id not in self.active_connections:
                self.active_connections[chat_id] = {}
            
            self.active_connections[chat_id][user_id] = websocket
            
            if user_id not in self.user_chats:
                self.user_chats[user_id] = set()
            self.user_chats[user_id].add(chat_id)
        
        logger.info(f"User {user_id} connected to chat {chat_id}")

    async def disconnect(self, chat_id: int, user_id: int, websocket):
        """Remove a WebSocket connection."""
        async with self._lock:
            if chat_id in self.active_connections:
                self.active_connections[chat_id].pop(user_id, None)
                
                if not self.active_connections[chat_id]:
                    del self.active_connections[chat_id]
            
            if user_id in self.user_chats:
                self.user_chats[user_id].discard(chat_id)
                if not self.user_chats[user_id]:
                    del self.user_chats[user_id]
        
        logger.info(f"User {user_id} disconnected from chat {chat_id}")

    async def broadcast(self, chat_id: int, message: dict):
        """Broadcast a message to all connections in a chat."""
        if chat_id not in self.active_connections:
            return
        
        disconnected_users = []
        for user_id, websocket in list(self.active_connections[chat_id].items()):
            try:
                # Check if connection is still open before sending
                if websocket.client_state.name == "CONNECTED":
                    await websocket.send_json(message)
            except Exception as e:
                logger.debug(f"Error sending message to user {user_id}: {e}")
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            async with self._lock:
                self.active_connections[chat_id].pop(user_id, None)

    async def send_personal(self, chat_id: int, user_id: int, message: dict):
        """Send a message to a specific user in a chat."""
        if chat_id not in self.active_connections:
            return
        
        websocket = self.active_connections[chat_id].get(user_id)
        if websocket:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending personal message to user {user_id}: {e}")

    def get_active_users(self, chat_id: int) -> List[int]:
        """Get list of active user IDs in a chat."""
        if chat_id in self.active_connections:
            return list(self.active_connections[chat_id].keys())
        return []


class ChatServiceManager:
    """Manages chat operations and state."""
    
    def __init__(self):
        self.chats: Dict[int, dict] = {}
        self.messages: Dict[int, List[dict]] = {}
        self.message_id_counter: Dict[int, int] = {}
        self._lock = asyncio.Lock()

    def create_chat(self, chat_id: int, chat_type: ChatType, members: List[int], name: str = None):
        """Create a new chat."""
        self.chats[chat_id] = {
            "id": chat_id,
            "type": chat_type,
            "members": set(members),
            "name": name,
            "created_at": None
        }
        self.messages[chat_id] = []
        self.message_id_counter[chat_id] = 0

    async def add_message(self, chat_id: int, message: dict):
        """Add a message to chat history."""
        async with self._lock:
            if chat_id in self.messages:
                self.messages[chat_id].append(message)

    def get_messages(self, chat_id: int, limit: int = 50) -> List[dict]:
        """Get recent messages from a chat."""
        if chat_id in self.messages:
            return self.messages[chat_id][-limit:]
        return []

    def get_chat_members(self, chat_id: int) -> Set[int]:
        """Get members of a chat."""
        if chat_id in self.chats:
            return self.chats[chat_id]["members"]
        return set()

    def add_member(self, chat_id: int, user_id: int):
        """Add a member to a chat."""
        if chat_id in self.chats:
            self.chats[chat_id]["members"].add(user_id)

    def remove_member(self, chat_id: int, user_id: int):
        """Remove a member from a chat."""
        if chat_id in self.chats:
            self.chats[chat_id]["members"].discard(user_id)

    def get_next_message_id(self, chat_id: int) -> int:
        """Get the next message ID for a chat."""
        if chat_id not in self.message_id_counter:
            self.message_id_counter[chat_id] = 0
        self.message_id_counter[chat_id] += 1
        return self.message_id_counter[chat_id]


# Global instances
connection_manager = ConnectionManager()
chat_service = ChatServiceManager()
