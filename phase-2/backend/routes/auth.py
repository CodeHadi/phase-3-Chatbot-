from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
import jwt
import os
from datetime import datetime, timedelta
from typing import Dict, Any
import hashlib
import secrets

from sqlmodel import Session
from backend.database import get_session
from backend.models import User
from passlib.context import CryptContext

router = APIRouter(prefix="/api/auth", tags=["auth"])

SECRET = os.getenv("BETTER_AUTH_SECRET", "your-secret-key")

# Use argon2 instead of bcrypt (no 72 char limit)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class SignUpRequest(BaseModel):
    email: str
    password: str


class SignInRequest(BaseModel):
    email: str
    password: str


def get_password_hash(password: str) -> str:
    """Hash password using argon2 (no 72-char limit like bcrypt)"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password hashing failed: {str(e)}"
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_jwt_token(user_id: str, expires_delta: timedelta = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(days=7)
    expire = datetime.utcnow() + expires_delta
    payload = {"sub": user_id, "exp": expire, "iat": datetime.utcnow()}
    token = jwt.encode(payload, SECRET, algorithm="HS256")
    return token


@router.post("/sign-up")
def sign_up(data: SignUpRequest, session: Session = Depends(get_session)) -> Dict[str, Any]:
    existing = session.get(User, data.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(email=data.email, password_hash=get_password_hash(data.password))
    session.add(user)
    session.commit()
    session.refresh(user)

    token = create_jwt_token(user.email)
    return {"user": {"email": user.email, "id": user.email}, "token": token, "session": {"token": token, "user": {"email": user.email, "id": user.email}}}


@router.post("/sign-in")
def sign_in(data: SignInRequest, session: Session = Depends(get_session)) -> Dict[str, Any]:
    user = session.get(User, data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_jwt_token(user.email)
    return {"user": {"email": user.email, "id": user.email}, "token": token, "session": {"token": token, "user": {"email": user.email, "id": user.email}}}


@router.post("/sign-out")
def sign_out():
    return {"message": "Signed out successfully"}


@router.get("/session")
def get_session_route(authorization: str = None) -> Dict[str, Any]:
    if not authorization:
        return {"session": None}

    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            return {"session": None}

        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        return {"session": {"token": token, "user": {"email": user_id, "id": user_id}}}
    except Exception:
        return {"session": None}
