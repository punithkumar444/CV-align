from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "mongodb+srv://punithkumar444:NAni.123@cluster0.a6mhwmx.mongodb.net/"

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.cv_align_db

job_roles_collection = database.get_collection("job_roles")
cv_uploads_collection = database.get_collection("cv_uploads")
users_collection = database.get_collection("users")  # <-- Add this line
