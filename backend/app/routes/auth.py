from fastapi import APIRouter, HTTPException, status
from app.schemas.user import UserCreate, UserLogin, TokenResponse
from app.schemas.company import CompanyCreate, CompanyLogin
from app.database import users_collection, companies_collection
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
    result = await users_collection.insert_one(new_user)

    token = create_access_token({"sub": user_data.email, "role":"user", "id": str(result.inserted_id)})
    return {
    "access_token": token,
    "token_type": "bearer",
    "user": {
        "email": user_data.email,
        "role": "user",
        "id": str(result.inserted_id)
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

    token = create_access_token({"sub": user.email, "role":"user", "id": str(existing_user["_id"])})
    return {"access_token": token, "token_type": "bearer"}

COMPANY_SIGNUP_SECRET = "HEHEHE"  # set securely in env in production

@router.post("/company/signup", response_model=TokenResponse)
async def company_signup(company_data: CompanyCreate):
    if company_data.company_secret != COMPANY_SIGNUP_SECRET:
        raise HTTPException(status_code=403, detail="Invalid company secret")

    existing_company = await companies_collection.find_one({"email": company_data.email})
    if existing_company:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(company_data.password)
    new_company = {
        "email": company_data.email,
        "password": hashed_password,
        "company_name": company_data.company_name,
    }
    result = await companies_collection.insert_one(new_company)

    token = create_access_token({"sub": company_data.email, "role": "company","id": str(result.inserted_id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "email": company_data.email,
            "role": "company",
            "id": str(result.inserted_id)
        }
    }

@router.post("/company/signin", response_model=TokenResponse)
async def company_signin(company: CompanyLogin):
    existing_company = await companies_collection.find_one({"email": company.email})
    if not existing_company or not verify_password(company.password, existing_company["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token({"sub": company.email, "role": "company", "id": str(existing_company["_id"])})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "email": company.email,
            "role": "company",
            "id": str(existing_company["_id"])
        }
    }
