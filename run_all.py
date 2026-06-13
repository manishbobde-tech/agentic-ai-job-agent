#!/usr/bin/env python3
"""
Run the complete job search workflow automatically
"""

from job_scraper import JobSearchAgent, Config, JobFilter, FilterConfig, JobExporter
from job_scraper.scraper import JobScraper
from job_scraper.notifications import EmailNotifier
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import json


def main():
    console = Console()
    console.print("\n[bold cyan]🤖 Agentic AI Job Search Agent - Full Run[/bold cyan]\n")
    
    # Step 1: Search for jobs
    console.print("[yellow]Step 1: Searching for Agentic AI Engineer jobs...[/yellow]")
    config = Config(target_role="Agentic AI Engineer", num_results=10)
    agent = JobSearchAgent(config)
    jobs = agent.searcher.search_all_sources()
    console.print(f"  ✓ Found {len(jobs)} jobs\n")
    
    if not jobs:
        console.print("[red]No jobs found.[/red]")
        return
    
    # Step 2: Scrape full descriptions
    console.print("[yellow]Step 2: Scraping full job descriptions...[/yellow]")
    scraper = JobScraper()
    for i, job in enumerate(jobs[:5], 1):
        console.print(f"  → [{i}/5] Scraping: {job.get('title', 'Unknown')[:40]}...")
        url = job.get("url", "")
        source = job.get("source", "generic").lower()
        description_data = scraper.scrape_job(url, source)
        if description_data:
            job["full_description"] = description_data.get("description", "")
            job["detailed_requirements"] = description_data.get("requirements", [])
    console.print("  ✓ Done\n")
    
    # Step 3: Display results
    console.print("[yellow]Step 3: Displaying results...[/yellow]\n")
    
    table = Table(title="Agentic AI Engineer Jobs", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Position", style="cyan", max_width=35)
    table.add_column("Company", style="green", max_width=25)
    table.add_column("Source", style="yellow")
    table.add_column("Skills", style="blue", max_width=30)
    
    for i, job in enumerate(jobs, 1):
        skills = ", ".join(job.get("skills", [])[:3])
        table.add_row(
            str(i),
            job.get("title", "Unknown")[:35],
            job.get("company", "Unknown")[:25],
            job.get("source", "Unknown"),
            skills[:30]
        )
    
    console.print(table)
    
    # Step 4: Export
    console.print("\n[yellow]Step 4: Exporting results...[/yellow]")
    exporter = JobExporter()
    
    csv_path = exporter.export_csv(jobs, "agentic_ai_jobs.csv")
    console.print(f"  ✓ CSV: {csv_path}")
    
    json_path = exporter.export_json(jobs, "agentic_ai_jobs.json")
    console.print(f"  ✓ JSON: {json_path}")
    
    md_path = exporter.export_markdown(jobs, "agentic_ai_jobs.md")
    console.print(f"  ✓ Markdown: {md_path}")
    
    # Step 5: Show top jobs with details
    console.print("\n[yellow]Step 5: Top 3 Jobs with Full Details[/yellow]\n")
    
    for i, job in enumerate(jobs[:3], 1):
        title = job.get("title", "Unknown")
        company = job.get("company", "Unknown")
        full_desc = job.get("full_description", "No description available")
        requirements = job.get("detailed_requirements", [])
        
        content = f"[bold cyan]{title}[/bold cyan]\n"
        content += f"[dim]Company:[/dim] {company}\n"
        content += f"[dim]Source:[/dim] {job.get('source', 'Unknown')}\n\n"
        
        if full_desc and full_desc != "No description available":
            desc_preview = full_desc[:800] + "..." if len(full_desc) > 800 else full_desc
            content += f"[bold]📝 Job Description:[/bold]\n{desc_preview}\n\n"
        
        if requirements and requirements[0] != "See job description":
            content += "[bold]🎯 Requirements:[/bold]\n"
            for req in requirements[:3]:
                content += f"  • {req}\n"
        
        console.print(Panel(
            content,
            title=f"[blue]Top Job {i}[/blue]",
            border_style="green",
            padding=(1, 2)
        ))
    
    # Step 6: Statistics
    console.print("\n[bold green]📊 Statistics[/bold green]\n")
    
    sources = {}
    for job in jobs:
        source = job.get("source", "Unknown")
        sources[source] = sources.get(source, 0) + 1
    
    stats_table = Table(title="Jobs by Source", show_header=True)
    stats_table.add_column("Source", style="cyan")
    stats_table.add_column("Count", style="green")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        stats_table.add_row(source, str(count))
    console.print(stats_table)
    
    console.print("\n[bold green]✅ All done! Files saved:[/bold green]")
    console.print("  • agentic_ai_jobs.csv")
    console.print("  • agentic_ai_jobs.json")
    console.print("  • agentic_ai_jobs.md\n")


if __name__ == "__main__":
    main()
