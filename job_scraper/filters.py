import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class FilterConfig:
    """Configuration for job filtering."""
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    locations: List[str] = None
    remote_only: bool = False
    exclude_locations: List[str] = None
    keywords: List[str] = None
    exclude_keywords: List[str] = None
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    
    def __post_init__(self):
        if self.locations is None:
            self.locations = []
        if self.exclude_locations is None:
            self.exclude_locations = []
        if self.keywords is None:
            self.keywords = []
        if self.exclude_keywords is None:
            self.exclude_keywords = []


class JobFilter:
    """Filters jobs based on various criteria."""
    
    def __init__(self, config: FilterConfig = None):
        self.config = config or FilterConfig()
    
    def filter_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Apply all configured filters to job list."""
        filtered = jobs
        
        if self.config.min_salary or self.config.max_salary:
            filtered = self._filter_by_salary(filtered)
        
        if self.config.locations:
            filtered = self._filter_by_location(filtered)
        
        if self.config.remote_only:
            filtered = self._filter_remote(filtered)
        
        if self.config.exclude_locations:
            filtered = self._exclude_locations(filtered)
        
        if self.config.keywords:
            filtered = self._filter_by_keywords(filtered)
        
        if self.config.exclude_keywords:
            filtered = self._exclude_keywords(filtered)
        
        if self.config.min_experience or self.config.max_experience:
            filtered = self._filter_by_experience(filtered)
        
        return filtered
    
    def _filter_by_salary(self, jobs: List[Dict]) -> List[Dict]:
        """Filter jobs by salary range."""
        filtered = []
        for job in jobs:
            salary = self._extract_salary(job)
            if salary is None:
                filtered.append(job)  # Include jobs without salary info
                continue
            
            if self.config.min_salary and salary < self.config.min_salary:
                continue
            if self.config.max_salary and salary > self.config.max_salary:
                continue
            
            filtered.append(job)
        
        return filtered
    
    def _extract_salary(self, job: Dict) -> Optional[int]:
        """Extract salary from job data."""
        text = f"{job.get('title', '')} {job.get('snippet', '')} {job.get('full_description', '')}"
        
        # Common salary patterns
        patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:k|K)?',
            r'£(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:k|K)?',
            r'€(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:k|K)?',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:USD|GBP|EUR)',
            r'salary[:\s]*[\$£€]?(\d{1,3}(?:,\d{3})*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                salary_str = match.group(1).replace(',', '')
                try:
                    salary = int(float(salary_str))
                    # Handle k notation
                    if 'k' in pattern.lower():
                        salary *= 1000
                    return salary
                except ValueError:
                    continue
        
        return None
    
    def _filter_by_location(self, jobs: List[Dict]) -> List[Dict]:
        """Filter jobs by location."""
        filtered = []
        for job in jobs:
            job_location = job.get('location', '').lower()
            job_text = f"{job.get('title', '')} {job.get('snippet', '')} {job.get('full_description', '')}".lower()
            
            for loc in self.config.locations:
                if loc.lower() in job_text or loc.lower() in job_location:
                    filtered.append(job)
                    break
        
        return filtered
    
    def _filter_remote(self, jobs: List[Dict]) -> List[Dict]:
        """Filter for remote jobs only."""
        remote_keywords = ['remote', 'work from home', 'wfh', 'distributed', 'anywhere']
        
        return [
            job for job in jobs
            if any(kw in f"{job.get('title', '')} {job.get('snippet', '')} {job.get('full_description', '')}".lower() 
                   for kw in remote_keywords)
        ]
    
    def _exclude_locations(self, jobs: List[Dict]) -> List[Dict]:
        """Exclude jobs from specific locations."""
        filtered = []
        for job in jobs:
            job_text = f"{job.get('title', '')} {job.get('snippet', '')} {job.get('full_description', '')}".lower()
            
            excluded = False
            for loc in self.config.exclude_locations:
                if loc.lower() in job_text:
                    excluded = True
                    break
            
            if not excluded:
                filtered.append(job)
        
        return filtered
    
    def _filter_by_keywords(self, jobs: List[Dict]) -> List[Dict]:
        """Filter jobs containing specific keywords."""
        filtered = []
        for job in jobs:
            job_text = f"{job.get('title', '')} {job.get('snippet', '')} {job.get('full_description', '')}".lower()
            
            if any(kw.lower() in job_text for kw in self.config.keywords):
                filtered.append(job)
        
        return filtered
    
    def _exclude_keywords(self, jobs: List[Dict]) -> List[Dict]:
        """Exclude jobs containing specific keywords."""
        filtered = []
        for job in jobs:
            job_text = f"{job.get('title', '')} {job.get('snippet', '')} {job.get('full_description', '')}".lower()
            
            if not any(kw.lower() in job_text for kw in self.config.exclude_keywords):
                filtered.append(job)
        
        return filtered
    
    def _filter_by_experience(self, jobs: List[Dict]) -> List[Dict]:
        """Filter jobs by experience requirements."""
        filtered = []
        for job in jobs:
            exp = self._extract_experience_years(job)
            
            if exp is None:
                filtered.append(job)  # Include jobs without experience info
                continue
            
            if self.config.min_experience and exp < self.config.min_experience:
                continue
            if self.config.max_experience and exp > self.config.max_experience:
                continue
            
            filtered.append(job)
        
        return filtered
    
    def _extract_experience_years(self, job: Dict) -> Optional[int]:
        """Extract experience years from job data."""
        text = f"{job.get('title', '')} {job.get('snippet', '')} {job.get('full_description', '')}"
        
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)',
            r'experience[:\s]*(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:to|-)\s*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:years?|yrs?)\s*(?:minimum|min|or more)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return None
