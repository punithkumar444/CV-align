from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from typing import List, Optional
from app.models.cv import CVModel, CVCreate
from app.database import cv_uploads_collection, job_roles_collection, users_collection
from app.dependencies.auth import get_current_user
from bson import ObjectId
import base64
import io
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/cv", tags=["cv_uploads"])


@router.post("/", response_model=CVModel)
async def upload_cv(
    file: UploadFile = File(...),
    description: str = Form(""),
    job_role_id: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Only users can upload CVs")
        
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    # Validate job_role_id if provided
    if job_role_id:
        if not ObjectId.is_valid(job_role_id):
            raise HTTPException(status_code=400, detail="Invalid job_role_id")
        job_role = await job_roles_collection.find_one({"_id": ObjectId(job_role_id)})
        if not job_role:
            raise HTTPException(status_code=404, detail="Job role not found")

    base64_data = base64.b64encode(content).decode("utf-8")

    cv_data = CVCreate(
        filename=file.filename,
        content_type=file.content_type,
        data=base64_data,
        description=description,
        job_role_id=ObjectId(job_role_id) if job_role_id else None,
        user_id=ObjectId(current_user["_id"])  # use _id consistently
    )

    # Insert the dict with ObjectId intact
    result = await cv_uploads_collection.insert_one(cv_data.dict(by_alias=True, exclude_none=True))
    saved_cv = await cv_uploads_collection.find_one({"_id": result.inserted_id})

    return CVModel(**saved_cv)


@router.get("/", response_model=List[CVModel])
async def list_cvs(
    job_role_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    query = {}

    if job_role_id:
        if not ObjectId.is_valid(job_role_id):
            raise HTTPException(status_code=400, detail="Invalid job_role_id")
        query["job_role_id"] = job_role_id

    # Use "_id" here as well for consistency
    if current_user["role"] == "user":
        query["user_id"] = current_user["_id"]

    cvs = await cv_uploads_collection.find(query).to_list(length=100)
    enriched_cvs = []
    for cv in cvs:
        user = await users_collection.find_one({"_id": cv["user_id"]})
        if user:
            cv["user_email"] = user["email"]
            cv["user_name"] = f"{user.get('firstname', '')} {user.get('lastname', '')}".strip()
        enriched_cvs.append(CVModel(**cv))

    return enriched_cvs


@router.get("/{cv_id}")
async def get_cv(
    cv_id: str,
    current_user: dict = Depends(get_current_user)
):
    if not ObjectId.is_valid(cv_id):
        raise HTTPException(status_code=400, detail="Invalid CV ID")

    cv = await cv_uploads_collection.find_one({"_id": ObjectId(cv_id)})

    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    # Consistent _id access & type check for authorization
    if current_user["role"] == "user" and cv.get("user_id") != ObjectId(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to access this CV")

    try:
        file_data = base64.b64decode(cv["data"])
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=cv["content_type"],
            headers={
                "Content-Disposition": f"attachment; filename={cv['filename']}"
            }
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to decode or send file")
