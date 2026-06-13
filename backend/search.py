import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import json
from pathlib import Path


class JobSearcher:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
    
    def search(self, query: str, num_results: int = 20) -> List[Dict]:
        all_jobs = []
        
        all_jobs.extend(self._search_google(query))
        all_jobs.extend(self._search_linkedin(query))
        
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            title_key = job["title"].lower().strip()
            if title_key not in seen:
                seen.add(title_key)
                unique_jobs.append(job)
        
        result = unique_jobs[:num_results]
        
        with open("cached_jobs.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
        
        return result
    
    def _search_google(self, query: str) -> List[Dict]:
        jobs = []
        try:
            response = requests.get(
                "https://www.google.com/search",
                params={"q": f"{query} jobs", "num": 15},
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
                    
                    jobs.append({
                        "title": title_elem.text,
                        "url": url,
                        "snippet": snippet_elem.text if snippet_elem else "",
                        "source": self._detect_source(url),
                        "company": self._extract_company(title_elem.text),
                        "location": self._extract_location(snippet_elem.text if snippet_elem else ""),
                        "skills": [],
                        "requirements": [],
                        "responsibilities": []
                    })
        except Exception as e:
            print(f"Google search error: {e}")
        return jobs
    
    def _search_linkedin(self, query: str) -> List[Dict]:
        jobs = []
        try:
            response = requests.get(
                f"https://www.linkedin.com/jobs/search/?keywords={query.replace(' ', '%20')}&location=Remote",
                headers=self.headers,
                timeout=10
            )
            soup = BeautifulSoup(response.text, "html.parser")
            
            for card in soup.select("div.base-card"):
                title_elem = card.select_one("h3.base-search-card__title")
                company_elem = card.select_one("h4.base-search-card__subtitle")
                link_elem = card.select_one("a.base-card__full-link")
                location_elem = card.select_one("span.job-search-card__location")
                
                if title_elem:
                    jobs.append({
                        "title": title_elem.text.strip(),
                        "url": link_elem["href"] if link_elem else "",
                        "company": company_elem.text.strip() if company_elem else "Unknown",
                        "location": location_elem.text.strip() if location_elem else "Not specified",
                        "source": "LinkedIn",
                        "snippet": "",
                        "skills": [],
                        "requirements": [],
                        "responsibilities": []
                    })
        except Exception as e:
            print(f"LinkedIn search error: {e}")
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
        else:
            return "Web"
    
    def _extract_company(self, title: str) -> str:
        parts = title.split(" at ")
        if len(parts) > 1:
            return parts[-1].strip()
        parts = title.split(" - ")
        if len(parts) > 1:
            return parts[-1].strip()
        return "Unknown"
    
    def _extract_location(self, text: str) -> str:
        location_keywords = ["Remote", "London", "New York", "San Francisco", "Berlin", "Paris", "Tokyo"]
        for keyword in location_keywords:
            if keyword.lower() in text.lower():
                return keyword
        return "Not specified"
