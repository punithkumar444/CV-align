from pydantic import BaseModel, Field
from typing import Optional
from app.models.utils import PyObjectId
from bson import ObjectId


class CVBase(BaseModel):
    filename: str
    content_type: str
    data: str  # base64 encoded string
    description: Optional[str] = None
    job_role_id: Optional[PyObjectId] = None  # Reference to JobRole
    user_id: Optional[PyObjectId] = None  # NEW: Reference to User

    class Config:
        json_encoders = {
            ObjectId: str,
        }
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "filename": "resume.pdf",
                "content_type": "application/pdf",
                "description": "My latest resume",
                "job_role_id": "646f1e9f12e4f7e0f4b12345",
                "user_id": "646f1e9f12e4f7e0f4b12346"
            }
        }


class CVCreate(CVBase):
    pass


class CVModel(CVBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str,
        }
        validate_by_name = True
