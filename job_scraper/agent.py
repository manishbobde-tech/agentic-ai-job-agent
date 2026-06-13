from .config import Config
from .search import JobSearcher
from .parser import JobParser
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown


class JobSearchAgent:
    """
    Agent that searches for Agentic AI Engineer jobs,
    parses JDs, and provides clear analysis.
    """
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.searcher = JobSearcher(self.config)
        self.parser = JobParser(self.config)
        self.console = Console()
    
    def run(self) -> List[Dict]:
        """Execute the job search agent."""
        self.console.print("\n[bold cyan]🤖 Agentic AI Job Search Agent[/bold cyan]\n")
        
        # Step 1: Search for jobs
        self.console.print("[yellow]Step 1: Searching job platforms...[/yellow]")
        jobs = self.searcher.search_all_sources()
        
        if not jobs:
            self.console.print("[red]No jobs found. Try adjusting your search.[/red]")
            return []
        
        # Step 2: Parse and extract details
        self.console.print("\n[yellow]Step 2: Parsing job details...[/yellow]")
        parsed_jobs = [self.parser.extract_job_details(job) for job in jobs]
        
        # Step 3: LLM analysis (if API key available)
        if self.config.openai_api_key:
            self.console.print("\n[yellow]Step 3: AI-powered analysis...[/yellow]")
            analyzed_jobs = self.parser.summarize_with_llm(parsed_jobs)
        else:
            self.console.print("\n[yellow]Step 3: Skipping LLM analysis (no API key)[/yellow]")
            analyzed_jobs = parsed_jobs
        
        # Step 4: Display results
        self._display_results(analyzed_jobs)
        
        return analyzed_jobs
    
    def _display_results(self, jobs: List[Dict]):
        """Display job results in a beautiful format."""
        self.console.print(f"\n[bold green]📊 Found {len(jobs)} Agentic AI Engineer positions[/bold green]\n")
        
        for i, job in enumerate(jobs, 1):
            # Create job panel
            title = job.get("title", "Unknown Position")
            company = job.get("company", "Unknown Company")
            source = job.get("source", "Unknown")
            url = job.get("url", "")
            
            content = f"[bold]{title}[/bold]\n"
            content += f"[dim]Company:[/dim] {company}\n"
            content += f"[dim]Source:[/dim] {source}\n"
            if url:
                content += f"[dim]URL:[/dim] {url}\n"
            
            # Skills
            skills = job.get("skills", [])
            if skills:
                content += f"\n[bold]🎯 Required Skills:[/bold]\n"
                for skill in skills[:5]:
                    content += f"  • {skill}\n"
            
            # Experience
            exp = job.get("experience", "Not specified")
            content += f"\n[bold]📈 Experience:[/bold] {exp}\n"
            
            # LLM Analysis (if available)
            analysis = job.get("llm_analysis", {})
            if analysis and "summary" in analysis:
                content += f"\n[bold]📝 Summary:[/bold] {analysis['summary']}\n"
                
                if "key_requirements" in analysis:
                    content += f"\n[bold]🔑 Key Requirements:[/bold]\n"
                    for req in analysis["key_requirements"][:3]:
                        content += f"  • {req}\n"
                
                if "unique_aspects" in analysis:
                    content += f"\n[bold]✨ What Makes It Unique:[/bold] {analysis['unique_aspects']}\n"
            
            # Display panel
            self.console.print(Panel(
                content,
                title=f"[cyan]Job {i}[/cyan]",
                border_style="blue",
                padding=(1, 2)
            ))
        
        # Summary table
        self._display_summary_table(jobs)
    
    def _display_summary_table(self, jobs: List[Dict]):
        """Display a summary table of all jobs."""
        table = Table(title="📋 Quick Summary", show_header=True, header_style="bold magenta")
        
        table.add_column("#", style="dim", width=3)
        table.add_column("Position", style="cyan")
        table.add_column("Company", style="green")
        table.add_column("Source", style="yellow")
        table.add_column("Key Skill", style="blue")
        
        for i, job in enumerate(jobs, 1):
            skills = job.get("skills", [])
            top_skill = skills[0] if skills else "N/A"
            
            table.add_row(
                str(i),
                job.get("title", "Unknown")[:40],
                job.get("company", "Unknown")[:20],
                job.get("source", "Unknown"),
                top_skill
            )
        
        self.console.print(table)
