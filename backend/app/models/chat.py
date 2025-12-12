from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ChatType(str, Enum):
    ONE_TO_ONE = "one_to_one"
    GROUP = "group"


class Chat(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    chat_type: ChatType
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatCreate(BaseModel):
    name: Optional[str] = None
    chat_type: ChatType
    member_ids: List[int]


class ChatMember(BaseModel):
    id: Optional[int] = None
    chat_id: int
    user_id: int
    joined_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    id: int
    name: Optional[str]
    chat_type: ChatType
    created_by: int
    created_at: datetime
    members: List[int]

    class Config:
        from_attributes = True
