"""
Authentication module for FastAPI application.
Handles JWT token validation and user context management.
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import json
from pathlib import Path

# JWT Configuration
SECRET_KEY = "django-insecure-_y@ihlpikbig^bbjn&q@85%x9mo(y3$b@kq$urdhny4s!li45p"  # Same as Django
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security scheme
security = HTTPBearer()

# In-memory storage for user contexts (replace with Redis in production)
user_contexts: Dict[str, Dict[str, Any]] = {}

class UserContext:
    """User context for managing conversation state"""
    def __init__(self, user_id: str, username: str, email: str):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.current_chat_id: Optional[str] = None
        self.current_document_id: Optional[str] = None
        self.conversation_history: list = []
        self.created_at = datetime.now()

def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token and return payload.
    Uses the same secret key as Django backend.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserContext:
    """
    FastAPI dependency to get current authenticated user.
    Validates JWT token and returns user context.
    """
    token = credentials.credentials
    payload = verify_jwt_token(token)
    
    user_id = payload.get("user_id") or payload.get("user")  # SimpleJWT default is 'user_id'
    # Username/email may be absent depending on how the token was issued
    username = payload.get("username") or (f"user-{user_id}" if user_id else None)
    email = payload.get("email")

    # Only require a resolvable user_id; other fields are optional
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get or create user context
    if user_id not in user_contexts:
        user_contexts[user_id] = UserContext(user_id, username, email)
    
    return user_contexts[user_id]

def get_user_context(user_id: str) -> Optional[UserContext]:
    """Get user context by user ID"""
    return user_contexts.get(user_id)

def update_user_context(user_id: str, **kwargs) -> bool:
    """Update user context with new values"""
    if user_id in user_contexts:
        context = user_contexts[user_id]
        for key, value in kwargs.items():
            if hasattr(context, key):
                setattr(context, key, value)
        return True
    return False

def save_user_conversation(user_id: str, chat_id: str, message: str, response: str):
    """Save conversation message to user context"""
    if user_id in user_contexts:
        context = user_contexts[user_id]
        context.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "chat_id": chat_id,
            "message": message,
            "response": response
        })

def get_user_conversation_history(user_id: str, chat_id: Optional[str] = None) -> list:
    """Get user's conversation history, optionally filtered by chat_id"""
    if user_id not in user_contexts:
        return []
    
    context = user_contexts[user_id]
    if chat_id:
        return [msg for msg in context.conversation_history if msg["chat_id"] == chat_id]
    return context.conversation_history

def clear_user_context(user_id: str):
    """Clear user context (useful for logout)"""
    if user_id in user_contexts:
        del user_contexts[user_id]

# Optional: Add user context persistence to file
def save_contexts_to_file():
    """Save user contexts to file for persistence"""
    try:
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        contexts_data = {}
        for user_id, context in user_contexts.items():
            contexts_data[user_id] = {
                "user_id": context.user_id,
                "username": context.username,
                "email": context.email,
                "current_chat_id": context.current_chat_id,
                "current_document_id": context.current_document_id,
                "conversation_history": context.conversation_history,
                "created_at": context.created_at.isoformat()
            }
        
        with open(data_dir / "user_contexts.json", "w") as f:
            json.dump(contexts_data, f, indent=2)
    except Exception as e:
        print(f"Error saving user contexts: {e}")

def load_contexts_from_file():
    """Load user contexts from file"""
    try:
        contexts_file = Path("data") / "user_contexts.json"
        if contexts_file.exists():
            with open(contexts_file, "r") as f:
                contexts_data = json.load(f)
            
            for user_id, data in contexts_data.items():
                context = UserContext(data["user_id"], data["username"], data["email"])
                context.current_chat_id = data.get("current_chat_id")
                context.current_document_id = data.get("current_document_id")
                context.conversation_history = data.get("conversation_history", [])
                context.created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
                user_contexts[user_id] = context
    except Exception as e:
        print(f"Error loading user contexts: {e}")
