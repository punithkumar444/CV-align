from fastapi import APIRouter, HTTPException, status
from app.schemas.user import UserCreate, UserLogin, TokenResponse
from app.database import users_collection
from app.auth_utils import get_password_hash, verify_password, create_access_token
from datetime import timedelta

router = APIRouter()

@router.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserCreate):
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user_data.password)
    new_user = {
        "email": user_data.email,
        "password": hashed_password,
        "firstname": user_data.firstname,
        "lastname": user_data.lastname,
    }
    await users_collection.insert_one(new_user)

    token = create_access_token({"sub": user_data.email})
    return {
    "access_token": token,
    "token_type": "bearer",
    "user": {
        "email": user_data.email,
        "role": "user",
        "id": str(new_user_id)
    }
}

@router.post("/signin", response_model=TokenResponse)
async def signin(user: UserLogin):
    existing_user = await users_collection.find_one({"email": user.email})
    if not existing_user or not verify_password(user.password, existing_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
