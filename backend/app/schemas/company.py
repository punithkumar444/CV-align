from pydantic import BaseModel, EmailStr

class CompanyCreate(BaseModel):
    email: EmailStr
    password: str
    company_name: str
    company_secret: str  # new field

class CompanyLogin(BaseModel):
    email: EmailStr
    password: str
