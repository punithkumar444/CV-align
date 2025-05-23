from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
# from app.schemas.user import Token  # create if needed
from app.database import users_collection, companies_collection
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")

SECRET_KEY = "your-secret-key"  # use env var in production
ALGORITHM = "HS256"

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")
        user_id = payload.get("id")

        if not email or not role or not user_id:
            raise credentials_exception

        collection = users_collection if role == "user" else companies_collection
        user = await collection.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise credentials_exception

        user["role"] = role
        user["id"] = user_id
        return user

    except JWTError:
        raise credentials_exception
