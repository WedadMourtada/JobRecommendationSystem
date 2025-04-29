from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil
import os

app = FastAPI()  # << THIS MUST BE EXACTLY HERE

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads folder
UPLOAD_FOLDER = "uploaded_resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    # Dummy job recommendations
    recommended_jobs = [
        {"title": "Software Engineer", "location": "New York", "similarity": 92},
        {"title": "Data Analyst", "location": "Remote", "similarity": 88},
        {"title": "Business Analyst", "location": "Boston", "similarity": 85},
    ]

    return recommended_jobs
