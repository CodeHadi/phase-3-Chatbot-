from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from backend.database import get_session
from backend.models import Task
from backend.dependencies import get_current_user
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

class CreateTaskRequest(BaseModel):
    title: str
    description: Optional[str] = None

class UpdateTaskRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


@router.get("/", response_model=List[Task])
def get_tasks(
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get all tasks for the current user"""
    tasks = session.exec(select(Task).where(Task.user_id == current_user)).all()
    return tasks


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: CreateTaskRequest,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new task for the current user"""
    task = Task(
        title=task_data.title,
        description=task_data.description,
        user_id=current_user,
        completed=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: str,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a specific task (only if it belongs to the current user)"""
    try:
        task_id = int(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: str,
    updated_task: UpdateTaskRequest,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update a specific task (only if it belongs to the current user)"""
    try:
        task_id = int(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if updated_task.title is not None:
        task.title = updated_task.title
    if updated_task.description is not None:
        task.description = updated_task.description
    if updated_task.completed is not None:
        task.completed = updated_task.completed
    
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a specific task (only if it belongs to the current user)"""
    try:
        task_id = int(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    session.delete(task)
    session.commit()


@router.patch("/{task_id}/complete", response_model=Task)
def complete_task(
    task_id: str,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Mark a task as complete (only if it belongs to the current user)"""
    try:
        task_id = int(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task.completed = True
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
