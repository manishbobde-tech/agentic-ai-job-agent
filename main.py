#!/usr/bin/env python3
"""
Agentic AI Job Search Agent
Scans job listings for Agentic AI Engineer positions.
"""

from job_scraper import JobSearchAgent, Config


def main():
    """Main entry point."""
    # Initialize config
    config = Config(
        target_role="Agentic AI Engineer",
        location="Remote",
        num_results=10
    )
    
    # Create and run agent
    agent = JobSearchAgent(config)
    jobs = agent.run()
    
    # Optional: Save results to file
    if jobs:
        import json
        with open("job_results.json", "w") as f:
            json.dump(jobs, f, indent=2, default=str)
        print(f"\n✅ Results saved to job_results.json")


if __name__ == "__main__":
    main()
