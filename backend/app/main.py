from fastapi import FastAPI
from app.routes import job_roles, cv_uploads , auth,evaluation

app = FastAPI()

# app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(job_roles.router, prefix="/job-roles", tags=["job_roles"])
app.include_router(cv_uploads.router, prefix="/cv-uploads", tags=["cv_uploads"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(evaluation.router, prefix="/evaluation", tags=["evaluation"])


@app.get("/")
async def root():
    return {"message": "CV-align backend with MongoDB is running!"}
