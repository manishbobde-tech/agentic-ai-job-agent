import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import json
from pathlib import Path
from urllib.parse import quote_plus
from datetime import datetime, timedelta


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
            "Maryland": ["Baltimore", "Bethesda"],
            "Remote": ["Remote"]
        }
    
    def search(self, query: str, num_results: int = 20, location: str = "", 
               country: str = "USA", state: str = "", city: str = "", 
               remote_only: bool = False) -> List[Dict]:
        
        all_jobs = []
        
        # Search Remotive (real remote jobs)
        print("  → Searching Remotive (remote jobs)...")
        remotive_jobs = self._search_remotive(query)
        all_jobs.extend(remotive_jobs)
        
        # Search GitHub Jobs alternative - TechCareers
        print("  → Searching LinkedIn...")
        linkedin_jobs = self._search_linkedin(query, state, city, remote_only)
        all_jobs.extend(linkedin_jobs)
        
        # Search Google for USA jobs
        print("  → Searching Google Jobs...")
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
        
        # Sort by relevance
        result = unique_jobs[:num_results]
        
        # Cache results
        with open("cached_jobs.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"Found {len(result)} unique jobs")
        return result
    
    def _search_remotive(self, query: str) -> List[Dict]:
        """Search Remotive API - Free, real remote jobs"""
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
                    jobs.append({
                        "title": job.get("title", ""),
                        "company": job.get("company_name", ""),
                        "location": job.get("candidate_required_location", "Worldwide"),
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
            print(f"Remotive error: {e}")
        return jobs
    
    def _search_linkedin(self, query: str, state: str = "", city: str = "", remote_only: bool = False) -> List[Dict]:
        """Search LinkedIn"""
        jobs = []
        try:
            location = f"{city}, {state}" if city else state
            if not location:
                location = "United States"
            
            params = {"keywords": quote_plus(query), "location": quote_plus(location)}
            if remote_only:
                params["f_WT"] = "2"
            
            url = f"https://www.linkedin.com/jobs/search/?{'&'.join(f'{k}={v}' for k, v in params.items())}"
            
            response = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "text/html",
            }, timeout=10)
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            for card in soup.select("div.base-card")[:15]:
                title_elem = card.select_one("h3.base-search-card__title")
                company_elem = card.select_one("h4.base-search-card__subtitle")
                link_elem = card.select_one("a.base-card__full-link")
                location_elem = card.select_one("span.job-search-card__location")
                
                if title_elem:
                    job_location = location_elem.text.strip() if location_elem else ""
                    jobs.append({
                        "title": title_elem.text.strip(),
                        "url": link_elem["href"] if link_elem else "",
                        "company": company_elem.text.strip() if company_elem else "Unknown",
                        "location": job_location,
                        "source": "LinkedIn",
                        "snippet": "",
                        "salary": "",
                        "posted": "",
                        "remote": "remote" in job_location.lower() or "remote" in title_elem.text.lower(),
                        "skills": [],
                        "requirements": [],
                        "responsibilities": [],
                        "job_type": ""
                    })
        except Exception as e:
            print(f"LinkedIn error: {e}")
        return jobs
    
    def _search_google_usa(self, query: str, state: str = "", city: str = "") -> List[Dict]:
        """Search Google for USA jobs"""
        jobs = []
        try:
            location = f"{city}, {state} USA" if city else f"{state} USA" if state else "USA"
            search_query = f"{query} jobs {location}"
            
            response = requests.get(
                "https://www.google.com/search",
                params={"q": search_query, "num": 12},
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "Accept": "text/html",
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
                    
                    snippet = snippet_elem.text if snippet_elem else ""
                    
                    jobs.append({
                        "title": title_elem.text,
                        "url": url,
                        "snippet": snippet,
                        "source": self._detect_source(url),
                        "company": self._extract_company(title_elem.text, snippet),
                        "location": city or state or "USA",
                        "skills": self._extract_skills(snippet),
                        "requirements": [],
                        "responsibilities": [],
                        "remote": "remote" in snippet.lower(),
                        "salary": self._extract_salary(snippet),
                        "posted": "",
                        "job_type": ""
                    })
        except Exception as e:
            print(f"Google error: {e}")
        return jobs
    
    def _clean_html(self, html: str) -> str:
        """Remove HTML tags from text"""
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    
    def _detect_source(self, url: str) -> str:
        url_lower = url.lower()
        if "linkedin.com" in url_lower:
            return "LinkedIn"
        elif "indeed.com" in url_lower:
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
        import re
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
