import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import re
import time


class JobScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    
    def scrape_job(self, url: str, source: str = "generic") -> Optional[Dict]:
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            description = self._extract_description(soup)
            requirements = self._extract_requirements(description)
            responsibilities = self._extract_responsibilities(description)
            
            return {
                "description": description[:5000],
                "requirements": requirements[:10],
                "responsibilities": responsibilities[:10]
            }
        except Exception as e:
            print(f"Scrape error: {e}")
            return None
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        selectors = [
            "div.show-more-less-html__markup",
            "div.job-description",
            "div.description",
            "section.job-description",
            "#job-description",
            "div.posting-requirements",
            "article"
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(separator="\n", strip=True)
        
        main = soup.select_one("main") or soup.select_one("body")
        if main:
            return main.get_text(separator="\n", strip=True)[:5000]
        
        return ""
    
    def _extract_requirements(self, text: str) -> list:
        requirements = []
        
        lines = text.split("\n")
        in_requirements = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            lower = line.lower()
            if any(kw in lower for kw in ["requirements", "qualifications", "must have", "what you need"]):
                in_requirements = True
                continue
            
            if any(kw in lower for kw in ["responsibilities", "what you'll do", "about the role"]):
                in_requirements = False
                continue
            
            if in_requirements and len(line) > 10 and len(line) < 200:
                clean = re.sub(r'^[\•\-\*]\s*', '', line)
                if clean:
                    requirements.append(clean)
        
        if not requirements:
            bullets = re.findall(r'[•\-\*]\s*(.+?)(?:\n|$)', text)
            requirements = [b.strip() for b in bullets if len(b.strip()) > 10][:10]
        
        return requirements
    
    def _extract_responsibilities(self, text: str) -> list:
        responsibilities = []
        
        lines = text.split("\n")
        in_responsibilities = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            lower = line.lower()
            if any(kw in lower for kw in ["responsibilities", "what you'll do", "what you will do", "about the role"]):
                in_responsibilities = True
                continue
            
            if any(kw in lower for kw in ["requirements", "qualifications", "must have", "benefits"]):
                in_responsibilities = False
                continue
            
            if in_responsibilities and len(line) > 10 and len(line) < 200:
                clean = re.sub(r'^[\•\-\*]\s*', '', line)
                if clean:
                    responsibilities.append(clean)
        
        return responsibilities
