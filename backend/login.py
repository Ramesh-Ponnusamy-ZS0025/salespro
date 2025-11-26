"""
Authentication & Login Module
Contains: User models, auth helpers, login/register routes
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
from passlib.context import CryptContext
import os

# JWT and password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

JWT_SECRET = os.environ.get('JWT_SECRET', 'mysecret')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 24))

# Router
router = APIRouter(prefix="/api", tags=["auth"])

# Database reference - will be set from server.py
db = None

def set_db(database):
    global db
    db = database

# ============== MODELS ==============

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    username: str
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

# ============== AUTH HELPERS ==============

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

        user_data = await db.users.find_one({"id": user_id}, {"_id": 0})
        if user_data is None:
            raise HTTPException(status_code=401, detail="User not found")

        return User(**user_data)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============== AUTH ROUTES ==============

@router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
    )

    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.users.insert_one(doc)

    # Create token
    access_token = create_access_token({"sub": user.id, "email": user.email})

    return TokenResponse(
        access_token=access_token,
        user={"id": user.id, "email": user.email, "username": user.username}
    )

@router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user_data = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = User(**user_data)
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token({"sub": user.id, "email": user.email})

    return TokenResponse(
        access_token=access_token,
        user={"id": user.id, "email": user.email, "username": user.username}
    )

@router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "username": current_user.username}
