from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import os
from pathlib import Path

from search import JobSearcher
from scraper import JobScraper
from resume_matcher import ResumeMatcher

app = FastAPI(title="Agentic AI Job Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

searcher = JobSearcher()
scraper = JobScraper()
matcher = ResumeMatcher()

class SearchRequest(BaseModel):
    query: str = "Agentic AI Engineer"
    location: str = "Remote"
    num_results: int = 20

class ResumeMatchRequest(BaseModel):
    resume_text: str
    job_description: str
    job_title: str = ""

class TailorResumeRequest(BaseModel):
    resume_text: str
    job_description: str
    job_title: str = ""
    instructions: str = ""

@app.get("/")
def root():
    return {"message": "Agentic AI Job Search API"}

@app.post("/api/search")
def search_jobs(request: SearchRequest):
    try:
        jobs = searcher.search(request.query, request.num_results)
        return {"jobs": jobs, "total": len(jobs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scrape/{job_index}")
def scrape_job(job_index: int):
    try:
        jobs_file = Path("cached_jobs.json")
        if not jobs_file.exists():
            raise HTTPException(status_code=404, detail="No cached jobs. Search first.")
        
        with open(jobs_file) as f:
            jobs = json.load(f)
        
        if job_index >= len(jobs):
            raise HTTPException(status_code=404, detail="Job index out of range")
        
        job = jobs[job_index]
        url = job.get("url", "")
        source = job.get("source", "generic").lower()
        
        description_data = scraper.scrape_job(url, source)
        if description_data:
            job["full_description"] = description_data.get("description", "")
            job["requirements"] = description_data.get("requirements", [])
            job["responsibilities"] = description_data.get("responsibilities", [])
        
        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/match")
def match_resume(request: ResumeMatchRequest):
    try:
        result = matcher.analyze_match(
            request.resume_text,
            request.job_description,
            request.job_title
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tailor")
def tailor_resume(request: TailorResumeRequest):
    try:
        result = matcher.tailor_resume(
            request.resume_text,
            request.job_description,
            request.job_title,
            request.instructions
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/cache")
def get_cached_jobs():
    jobs_file = Path("cached_jobs.json")
    if jobs_file.exists():
        with open(jobs_file) as f:
            jobs = json.load(f)
        return {"jobs": jobs}
    return {"jobs": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
