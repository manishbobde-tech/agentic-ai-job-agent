import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import re
import time


class JobScraper:
    """Scrapes full job descriptions from URLs."""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    
    def scrape_linkedin(self, url: str) -> Optional[Dict]:
        """Scrape LinkedIn job description."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            description_div = soup.select_one("div.show-more-less-html__markup")
            if description_div:
                return {
                    "description": description_div.get_text(separator="\n", strip=True),
                    "requirements": self._extract_requirements(description_div.get_text()),
                    "responsibilities": self._extract_responsibilities(description_div.get_text())
                }
        except Exception as e:
            print(f"LinkedIn scrape error: {e}")
        return None
    
    def scrape_indeed(self, url: str) -> Optional[Dict]:
        """Scrape Indeed job description."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            description_div = soup.select_one("div.job-description")
            if description_div:
                return {
                    "description": description_div.get_text(separator="\n", strip=True),
                    "requirements": self._extract_requirements(description_div.get_text()),
                    "responsibilities": self._extract_responsibilities(description_div.get_text())
                }
        except Exception as e:
            print(f"Indeed scrape error: {e}")
        return None
    
    def scrape_generic(self, url: str) -> Optional[Dict]:
        """Generic job page scraper."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Try common job description selectors
            selectors = [
                "div.job-description",
                "div.description",
                "section.job-description",
                "div.posting-requirements",
                "#job-description"
            ]
            
            for selector in selectors:
                desc_div = soup.select_one(selector)
                if desc_div:
                    return {
                        "description": desc_div.get_text(separator="\n", strip=True),
                        "requirements": self._extract_requirements(desc_div.get_text()),
                        "responsibilities": self._extract_responsibilities(desc_div.get_text())
                    }
            
            # Fallback: get main content
            main = soup.select_one("main") or soup.select_one("article")
            if main:
                return {
                    "description": main.get_text(separator="\n", strip=True)[:2000],
                    "requirements": self._extract_requirements(main.get_text()),
                    "responsibilities": self._extract_responsibilities(main.get_text())
                }
        except Exception as e:
            print(f"Generic scrape error: {e}")
        return None
    
    def scrape_job(self, url: str, source: str = "generic") -> Optional[Dict]:
        """Scrape job based on source."""
        scrapers = {
            "linkedin": self.scrape_linkedin,
            "indeed": self.scrape_indeed,
            "generic": self.scrape_generic
        }
        
        scraper = scrapers.get(source, self.scrape_generic)
        result = scraper(url)
        
        # Add delay to be respectful
        time.sleep(1)
        
        return result
    
    def _extract_requirements(self, text: str) -> list:
        """Extract requirements from text."""
        requirements = []
        
        # Common requirement patterns
        patterns = [
            r'(?:requirements?|qualifications?|must have)[:\s]*(.*?)(?:\n\n|\Z)',
            r'(?:experience|knowledge) (?:in|with) (.+?)(?:\n|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            requirements.extend(matches[:5])
        
        # Fallback: extract bullet points
        if not requirements:
            bullets = re.findall(r'[•\-\*]\s*(.+?)(?:\n|$)', text)
            requirements = [b.strip() for b in bullets[:5]]
        
        return requirements if requirements else ["See job description"]
    
    def _extract_responsibilities(self, text: str) -> list:
        """Extract responsibilities from text."""
        responsibilities = []
        
        # Common responsibility keywords
        keywords = [
            "design", "build", "develop", "implement", "deploy",
            "maintain", "optimize", "collaborate", "lead", "mentor"
        ]
        
        sentences = text.split('\n')
        for sentence in sentences:
            for keyword in keywords:
                if keyword in sentence.lower() and len(sentence) < 200:
                    responsibilities.append(sentence.strip())
                    break
            if len(responsibilities) >= 5:
                break
        
        return responsibilities if responsibilities else ["See job description"]
