import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import re


class JobSearcher:
    """Searches job platforms for relevant listings."""
    
    def __init__(self, config):
        self.config = config
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
    
    def search_google_jobs(self, query: str) -> List[Dict]:
        """Search Google for job listings."""
        jobs = []
        search_url = "https://www.google.com/search"
        params = {
            "q": f"{query} jobs",
            "num": self.config.num_results
        }
        
        try:
            response = requests.get(search_url, params=params, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            for result in soup.select("div.g"):
                title_elem = result.select_one("h3")
                link_elem = result.select_one("a")
                snippet_elem = result.select_one("div.VwiC3b")
                
                if title_elem and link_elem:
                    jobs.append({
                        "title": title_elem.text,
                        "url": link_elem["href"],
                        "snippet": snippet_elem.text if snippet_elem else "",
                        "source": "Google"
                    })
        except Exception as e:
            print(f"Google search error: {e}")
        
        return jobs
    
    def search_indeed(self, query: str) -> List[Dict]:
        """Search Indeed for job listings."""
        jobs = []
        search_url = f"https://www.indeed.com/jobs?q={query.replace(' ', '+')}&l=Remote"
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            for card in soup.select("div.job_seen_beacon"):
                title_elem = card.select_one("h2.jobTitle a")
                company_elem = card.select_one("span.companyName")
                snippet_elem = card.select_one("div.job-snippet")
                
                if title_elem:
                    jobs.append({
                        "title": title_elem.text.strip(),
                        "url": f"https://www.indeed.com{title_elem.get('href', '')}",
                        "company": company_elem.text.strip() if company_elem else "Unknown",
                        "snippet": snippet_elem.text.strip() if snippet_elem else "",
                        "source": "Indeed"
                    })
        except Exception as e:
            print(f"Indeed search error: {e}")
        
        return jobs
    
    def search_linkedin(self, query: str) -> List[Dict]:
        """Search LinkedIn for job listings (limited without auth)."""
        jobs = []
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={query.replace(' ', '%20')}&location=Remote"
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            for card in soup.select("div.base-card"):
                title_elem = card.select_one("h3.base-search-card__title")
                company_elem = card.select_one("h4.base-search-card__subtitle")
                link_elem = card.select_one("a.base-card__full-link")
                
                if title_elem:
                    jobs.append({
                        "title": title_elem.text.strip(),
                        "url": link_elem["href"] if link_elem else "",
                        "company": company_elem.text.strip() if company_elem else "Unknown",
                        "snippet": "",
                        "source": "LinkedIn"
                    })
        except Exception as e:
            print(f"LinkedIn search error: {e}")
        
        return jobs
    
    def search_all_sources(self) -> List[Dict]:
        """Search all configured sources."""
        all_jobs = []
        query = self.config.target_role
        
        print(f"🔍 Searching for '{query}' jobs...")
        
        # Search Google
        print("  → Searching Google...")
        all_jobs.extend(self.search_google_jobs(query))
        
        # Search Indeed
        print("  → Searching Indeed...")
        all_jobs.extend(self.search_indeed(query))
        
        # Search LinkedIn
        print("  → Searching LinkedIn...")
        all_jobs.extend(self.search_linkedin(query))
        
        # Deduplicate by title
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            title_key = job["title"].lower()
            if title_key not in seen:
                seen.add(title_key)
                unique_jobs.append(job)
        
        print(f"✅ Found {len(unique_jobs)} unique job listings")
        return unique_jobs[:self.config.num_results]
