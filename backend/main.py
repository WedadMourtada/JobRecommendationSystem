from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import fitz  # PyMuPDF

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

# Load datasets
DATASET_DIR = "datasets"
jobs_df = pd.read_csv(os.path.join(DATASET_DIR, "final_data.csv"))
jobs_df.columns = jobs_df.columns.str.strip()  # Fix column spacing issues

salary_df = pd.read_csv(os.path.join(DATASET_DIR, "software_engineer_salaries.csv"))
nyc_jobs_df = pd.read_csv(os.path.join(DATASET_DIR, "jobs_nyc_postings.csv"))

# Get skill columns (all uppercase binary flags except LEVEL/INVOLVEMENT)
skill_columns = [
    col for col in jobs_df.columns
    if col.isupper() and col not in ["LEVEL", "INVOLVEMENT"]
]

# Build a pseudo-description from designation + metadata + active skills
def combine_skills(row):
    skills = [col for col in skill_columns if row.get(col) == 1]
    return " ".join(skills)

jobs_df["description"] = (
    jobs_df["Designation"].fillna("") + " " +
    jobs_df["Level"].fillna("") + " " +
    jobs_df["Involvement"].fillna("") + " " +
    jobs_df.apply(combine_skills, axis=1)
)

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    # Save uploaded file
    file_location = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    # Read resume content (supports .pdf and .txt)
    resume_text = ""
    
    if file.filename.lower().endswith(".pdf"):
        with fitz.open(file_location) as doc:
            for page in doc:
                resume_text += page.get_text()
    else:
        with open(file_location, "r", encoding="utf-8") as f:
            resume_text = f.read()

    # DEBUG: Show resume content
    print("=== Resume Text Start ===")
    print(resume_text[:1000])
    print("=== Resume Text End ===")

    # Vectorize job descriptions + resume using TF-IDF
    corpus = jobs_df["description"].tolist() + [resume_text]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Compute cosine similarity between resume and all job descriptions
    similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

    # DEBUG: Show similarity scores
    print("Max similarity:", similarity_scores.max())
    print("Top 5 similarity scores:", similarity_scores[:5])

    jobs_df["similarity"] = (similarity_scores * 100).round(2)

    # Sort by similarity and return top 5
    top_jobs = jobs_df.sort_values(by="similarity", ascending=False).head(5)
    recommended_jobs = top_jobs[["Designation", "Location", "similarity"]].to_dict(orient="records")

    return recommended_jobs




# from fastapi import FastAPI, File, UploadFile
# from fastapi.middleware.cors import CORSMiddleware
# from typing import List
# import shutil
# import os

# app = FastAPI()  # << THIS MUST BE EXACTLY HERE

# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Create uploads folder
# UPLOAD_FOLDER = "uploaded_resumes"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @app.post("/upload_resume")
# async def upload_resume(file: UploadFile = File(...)):
#     file_location = f"{UPLOAD_FOLDER}/{file.filename}"
#     with open(file_location, "wb+") as file_object:
#         shutil.copyfileobj(file.file, file_object)

#     # Dummy job recommendations
#     recommended_jobs = [
#         {"title": "Software Engineer", "location": "New York", "similarity": 92},
#         {"title": "Data Analyst", "location": "Remote", "similarity": 88},
#         {"title": "Business Analyst", "location": "Boston", "similarity": 85},
#     ]

#     return recommended_jobs
