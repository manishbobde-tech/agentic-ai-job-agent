from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()


class ResumeMatcher:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY", "")
        self.client = OpenAI(api_key=api_key) if api_key else None
    
    def analyze_match(self, resume_text: str, job_description: str, job_title: str = "") -> dict:
        if not self.client:
            return self._analyze_without_ai(resume_text, job_description)
        
        prompt = f"""Analyze how well this resume matches the job description.

Job Title: {job_title}
Job Description: {job_description[:3000]}

Resume:
{resume_text[:3000]}

Provide analysis in JSON format:
{{
    "match_score": 0-100,
    "summary": "brief summary of match",
    "matched_skills": ["skill1", "skill2"],
    "missing_skills": ["skill1", "skill2"],
    "strengths": ["strength1", "strength2"],
    "improvements": ["improvement1", "improvement2"],
    "keywords_to_add": ["keyword1", "keyword2"]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.3,
                messages=[
                    {"role": "system", "content": "You are an expert resume analyzer and career coach. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e), "match_score": 0}
    
    def tailor_resume(self, resume_text: str, job_description: str, job_title: str = "", instructions: str = "") -> dict:
        if not self.client:
            return {"error": "OpenAI API key required for resume tailoring", "tailored_resume": resume_text}
        
        prompt = f"""Tailor this resume to better match the job description. 
Make itATS-friendly and highlight relevant experience.

Job Title: {job_title}
Job Description: {job_description[:3000]}

Additional Instructions: {instructions}

Original Resume:
{resume_text[:3000]}

Provide the tailored resume and explanation in JSON format:
{{
    "tailored_resume": "the full tailored resume text",
    "changes_made": ["change1", "change2"],
    "tips": ["tip1", "tip2"]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.7,
                messages=[
                    {"role": "system", "content": "You are an expert resume writer. Create ATS-friendly resumes. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e), "tailored_resume": resume_text}
    
    def _analyze_without_ai(self, resume_text: str, job_description: str) -> dict:
        resume_lower = resume_text.lower()
        job_lower = job_description.lower()
        
        common_tech = [
            "python", "javascript", "typescript", "react", "node", "aws", "docker",
            "kubernetes", "sql", "git", "api", "rest", "graphql", "machine learning",
            "ai", "llm", "langchain", "fastapi", "django", "flask", "pytorch", "tensorflow"
        ]
        
        matched = [t for t in common_tech if t in resume_lower and t in job_lower]
        missing = [t for t in common_tech if t not in resume_lower and t in job_lower]
        
        score = min(100, len(matched) * 10 + 20) if matched else 30
        
        return {
            "match_score": score,
            "summary": f"Found {len(matched)} matching skills. {len(missing)} skills to add.",
            "matched_skills": matched,
            "missing_skills": missing,
            "strengths": ["Experience relevant to role"] if matched else [],
            "improvements": [f"Add {skill} to resume" for skill in missing[:5]],
            "keywords_to_add": missing[:5]
        }
