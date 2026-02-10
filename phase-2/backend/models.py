from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """Simple user model using email as primary key for quick prototyping."""
    email: str = Field(primary_key=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )


class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: Optional[int] = Field(default=None, foreign_key="conversation.id", index=True)
    role: str  # 'user' | 'agent' | 'system'
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata_json: Optional[str] = None
