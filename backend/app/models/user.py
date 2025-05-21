from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from bson import ObjectId
import os

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["cv_align"]
user_collection = db["users"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_email(email: str):
    return await user_collection.find_one({"email": email})

async def create_user(user: dict):
    user["password"] = pwd_context.hash(user["password"])
    result = await user_collection.insert_one(user)
    return str(result.inserted_id)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
