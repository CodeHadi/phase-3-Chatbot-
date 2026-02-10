from fastapi import Depends, HTTPException, Header, status
import jwt
from dotenv import load_dotenv
import os

load_dotenv()

SECRET = os.getenv("BETTER_AUTH_SECRET")

if not SECRET:
    raise ValueError("BETTER_AUTH_SECRET not found in .env")


async def get_current_user(authorization: str = Header(None)) -> str:
    """
    Extract and verify JWT token from Authorization header.
    Requires a valid Bearer token; raises 401 if missing or invalid.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )
    
    try:
        parts = authorization.split(" ")
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization format"
            )
        
        token = parts[1]
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return user_id
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )
