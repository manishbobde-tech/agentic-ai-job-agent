#!/usr/bin/env python3
"""
Enhanced Job Search Agent - Scrapes full job descriptions
"""

from job_scraper import JobSearchAgent, Config
from job_scraper.scraper import JobScraper
from rich.console import Console
from rich.panel import Panel
import json


def main():
    console = Console()
    config = Config(
        target_role="Agentic AI Engineer",
        location="Remote",
        num_results=5
    )
    
    # Step 1: Search for jobs
    console.print("\n[bold cyan]🤖 Enhanced Job Search Agent[/bold cyan]\n")
    agent = JobSearchAgent(config)
    jobs = agent.searcher.search_all_sources()
    
    if not jobs:
        console.print("[red]No jobs found.[/red]")
        return
    
    # Step 2: Scrape full descriptions
    console.print("\n[yellow]Step 2: Scraping full job descriptions...[/yellow]")
    scraper = JobScraper()
    
    for i, job in enumerate(jobs[:5], 1):
        url = job.get("url", "")
        source = job.get("source", "generic").lower()
        
        console.print(f"  → [{i}/5] Scraping: {job.get('title', 'Unknown')[:40]}...")
        
        description_data = scraper.scrape_job(url, source)
        
        if description_data:
            job["full_description"] = description_data.get("description", "")
            job["detailed_requirements"] = description_data.get("requirements", [])
            job["detailed_responsibilities"] = description_data.get("responsibilities", [])
    
    # Step 3: Display enhanced results
    console.print("\n[bold green]📊 Enhanced Results with Full Descriptions[/bold green]\n")
    
    for i, job in enumerate(jobs[:5], 1):
        title = job.get("title", "Unknown")
        company = job.get("company", "Unknown")
        full_desc = job.get("full_description", "No description available")
        requirements = job.get("detailed_requirements", [])
        responsibilities = job.get("detailed_responsibilities", [])
        
        content = f"[bold cyan]{title}[/bold cyan]\n"
        content += f"[dim]Company:[/dim] {company}\n"
        content += f"[dim]Source:[/dim] {job.get('source', 'Unknown')}\n\n"
        
        # Full description (truncated)
        if full_desc and full_desc != "No description available":
            desc_preview = full_desc[:1500] + "..." if len(full_desc) > 1500 else full_desc
            content += f"[bold]📝 Job Description:[/bold]\n{desc_preview}\n\n"
        
        # Requirements
        if requirements and requirements[0] != "See job description":
            content += "[bold]🎯 Requirements:[/bold]\n"
            for req in requirements[:5]:
                content += f"  • {req}\n"
        
        # Responsibilities
        if responsibilities and responsibilities[0] != "See job description":
            content += "\n[bold]💼 Responsibilities:[/bold]\n"
            for resp in responsibilities[:5]:
                content += f"  • {resp}\n"
        
        console.print(Panel(
            content,
            title=f"[blue]Job {i}[/blue]",
            border_style="green",
            padding=(1, 2)
        ))
    
    # Save enhanced results
    with open("enhanced_job_results.json", "w") as f:
        json.dump(jobs[:5], f, indent=2, default=str)
    
    console.print("\n[green]✅ Results saved to enhanced_job_results.json[/green]")


if __name__ == "__main__":
    main()
