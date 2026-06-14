import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json
from pathlib import Path
import re
from urllib.parse import quote_plus


class JobSearcher:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        self.usa_locations = {
            "states": {
                "California": ["San Francisco", "Los Angeles", "San Diego", "San Jose", "Sacramento", "Palo Alto", "Mountain View", "Santa Clara"],
                "New York": ["New York City", "Brooklyn", "Buffalo", "Albany", "Manhattan"],
                "Texas": ["Austin", "Houston", "Dallas", "San Antonio", "Fort Worth"],
                "Washington": ["Seattle", "Bellevue", "Redmond", "Tacoma"],
                "Massachusetts": ["Boston", "Cambridge", "Somerville", "Worcester"],
                "Colorado": ["Denver", "Boulder", "Colorado Springs"],
                "Illinois": ["Chicago", "Naperville", "Aurora"],
                "Georgia": ["Atlanta", "Savannah", "Augusta"],
                "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville"],
                "Remote": ["Remote"]
            }
        }
    
    def search(self, query: str, num_results: int = 20, location: str = "", 
               country: str = "USA", state: str = "", city: str = "", 
               remote_only: bool = False) -> List[Dict]:
        
        all_jobs = []
        
        # Build location string
        location_str = self._build_location_string(country, state, city, remote_only)
        
        # Search multiple sources
        all_jobs.extend(self._search_google_jobs(query, location_str))
        all_jobs.extend(self._search_linkedin(query, location_str, remote_only))
        all_jobs.extend(self._search_indeed(query, location_str))
        all_jobs.extend(self._search_usa_jobs(query, location_str))
        
        # Deduplicate
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            title_key = f"{job['title'].lower().strip()}_{job.get('company', '').lower().strip()}"
            if title_key not in seen:
                seen.add(title_key)
                unique_jobs.append(job)
        
        # Filter by remote if requested
        if remote_only:
            unique_jobs = [j for j in unique_jobs if self._is_remote(j)]
        
        result = unique_jobs[:num_results]
        
        # Cache results
        with open("cached_jobs.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
        
        return result
    
    def _build_location_string(self, country: str, state: str, city: str, remote_only: bool) -> str:
        if remote_only:
            return "Remote"
        
        parts = []
        if city:
            parts.append(city)
        if state:
            parts.append(state)
        if country and country != "USA":
            parts.append(country)
        elif country == "USA" and not state and not city:
            parts.append("United States")
        
        return ", ".join(parts) if parts else ""
    
    def _search_google_jobs(self, query: str, location: str = "") -> List[Dict]:
        jobs = []
        try:
            search_query = f"{query} jobs"
            if location:
                search_query += f" {location}"
            
            response = requests.get(
                "https://www.google.com/search",
                params={"q": search_query, "num": 15},
                headers=self.headers,
                timeout=10
            )
            soup = BeautifulSoup(response.text, "html.parser")
            
            for result in soup.select("div.g"):
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
                        "location": self._extract_location(snippet, location),
                        "skills": self._extract_skills(snippet),
                        "requirements": [],
                        "responsibilities": [],
                        "remote": self._is_remote_text(snippet)
                    })
        except Exception as e:
            print(f"Google search error: {e}")
        return jobs
    
    def _search_linkedin(self, query: str, location: str = "", remote_only: bool = False) -> List[Dict]:
        jobs = []
        try:
            params = {"keywords": quote_plus(query)}
            if remote_only:
                params["f_WT"] = "2"  # Remote filter
            if location:
                params["location"] = quote_plus(location)
            
            url = f"https://www.linkedin.com/jobs/search/?{'&'.join(f'{k}={v}' for k, v in params.items())}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            for card in soup.select("div.base-card"):
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
                        "skills": [],
                        "requirements": [],
                        "responsibilities": [],
                        "remote": "remote" in job_location.lower() or "remote" in title_elem.text.lower()
                    })
        except Exception as e:
            print(f"LinkedIn search error: {e}")
        return jobs
    
    def _search_indeed(self, query: str, location: str = "") -> List[Dict]:
        jobs = []
        try:
            params = {"q": quote_plus(query)}
            if location:
                params["l"] = quote_plus(location)
            
            url = f"https://www.indeed.com/jobs?{'&'.join(f'{k}={v}' for k, v in params.items())}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            for card in soup.select("div.job_seen_beacon"):
                title_elem = card.select_one("h2.jobTitle a")
                company_elem = card.select_one("span.companyName")
                location_elem = card.select_one("div.companyLocation")
                snippet_elem = card.select_one("div.job-snippet")
                
                if title_elem:
                    job_location = location_elem.text.strip() if location_elem else ""
                    
                    jobs.append({
                        "title": title_elem.text.strip(),
                        "url": f"https://www.indeed.com{title_elem.get('href', '')}",
                        "company": company_elem.text.strip() if company_elem else "Unknown",
                        "location": job_location,
                        "source": "Indeed",
                        "snippet": snippet_elem.text.strip() if snippet_elem else "",
                        "skills": [],
                        "requirements": [],
                        "responsibilities": [],
                        "remote": "remote" in job_location.lower()
                    })
        except Exception as e:
            print(f"Indeed search error: {e}")
        return jobs
    
    def _search_usa_jobs(self, query: str, location: str = "") -> List[Dict]:
        """Search USA-specific job boards"""
        jobs = []
        
        # Search BuiltIn
        try:
            response = requests.get(
                f"https://builtin.com/search/jobs?q={quote_plus(query)}",
                headers=self.headers,
                timeout=10
            )
            soup = BeautifulSoup(response.text, "html.parser")
            
            for card in soup.select("div.job-card"):
                title_elem = card.select_one("a.job-title")
                company_elem = card.select_one("span.company-name")
                
                if title_elem:
                    jobs.append({
                        "title": title_elem.text.strip(),
                        "url": f"https://builtin.com{title_elem.get('href', '')}",
                        "company": company_elem.text.strip() if company_elem else "Unknown",
                        "location": "United States",
                        "source": "BuiltIn",
                        "snippet": "",
                        "skills": [],
                        "requirements": [],
                        "responsibilities": [],
                        "remote": False
                    })
        except Exception as e:
            print(f"BuiltIn search error: {e}")
        
        return jobs
    
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
        elif "dice.com" in url_lower:
            return "Dice"
        else:
            return "Web"
    
    def _extract_company(self, title: str, snippet: str) -> str:
        # Try from title
        parts = title.split(" at ")
        if len(parts) > 1:
            return parts[-1].strip()
        
        parts = title.split(" - ")
        if len(parts) > 1:
            return parts[-1].strip()
        
        # Try from snippet
        company_match = re.search(r'(?:at|@|for)\s+([A-Z][A-Za-z\s&]+)', snippet)
        if company_match:
            return company_match.group(1).strip()
        
        return "Unknown"
    
    def _extract_location(self, text: str, default_location: str = "") -> str:
        usa_cities = [
            "San Francisco", "New York", "Los Angeles", "Seattle", "Boston", "Chicago",
            "Austin", "Denver", "Atlanta", "Miami", "Dallas", "Houston", "Phoenix",
            "Portland", "San Diego", "Las Vegas", "Nashville", "Raleigh", "Charlotte"
        ]
        
        for city in usa_cities:
            if city.lower() in text.lower():
                return city
        
        if "remote" in text.lower():
            return "Remote"
        
        return default_location if default_location else "United States"
    
    def _extract_skills(self, text: str) -> List[str]:
        skill_keywords = [
            "python", "javascript", "typescript", "react", "node", "aws", "docker",
            "kubernetes", "sql", "git", "api", "rest", "graphql", "machine learning",
            "ai", "llm", "langchain", "pytorch", "tensorflow", "fastapi", "django",
            "azure", "gcp", "java", "go", "rust", "c++", "sql", "nosql", "redis",
            "kafka", "spark", "airflow", "dbt", "snowflake", "bigquery"
        ]
        
        found = []
        text_lower = text.lower()
        for skill in skill_keywords:
            if skill in text_lower:
                found.append(skill.title())
        
        return found[:8]
    
    def _is_remote(self, job: Dict) -> bool:
        text = f"{job.get('title', '')} {job.get('location', '')} {job.get('snippet', '')}".lower()
        return "remote" in text
    
    def _is_remote_text(self, text: str) -> bool:
        return "remote" in text.lower()
    
    def get_usa_locations(self) -> Dict:
        return self.usa_locations
