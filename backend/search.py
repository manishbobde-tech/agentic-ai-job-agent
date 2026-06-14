import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import json
from pathlib import Path
from urllib.parse import quote_plus
import re


class JobSearcher:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        
        self.us_states = {
            "California": ["San Francisco", "Los Angeles", "San Diego", "San Jose", "Palo Alto", "Mountain View", "Santa Clara", "Irvine"],
            "New York": ["New York City", "Manhattan", "Brooklyn", "Buffalo", "Albany"],
            "Texas": ["Austin", "Houston", "Dallas", "San Antonio", "Fort Worth"],
            "Washington": ["Seattle", "Bellevue", "Redmond"],
            "Massachusetts": ["Boston", "Cambridge", "Somerville"],
            "Colorado": ["Denver", "Boulder"],
            "Illinois": ["Chicago", "Naperville"],
            "Georgia": ["Atlanta", "Savannah"],
            "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville"],
            "North Carolina": ["Charlotte", "Raleigh", "Durham"],
            "Virginia": ["Arlington", "Alexandria", "Richmond"],
            "Oregon": ["Portland", "Eugene"],
            "Arizona": ["Phoenix", "Scottsdale"],
            "Michigan": ["Detroit", "Ann Arbor"],
            "Pennsylvania": ["Philadelphia", "Pittsburgh"],
            "Ohio": ["Columbus", "Cleveland", "Cincinnati"],
            "Tennessee": ["Nashville", "Memphis"],
            "Minnesota": ["Minneapolis", "St. Paul"],
            "Maryland": ["Baltimore", "Bethesda"]
        }
    
    def search(self, query: str, num_results: int = 20, location: str = "", 
               country: str = "USA", state: str = "", city: str = "", 
               remote_only: bool = False) -> List[Dict]:
        
        all_jobs = []
        
        # Search 1: Remotive (remote jobs, many USA)
        print("  → Searching Remotive...")
        remotive_jobs = self._search_remotive(query)
        all_jobs.extend(remotive_jobs)
        
        # Search 2: Arbeitnow (remote jobs)
        print("  → Searching Arbeitnow...")
        arbeitnow_jobs = self._search_arbeitnow(query)
        all_jobs.extend(arbeitnow_jobs)
        
        # Search 3: Findwork (tech jobs)
        print("  → Searching Findwork...")
        findwork_jobs = self._search_findwork(query)
        all_jobs.extend(findwork_jobs)
        
        # Search 4: Google for USA job boards
        print("  → Searching Google...")
        google_jobs = self._search_google_usa(query, state, city)
        all_jobs.extend(google_jobs)
        
        # Deduplicate
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            title_key = f"{job['title'].lower().strip()}_{job.get('company', '').lower().strip()}"
            if title_key not in seen and job.get('title'):
                seen.add(title_key)
                unique_jobs.append(job)
        
        # Filter by state/city if specified
        if state or city:
            unique_jobs = self._filter_by_location(unique_jobs, state, city)
        
        result = unique_jobs[:num_results]
        
        # Cache
        with open("cached_jobs.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"  → Found {len(result)} jobs")
        return result
    
    def _search_remotive(self, query: str) -> List[Dict]:
        """Search Remotive API - Free, remote tech jobs"""
        jobs = []
        try:
            response = requests.get(
                "https://remotive.com/api/remote-jobs",
                params={"search": query},
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                for job in data.get("jobs", [])[:15]:
                    location = job.get("candidate_required_location", "")
                    if location in ["Worldwide", "USA", "United States", ""]:
                        jobs.append({
                            "title": job.get("title", ""),
                            "company": job.get("company_name", ""),
                            "location": "Remote (USA)" if location in ["USA", "United States"] else "Remote",
                            "url": job.get("url", ""),
                            "snippet": self._clean_html(job.get("description", ""))[:400],
                            "salary": job.get("salary", "Not specified"),
                            "source": "Remotive",
                            "posted": job.get("publication_date", ""),
                            "remote": True,
                            "skills": job.get("tags", [])[:6],
                            "requirements": [],
                            "responsibilities": [],
                            "job_type": job.get("job_type", "")
                        })
        except Exception as e:
            print(f"  Remotive error: {e}")
        return jobs
    
    def _search_arbeitnow(self, query: str) -> List[Dict]:
        """Search Arbeitnow API - Free, remote jobs"""
        jobs = []
        try:
            response = requests.get(
                "https://www.arbeitnow.com/api/job-board-api",
                params={"remote": "true"},
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                for job in data.get("data", [])[:10]:
                    # Filter for USA-ish jobs
                    location = job.get("location", "")
                    if self._is_usa_location(location) or "remote" in location.lower():
                        jobs.append({
                            "title": job.get("title", ""),
                            "company": job.get("company_name", ""),
                            "location": location or "Remote",
                            "url": job.get("url", ""),
                            "snippet": self._clean_html(job.get("description", ""))[:400],
                            "salary": "",
                            "source": "Arbeitnow",
                            "posted": job.get("created_at", ""),
                            "remote": job.get("remote", False),
                            "skills": job.get("tags", [])[:6],
                            "requirements": [],
                            "responsibilities": [],
                            "job_type": ""
                        })
        except Exception as e:
            print(f"  Arbeitnow error: {e}")
        return jobs
    
    def _search_findwork(self, query: str) -> List[Dict]:
        """Search Findwork API - Free tech jobs"""
        jobs = []
        try:
            response = requests.get(
                "https://findwork.dev/api/jobs/",
                params={"search": query, "remote": "true"},
                headers={**self.headers, "Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                for job in data.get("results", [])[:10]:
                    jobs.append({
                        "title": job.get("role", ""),
                        "company": job.get("company_name", ""),
                        "location": job.get("location", "") or "Remote",
                        "url": job.get("url", ""),
                        "snippet": job.get("text", "")[:400],
                        "salary": "",
                        "source": "Findwork",
                        "posted": job.get("date_posted", ""),
                        "remote": True,
                        "skills": job.get("employment_type", []),
                        "requirements": [],
                        "responsibilities": [],
                        "job_type": job.get("employment_type", "")
                    })
        except Exception as e:
            print(f"  Findwork error: {e}")
        return jobs
    
    def _search_google_usa(self, query: str, state: str = "", city: str = "") -> List[Dict]:
        """Search Google for USA jobs"""
        jobs = []
        try:
            if city and state:
                location = f"{city}, {state}"
            elif state:
                location = state
            else:
                location = "United States"
            
            search_query = f"{query} jobs hiring {location} -site:linkedin.com"
            
            response = requests.get(
                "https://www.google.com/search",
                params={"q": search_query, "num": 12, "gl": "us", "hl": "en"},
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "Accept": "text/html",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                timeout=10
            )
            soup = BeautifulSoup(response.text, "html.parser")
            
            for result in soup.select("div.g")[:10]:
                title_elem = result.select_one("h3")
                link_elem = result.select_one("a")
                snippet_elem = result.select_one("div.VwiC3b")
                
                if title_elem and link_elem:
                    url = link_elem["href"]
                    if "/url?q=" in url:
                        url = url.split("/url?q=")[1].split("&")[0]
                    
                    if "linkedin.com" in url.lower():
                        continue
                    
                    snippet = snippet_elem.text if snippet_elem else ""
                    
                    if self._snippet_mentions_usa(snippet, state, city):
                        jobs.append({
                            "title": title_elem.text,
                            "url": url,
                            "snippet": snippet,
                            "source": self._detect_source(url),
                            "company": self._extract_company(title_elem.text, snippet),
                            "location": f"{city}, {state}" if city else state or "USA",
                            "skills": self._extract_skills(snippet),
                            "requirements": [],
                            "responsibilities": [],
                            "remote": "remote" in snippet.lower(),
                            "salary": self._extract_salary(snippet),
                            "posted": "",
                            "job_type": ""
                        })
        except Exception as e:
            print(f"  Google error: {e}")
        return jobs
    
    def _is_usa_location(self, location: str) -> bool:
        if not location:
            return False
        location_lower = location.lower()
        usa_keywords = [
            "usa", "united states", "america", "remote",
            "california", "new york", "texas", "washington", "massachusetts",
            "colorado", "illinois", "georgia", "florida", "north carolina",
            "virginia", "oregon", "arizona", "michigan", "pennsylvania",
            "ohio", "tennessee", "minnesota", "maryland",
            "san francisco", "los angeles", "seattle", "boston", "chicago",
            "austin", "denver", "atlanta", "miami", "dallas", "houston",
            "phoenix", "portland", "san diego", "nashville", "raleigh"
        ]
        for keyword in usa_keywords:
            if keyword in location_lower:
                return True
        if re.search(r',\s*[A-Z]{2}\b', location):
            return True
        return False
    
    def _snippet_mentions_usa(self, snippet: str, state: str = "", city: str = "") -> bool:
        snippet_lower = snippet.lower()
        if not state and not city:
            return any(kw in snippet_lower for kw in ["usa", "united states", "remote", "hiring"])
        if state and state.lower() in snippet_lower:
            return True
        if city and city.lower() in snippet_lower:
            return True
        return False
    
    def _filter_by_location(self, jobs: List[Dict], state: str = "", city: str = "") -> List[Dict]:
        if not state and not city:
            return jobs
        filtered = []
        for job in jobs:
            location = job.get("location", "").lower()
            if job.get("remote", False):
                filtered.append(job)
                continue
            if state and state.lower() in location:
                filtered.append(job)
            elif city and city.lower() in location:
                filtered.append(job)
        return filtered
    
    def _clean_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    
    def _detect_source(self, url: str) -> str:
        url_lower = url.lower()
        if "indeed.com" in url_lower:
            return "Indeed"
        elif "glassdoor" in url_lower:
            return "Glassdoor"
        elif "builtin" in url_lower:
            return "BuiltIn"
        else:
            return "Web"
    
    def _extract_company(self, title: str, snippet: str) -> str:
        parts = title.split(" at ")
        if len(parts) > 1:
            return parts[-1].strip()
        parts = title.split(" - ")
        if len(parts) > 1:
            return parts[-1].strip()
        return "Unknown"
    
    def _extract_skills(self, text: str) -> List[str]:
        skill_keywords = [
            "python", "javascript", "typescript", "react", "node", "aws", "docker",
            "kubernetes", "sql", "git", "api", "machine learning", "ai", "llm",
            "langchain", "pytorch", "tensorflow", "fastapi", "django", "java", "go"
        ]
        found = []
        text_lower = text.lower()
        for skill in skill_keywords:
            if skill in text_lower:
                found.append(skill.title())
        return found[:6]
    
    def _extract_salary(self, text: str) -> str:
        patterns = [
            r'\$[\d,]+(?:k|K)?(?:\s*-\s*\$[\d,]+(?:k|K)?)?',
            r'[\d,]+(?:k|K)?\s*(?:USD|per year|annual)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return ""
    
    def get_usa_locations(self) -> Dict:
        return {"states": self.us_states}
