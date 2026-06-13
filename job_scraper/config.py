import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    serpapi_key: str = os.getenv("SERPAPI_KEY", "")
    
    # Search settings
    target_role: str = "Agentic AI Engineer"
    location: str = "Remote"
    num_results: int = 10
    
    # LLM settings
    model: str = "gpt-4o-mini"
    temperature: float = 0.3
    
    # Job sources
    sources: list = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = ["linkedin", "indeed", "glassdoor"]
