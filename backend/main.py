import pandas as pd
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import pdfplumber
from docx import Document
from collections import defaultdict

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploaded_resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load all datasets
final_data = pd.read_csv("datasets/final_data.csv")
try:
    jobs_nyc = pd.read_csv("datasets/jobs_nyc_postings.csv", nrows=10000)  # limit for performance
except Exception:
    jobs_nyc = pd.DataFrame()
try:
    se_salaries = pd.read_csv("datasets/software_engineer_salaries.csv")
except Exception:
    se_salaries = pd.DataFrame()

def extract_jobs():
    jobs = []
    # From final_data.csv
    for _, row in final_data.iterrows():
        jobs.append({
            "title": str(row.get("Designation", "")),
            "location": str(row.get("Location", "")),
            "company": str(row.get("Company_Name", "")),
            "desc": str(row.get("Industry", "")),
            "source": "final_data"
        })
    # From jobs_nyc_postings.csv
    if not jobs_nyc.empty:
        title_col = next((c for c in jobs_nyc.columns if "title" in c.lower()), None)
        loc_col = next((c for c in jobs_nyc.columns if "loc" in c.lower()), None)
        desc_col = next((c for c in jobs_nyc.columns if "desc" in c.lower()), None)
        for _, row in jobs_nyc.iterrows():
            jobs.append({
                "title": str(row.get(title_col, "")),
                "location": str(row.get(loc_col, "")),
                "company": str(row.get("company", "")),
                "desc": str(row.get(desc_col, "")),
                "source": "jobs_nyc"
            })
    # From software_engineer_salaries.csv
    if not se_salaries.empty:
        for _, row in se_salaries.iterrows():
            jobs.append({
                "title": str(row.get("Job Title", "")),
                "location": str(row.get("Location", "")),
                "company": str(row.get("Company", "")),
                "desc": str(row.get("Salary", "")),
                "source": "se_salaries"
            })
    return jobs

all_jobs = extract_jobs()

def extract_text_from_file(file_path):
    if file_path.lower().endswith('.pdf'):
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif file_path.lower().endswith('.docx'):
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    else:  # assume txt
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

def extract_skills(resume_text):
    skills = [
        "python", "java", "c++", "machine learning", "data science", "sql", "javascript", "html", "css",
        "react", "nodejs", "django", "flask", "pandas", "numpy", "linux", "cloud", "aws", "azure", "git"
    ]
    found = [skill for skill in skills if skill in resume_text.lower()]
    return set(found)

def is_tech_job(job):
    tech_keywords = [
        "engineer", "developer", "software", "data", "machine learning", "ai", "python", "java", "cloud", "it", "programmer", "analyst", "devops", "web", "full stack"
    ]
    job_text = (job["title"] + " " + job["desc"]).lower()
    return any(kw in job_text for kw in tech_keywords)

def get_country(location):
    loc = location.lower()
    if any(x in loc for x in ["india", "maharashtra", "karnataka", "delhi", "tamil nadu"]):
        return "India"
    if any(x in loc for x in ["usa", "united states", "ny", "new york", "california", "tx", "wa", "remote"]):
        return "USA"
    return "Other"

def improved_match(resume_text, jobs):
    resume_skills = extract_skills(resume_text)
    results = []
    for job in jobs:
        if not is_tech_job(job):
            continue
        score = 0
        for skill in resume_skills:
            if skill in (job["title"] + " " + job["desc"]).lower():
                score += 5
        for word in job["title"].split() + job["desc"].split():
            if word.lower() in resume_text.lower():
                score += 1
        similarity = min(100, score * 10)
        results.append({
            "title": job["title"],
            "location": job["location"],
            "company": job["company"],
            "similarity": similarity,
            "source": job["source"],
            "country": get_country(job["location"])
        })
    # Sort all results by similarity
    results = sorted(results, key=lambda x: x['similarity'], reverse=True)
    # Group by country
    country_groups = {}
    for job in results:
        country = job["country"]
        if country not in country_groups:
            country_groups[country] = job
    # Start with one per country
    diverse = list(country_groups.values())
    # Fill up to 10 with next best matches
    seen = set((job["title"], job["location"]) for job in diverse)
    for job in results:
        if len(diverse) >= 10:
            break
        if (job["title"], job["location"]) not in seen:
            diverse.append(job)
            seen.add((job["title"], job["location"]))
    return diverse[:10]

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    resume_text = extract_text_from_file(file_location)
    recommended_jobs = improved_match(resume_text, all_jobs)
    return recommended_jobs
