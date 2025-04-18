from typing import Optional
from passlib.context import CryptContext
from app.db import db
from app.models.user import UserCreate, UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
collection = db["users"]

async def get_user_by_username(username: str) -> Optional[UserInDB]:
    doc = await collection.find_one({"username": username})
    if not doc:
        return None
    return UserInDB(
        id=str(doc.get("_id")),
        username=doc.get("username"),
        email=doc.get("email"),
        hashed_password=doc.get("hashed_password")
    )

async def create_user(user: UserCreate) -> UserInDB:
    hashed_password = pwd_context.hash(user.password)
    doc = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password
    }
    result = await collection.insert_one(doc)
    return UserInDB(
        id=str(result.inserted_id),
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

async def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = await get_user_by_username(username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user