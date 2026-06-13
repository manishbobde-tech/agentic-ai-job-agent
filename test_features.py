#!/usr/bin/env python3
"""
Test script for all features
"""

from job_scraper import JobSearchAgent, Config, JobFilter, FilterConfig, JobExporter
from job_scraper.notifications import EmailNotifier
from rich.console import Console
import json


def main():
    console = Console()
    console.print("\n[bold cyan]🧪 Testing All Features[/bold cyan]\n")
    
    # Test 1: Search jobs
    console.print("[yellow]Test 1: Searching for jobs...[/yellow]")
    config = Config(target_role="Agentic AI Engineer", num_results=5)
    agent = JobSearchAgent(config)
    jobs = agent.searcher.search_all_sources()
    console.print(f"  ✓ Found {len(jobs)} jobs\n")
    
    if not jobs:
        console.print("[red]No jobs found. Test failed.[/red]")
        return
    
    # Test 2: Filter by location
    console.print("[yellow]Test 2: Filtering by location (Remote)...[/yellow]")
    filter_config = FilterConfig(remote_only=True)
    job_filter = JobFilter(filter_config)
    remote_jobs = job_filter.filter_jobs(jobs)
    console.print(f"  ✓ Found {len(remote_jobs)} remote jobs\n")
    
    # Test 3: Filter by keywords
    console.print("[yellow]Test 3: Filtering by keyword (Python)...[/yellow]")
    filter_config = FilterConfig(keywords=["python"])
    job_filter = JobFilter(filter_config)
    python_jobs = job_filter.filter_jobs(jobs)
    console.print(f"  ✓ Found {len(python_jobs)} jobs mentioning Python\n")
    
    # Test 4: Export to CSV
    console.print("[yellow]Test 4: Exporting to CSV...[/yellow]")
    exporter = JobExporter()
    csv_path = exporter.export_csv(jobs, "test_jobs.csv")
    console.print(f"  ✓ CSV exported: {csv_path}\n")
    
    # Test 5: Export to JSON
    console.print("[yellow]Test 5: Exporting to JSON...[/yellow]")
    json_path = exporter.export_json(jobs, "test_jobs.json")
    console.print(f"  ✓ JSON exported: {json_path}\n")
    
    # Test 6: Export to Markdown
    console.print("[yellow]Test 6: Exporting to Markdown...[/yellow]")
    md_path = exporter.export_markdown(jobs, "test_jobs.md")
    console.print(f"  ✓ Markdown exported: {md_path}\n")
    
    # Test 7: Email notifier (without sending)
    console.print("[yellow]Test 7: Email notifier initialization...[/yellow]")
    notifier = EmailNotifier()
    new_jobs = notifier.get_new_jobs(jobs)
    console.print(f"  ✓ Email notifier initialized, {len(new_jobs)} new jobs detected\n")
    
    # Test 8: View statistics
    console.print("[yellow]Test 8: Statistics...[/yellow]")
    sources = {}
    skills = {}
    for job in jobs:
        source = job.get("source", "Unknown")
        sources[source] = sources.get(source, 0) + 1
        for skill in job.get("skills", []):
            if skill != "Not specified":
                skills[skill] = skills.get(skill, 0) + 1
    
    console.print(f"  ✓ Sources: {sources}")
    console.print(f"  ✓ Top skills: {dict(list(skills.items())[:5])}\n")
    
    console.print("[bold green]✅ All tests passed![/bold green]\n")


if __name__ == "__main__":
    main()
