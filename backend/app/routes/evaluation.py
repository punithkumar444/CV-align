from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.schemas.evaluation import CVEvaluationResponse
from app.database import cv_uploads_collection, job_roles_collection
from app.evaluation_utils import extract_text_from_cv, evaluate_cv_against_job
import nltk
nltk.download('punkt')

router = APIRouter()

@router.get("/{job_role_id}/{cv_id}", response_model=CVEvaluationResponse)
async def evaluate_cv(job_role_id: str, cv_id: str):
    if not ObjectId.is_valid(job_role_id):
        raise HTTPException(status_code=400, detail="Invalid job_role_id")
    if not ObjectId.is_valid(cv_id):
        raise HTTPException(status_code=400, detail="Invalid cv_id")

    job_role = await job_roles_collection.find_one({"_id": ObjectId(job_role_id)})
    if not job_role:
        raise HTTPException(status_code=404, detail="Job role not found")

    cv = await cv_uploads_collection.find_one({"_id": ObjectId(cv_id)})
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    import base64
    cv_content_bytes = base64.b64decode(cv["data"])

    cv_text = extract_text_from_cv(cv_content_bytes)
    job_description = job_role.get("description", "")

    evaluation_result = evaluate_cv_against_job(cv_text, job_description)
    return evaluation_result
