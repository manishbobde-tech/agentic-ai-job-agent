from openai import OpenAI
from typing import Dict, List
from .config import Config


class JobParser:
    """Parses and summarizes job descriptions using LLM."""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key) if config.openai_api_key else None
    
    def extract_job_details(self, job: Dict) -> Dict:
        """Extract structured details from job listing."""
        text = f"{job.get('title', '')} {job.get('snippet', '')} {job.get('description', '')}"
        
        # Basic extraction using heuristics
        details = {
            "title": job.get("title", "Unknown"),
            "company": job.get("company", "Unknown"),
            "url": job.get("url", ""),
            "source": job.get("source", "Unknown"),
            "skills": self._extract_skills(text),
            "experience": self._extract_experience(text),
            "responsibilities": self._extract_responsibilities(text),
            "requirements": self._extract_requirements(text)
        }
        
        return details
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract mentioned skills."""
        skill_keywords = [
            "python", "langchain", "llamaindex", "openai", "anthropic",
            "rag", "vector database", "embeddings", "prompt engineering",
            "fine-tuning", "transformers", "hugging face", "pytorch", "tensorflow",
            "docker", "kubernetes", "aws", "gcp", "azure",
            "agent", "agentic", "multi-agent", "autonomous",
            "machine learning", "deep learning", "nlp", "natural language processing"
        ]
        
        found_skills = []
        text_lower = text.lower()
        for skill in skill_keywords:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return found_skills if found_skills else ["Not specified"]
    
    def _extract_experience(self, text: str) -> str:
        """Extract experience requirements."""
        import re
        patterns = [
            r'(\d+[\+]?\s*(?:years?|yrs?))',
            r'experience:\s*(\d+)',
            r'(\d+)\s*to\s*(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "Not specified"
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities."""
        # Simplified extraction
        responsibilities = []
        if "design" in text.lower():
            responsibilities.append("Design systems")
        if "build" in text.lower() or "develop" in text.lower():
            responsibilities.append("Build/Develop solutions")
        if "deploy" in text.lower():
            responsibilities.append("Deploy to production")
        if "collaborate" in text.lower():
            responsibilities.append("Collaborate with teams")
        
        return responsibilities if responsibilities else ["See job description"]
    
    def _extract_requirements(self, text: str) -> List[str]:
        """Extract job requirements."""
        requirements = []
        if "python" in text.lower():
            requirements.append("Python proficiency")
        if "llm" in text.lower() or "large language model" in text.lower():
            requirements.append("LLM experience")
        if "agent" in text.lower():
            requirements.append("Agent development experience")
        
        return requirements if requirements else ["See job description"]
    
    def summarize_with_llm(self, jobs: List[Dict]) -> List[Dict]:
        """Use LLM to create better summaries."""
        if not self.client:
            return jobs
        
        summarized = []
        for job in jobs:
            prompt = f"""Analyze this job listing and provide:
1. A one-line summary
2. Key requirements (top 3)
3. What makes this role unique
4. Skills match for Agentic AI Engineer

Job: {job.get('title', 'Unknown')}
Snippet: {job.get('snippet', 'No description')}

Return as JSON with keys: summary, key_requirements, unique_aspects, skills_match"""

            try:
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    temperature=self.config.temperature,
                    messages=[
                        {"role": "system", "content": "You are a job analysis expert."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                import json
                analysis = json.loads(response.choices[0].message.content)
                job["llm_analysis"] = analysis
            except Exception as e:
                job["llm_analysis"] = {"error": str(e)}
            
            summarized.append(job)
        
        return summarized
