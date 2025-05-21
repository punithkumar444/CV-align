from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List, Optional
from app.models.cv import CVModel, CVCreate
from app.database import cv_uploads_collection, job_roles_collection
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
):
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
    )

    result = await cv_uploads_collection.insert_one(cv_data.dict(by_alias=True))
    saved_cv = await cv_uploads_collection.find_one({"_id": result.inserted_id})

    return CVModel(**saved_cv)


@router.get("/", response_model=List[CVModel])
async def list_cvs(job_role_id: Optional[str] = None):
    query = {}
    if job_role_id:
        if not ObjectId.is_valid(job_role_id):
            raise HTTPException(status_code=400, detail="Invalid job_role_id")
        query["job_role_id"] = ObjectId(job_role_id)

    cvs = await cv_uploads_collection.find(query).to_list(length=100)
    return [CVModel(**cv) for cv in cvs]


@router.get("/{cv_id}")
async def get_cv(cv_id: str):
    if not ObjectId.is_valid(cv_id):
        raise HTTPException(status_code=400, detail="Invalid CV ID")

    cv = await cv_uploads_collection.find_one({"_id": ObjectId(cv_id)})

    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

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
