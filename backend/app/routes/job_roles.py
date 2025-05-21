from fastapi import APIRouter, HTTPException
from typing import List
from app.models.job_role import JobRoleModel, JobRoleCreate
from app.database import job_roles_collection

router = APIRouter()

@router.post("/", response_model=JobRoleModel)
async def create_job_role(job_role: JobRoleCreate):
    job_role_dict = job_role.dict()
    new_job_role = await job_roles_collection.insert_one(job_role_dict)
    created_job_role = await job_roles_collection.find_one({"_id": new_job_role.inserted_id})
    return created_job_role

@router.get("/", response_model=List[JobRoleModel])
async def list_job_roles():
    roles_cursor = job_roles_collection.find()
    roles = await roles_cursor.to_list(length=100)
    return roles
