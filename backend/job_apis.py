import requests
from typing import List, Dict, Optional
from urllib.parse import quote_plus
import json
from datetime import datetime


class JoobleAPI:
    """Jooble API - Free, no auth required for demo"""
    
    BASE_URL = "https://jooble.org/api/"
    API_KEY = "a055a76f-87d5-4966-8104-9d4426720869"  # Free demo key
    
    def search(self, query: str, location: str = "USA", page: int = 1) -> List[Dict]:
        jobs = []
        try:
            payload = {
                "keywords": query,
                "location": location,
                "page": page
            }
            
            response = requests.post(
                f"{self.BASE_URL}{self.API_KEY}",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                for job in data.get("jobs", []):
                    jobs.append({
                        "title": job.get("title", ""),
                        "company": job.get("company", ""),
                        "location": job.get("location", ""),
                        "url": job.get("link", ""),
                        "snippet": job.get("snippet", ""),
                        "salary": job.get("salary", ""),
                        "source": "Jooble",
                        "posted": job.get("datePublished", ""),
                        "remote": self._is_remote(job),
                        "skills": [],
                        "requirements": [],
                        "responsibilities": []
                    })
        except Exception as e:
            print(f"Jooble API error: {e}")
        return jobs
    
    def _is_remote(self, job: Dict) -> bool:
        text = f"{job.get('title', '')} {job.get('location', '')} {job.get('snippet', '')}".lower()
        return "remote" in text


class AdzunaAPI:
    """Adzuna API - Free tier available"""
    
    BASE_URL = "https://api.adzuna.com/v1/api/jobs"
    
    def __init__(self, app_id: str = "", app_key: str = ""):
        self.app_id = app_id
        self.app_key = app_key
    
    def search(self, query: str, country: str = "us", page: int = 1) -> List[Dict]:
        jobs = []
        
        if not self.app_id or not self.app_key:
            return self._mock_adzuna_jobs(query)
        
        try:
            url = f"{self.BASE_URL}/{country}/search/{page}"
            params = {
                "app_id": self.app_id,
                "app_key": self.app_key,
                "what": query,
                "results_per_page": 20,
                "content-type": "application/json"
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                for job in data.get("results", []):
                    jobs.append({
                        "title": job.get("title", ""),
                        "company": job.get("company", {}).get("display_name", ""),
                        "location": job.get("location", {}).get("display_name", ""),
                        "url": job.get("redirect_url", ""),
                        "snippet": job.get("description", ""),
                        "salary": self._format_salary(job.get("salary_min"), job.get("salary_max")),
                        "source": "Adzuna",
                        "posted": job.get("created", ""),
                        "remote": False,
                        "skills": [],
                        "requirements": [],
                        "responsibilities": []
                    })
        except Exception as e:
            print(f"Adzuna API error: {e}")
        return jobs
    
    def _format_salary(self, min_sal, max_sal) -> str:
        if min_sal and max_sal:
            return f"${int(min_sal):,} - ${int(max_sal):,}"
        elif min_sal:
            return f"From ${int(min_sal):,}"
        return ""
    
    def _mock_adzuna_jobs(self, query: str) -> List[Dict]:
        return []


class RemotiveAPI:
    """Remotive API - Free, remote tech jobs"""
    
    BASE_URL = "https://remotive.com/api"
    
    def search(self, query: str = "", category: str = "") -> List[Dict]:
        jobs = []
        try:
            params = {}
            if query:
                params["search"] = query
            if category:
                params["category"] = category
            
            response = requests.get(
                f"{self.BASE_URL}/remote-jobs",
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                for job in data.get("jobs", []):
                    jobs.append({
                        "title": job.get("title", ""),
                        "company": job.get("company_name", ""),
                        "location": job.get("candidate_required_location", "Worldwide"),
                        "url": job.get("url", ""),
                        "snippet": job.get("description", "")[:500],
                        "salary": job.get("salary", ""),
                        "source": "Remotive",
                        "posted": job.get("publication_date", ""),
                        "remote": True,
                        "skills": job.get("tags", []),
                        "requirements": [],
                        "responsibilities": []
                    })
        except Exception as e:
            print(f"Remotive API error: {e}")
        return jobs


class ArbeitnowAPI:
    """Arbeitnow API - Free, no auth required"""
    
    BASE_URL = "https://www.arbeitnow.com/api"
    
    def search(self, query: str = "") -> List[Dict]:
        jobs = []
        try:
            params = {"remote": "true"}
            if query:
                params["q"] = query
            
            response = requests.get(
                f"{self.BASE_URL}/job-board-api",
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                for job in data.get("data", []):
                    jobs.append({
                        "title": job.get("title", ""),
                        "company": job.get("company_name", ""),
                        "location": job.get("location", ""),
                        "url": job.get("url", ""),
                        "snippet": job.get("description", "")[:500],
                        "salary": "",
                        "source": "Arbeitnow",
                        "posted": job.get("created_at", ""),
                        "remote": job.get("remote", False),
                        "skills": job.get("tags", []),
                        "requirements": [],
                        "responsibilities": []
                    })
        except Exception as e:
            print(f"Arbeitnow API error: {e}")
        return jobs


class USAJobsAPI:
    """USAJobs API - Free, US government jobs"""
    
    BASE_URL = "https://data.usajobs.gov/api"
    
    def search(self, query: str = "", state: str = "") -> List[Dict]:
        jobs = []
        try:
            headers = {
                "Host": "data.usajobs.gov",
                "User-Agent": "jobsearch-agent@email.com",
                "Authorization-Key": ""
            }
            
            params = {
                "Keyword": query,
                "ResultsPerPage": 20
            }
            
            if state:
                params["LocationName"] = state
            
            response = requests.get(
                f"{self.BASE_URL}/Search",
                params=params,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                for job in data.get("SearchResult", {}).get("SearchResultItems", []):
                    job_data = job.get("MatchedObjectDescriptor", {})
                    jobs.append({
                        "title": job_data.get("PositionTitle", ""),
                        "company": job_data.get("OrganizationName", ""),
                        "location": job_data.get("PositionLocation", [{}])[0].get("CityName", "") + ", " + job_data.get("PositionLocation", [{}])[0].get("CountrySubDivisionCode", ""),
                        "url": f"https://www.usajobs.gov/GetJob/ViewDetails/{job_data.get('PositionID', '')}",
                        "snippet": job_data.get("UserArea", {}).get("MajorDuties", [""])[0] if job_data.get("UserArea", {}).get("MajorDuties") else "",
                        "salary": job_data.get("PositionRemuneration", [{}])[0].get("MinimumRange", "") + " - " + job_data.get("PositionRemuneration", [{}])[0].get("MaximumRange", ""),
                        "source": "USAJobs",
                        "posted": job_data.get("PublicationStartDate", ""),
                        "remote": "remote" in job_data.get("PositionLocation", [{}])[0].get("CityName", "").lower() if job_data.get("PositionLocation") else False,
                        "skills": [],
                        "requirements": [],
                        "responsibilities": []
                    })
        except Exception as e:
            print(f"USAJobs API error: {e}")
        return jobs
