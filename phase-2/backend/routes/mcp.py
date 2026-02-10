from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Any, Dict, List
from sqlmodel import Session, select
from backend.database import get_session
from backend.dependencies import get_current_user
from backend.models import Task

router = APIRouter(prefix="/api/mcp/{user_id}", tags=["mcp"])


class MCPAddInput(BaseModel):
    title: str
    description: Optional[str] = None


class MCPUpdateInput(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


@router.get("/manifest")
def manifest():
    """Return a simple MCP manifest agents can discover."""
    tools = [
        {
            "name": "todo.add",
            "description": "Create a new todo for the authenticated user",
            "endpoint": "/api/mcp/{user_id}/todo.add",
            "method": "POST",
        },
        {
            "name": "todo.list",
            "description": "List todos for the authenticated user",
            "endpoint": "/api/mcp/{user_id}/todo.list",
            "method": "GET",
        },
        {
            "name": "todo.complete",
            "description": "Mark a todo as completed",
            "endpoint": "/api/mcp/{user_id}/todo.complete/{id}",
            "method": "PUT",
        },
        {
            "name": "todo.update",
            "description": "Update fields on a todo",
            "endpoint": "/api/mcp/{user_id}/todo.update/{id}",
            "method": "PATCH",
        },
        {
            "name": "todo.delete",
            "description": "Delete a todo",
            "endpoint": "/api/mcp/{user_id}/todo.delete/{id}",
            "method": "DELETE",
        },
    ]
    return {"tools": tools}


@router.post("/todo.add")
def mcp_todo_add(user_id: str, payload: MCPAddInput, current_user: str = Depends(get_current_user), session: Session = Depends(get_session)):
    # Enforce that provided user_id matches token owner to keep server stateless
    if user_id != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User mismatch")

    task = Task(title=payload.title, description=payload.description, user_id=user_id, completed=False)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/todo.list")
def mcp_todo_list(user_id: str, current_user: str = Depends(get_current_user), session: Session = Depends(get_session)):
    if user_id != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User mismatch")

    tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
    return tasks


@router.put("/todo.complete/{task_id}")
def mcp_todo_complete(user_id: str, task_id: int, current_user: str = Depends(get_current_user), session: Session = Depends(get_session)):
    if user_id != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User mismatch")

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    task.completed = True
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.patch("/todo.update/{task_id}")
def mcp_todo_update(user_id: str, task_id: int, payload: MCPUpdateInput, current_user: str = Depends(get_current_user), session: Session = Depends(get_session)):
    if user_id != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User mismatch")

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.completed is not None:
        task.completed = payload.completed
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/todo.delete/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def mcp_todo_delete(user_id: str, task_id: int, current_user: str = Depends(get_current_user), session: Session = Depends(get_session)):
    if user_id != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User mismatch")

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"status": "ok"}
