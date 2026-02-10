from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlmodel import Session, select
from backend.database import get_session
from backend.dependencies import get_current_user
from backend.models import Conversation, Message
from backend import agents
from backend.routes import mcp as mcp_routes

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


@router.post("/{user_id}/chat")
def chat_endpoint(user_id: str, payload: ChatRequest, current_user: str = Depends(get_current_user), session: Session = Depends(get_session)) -> Dict[str, Any]:
    # Verify caller matches token
    if user_id != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User mismatch")

    # Persist conversation if not exists
    conv = None
    if payload.conversation_id:
        conv = session.get(Conversation, payload.conversation_id)
        if not conv or conv.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    else:
        conv = Conversation(user_id=user_id, title=None)
        session.add(conv)
        session.commit()
        session.refresh(conv)

    # Save user message
    msg = Message(conversation_id=conv.id, role="user", content=payload.message)
    session.add(msg)
    session.commit()

    # Call agent to produce actions or reply
    result = agents.call_model_for_actions(payload.message)
    actions = result.get("actions", [])
    reply_text = result.get("reply") or ""

    # Execute actions sequentially and collect results
    action_results = []
    for action in actions:
        tool = action.get("tool")
        input_data = action.get("input") or {}
        try:
            if tool == "todo.add":
                # call mcp handler directly
                # build a simple object that has attributes matching MCPAddInput
                class PayloadObj:
                    def __init__(self, **kwargs):
                        for k, v in kwargs.items():
                            setattr(self, k, v)

                created = mcp_routes.mcp_todo_add(user_id=user_id, payload=PayloadObj(**input_data), current_user=user_id, session=session)
                action_results.append({"tool": tool, "result": created})
            elif tool == "todo.list":
                listed = mcp_routes.mcp_todo_list(user_id=user_id, current_user=user_id, session=session)
                action_results.append({"tool": tool, "result": listed})
            else:
                action_results.append({"tool": tool, "error": "tool not supported by agent runner"})
        except Exception as e:
            action_results.append({"tool": tool, "error": str(e)})

    # Save agent reply
    agent_msg = Message(conversation_id=conv.id, role="agent", content=reply_text, metadata_json=str(action_results))
    session.add(agent_msg)
    session.commit()

    return {"conversation_id": conv.id, "reply": reply_text, "actions": action_results}
