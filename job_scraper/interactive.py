from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.panel import Panel
from typing import List, Dict, Optional
from .config import Config
from .agent import JobSearchAgent
from .filters import JobFilter, FilterConfig
from .exporter import JobExporter
from .notifications import EmailNotifier
from .scraper import JobScraper


class InteractiveCLI:
    """Interactive command-line interface for the job search agent."""
    
    def __init__(self):
        self.console = Console()
        self.config = Config()
        self.jobs: List[Dict] = []
        self.filtered_jobs: List[Dict] = []
    
    def run(self):
        """Run the interactive CLI."""
        self.console.print("\n[bold cyan]🤖 Agentic AI Job Search Agent - Interactive Mode[/bold cyan]\n")
        
        while True:
            self._show_menu()
            choice = Prompt.ask("\n[yellow]Select an option[/yellow]", 
                              choices=["1", "2", "3", "4", "5", "6", "7", "8", "0"])
            
            if choice == "0":
                self.console.print("[green]Goodbye! 👋[/green]")
                break
            
            self._handle_choice(choice)
    
    def _show_menu(self):
        """Display the main menu."""
        table = Table(show_header=False, border_style="cyan")
        table.add_column("Option", style="bold")
        table.add_column("Description")
        
        table.add_row("1", "🔍 Search for jobs")
        table.add_row("2", "🎯 Filter jobs")
        table.add_row("3", "📊 View current results")
        table.add_row("4", "💾 Export to CSV/Excel/JSON")
        table.add_row("5", "📧 Set up email notifications")
        table.add_row("6", "⚙️  Configure settings")
        table.add_row("7", "🔄 Scrape full job descriptions")
        table.add_row("8", "📈 View statistics")
        table.add_row("0", "🚪 Exit")
        
        self.console.print(Panel(table, title="[bold]Main Menu[/bold]", border_style="blue"))
    
    def _handle_choice(self, choice: str):
        """Handle menu choice."""
        handlers = {
            "1": self._search_jobs,
            "2": self._filter_jobs,
            "3": self._view_results,
            "4": self._export_results,
            "5": self._setup_notifications,
            "6": self._configure_settings,
            "7": self._scrape_descriptions,
            "8": self._view_statistics,
        }
        
        handler = handlers.get(choice)
        if handler:
            handler()
    
    def _search_jobs(self):
        """Search for jobs."""
        self.console.print("\n[bold]🔍 Job Search[/bold]\n")
        
        role = Prompt.ask("Target role", default=self.config.target_role)
        location = Prompt.ask("Location (or 'Remote')", default=self.config.location)
        num_results = IntPrompt.ask("Number of results", default=self.config.num_results)
        
        self.config.target_role = role
        self.config.location = location
        self.config.num_results = num_results
        
        agent = JobSearchAgent(self.config)
        self.jobs = agent.searcher.search_all_sources()
        self.filtered_jobs = self.jobs.copy()
        
        self.console.print(f"\n[green]✅ Found {len(self.jobs)} jobs![/green]")
    
    def _filter_jobs(self):
        """Filter jobs based on criteria."""
        if not self.jobs:
            self.console.print("[red]No jobs to filter. Search first![/red]")
            return
        
        self.console.print("\n[bold]🎯 Job Filtering[/bold]\n")
        
        filter_config = FilterConfig()
        
        # Location filter
        if Confirm.ask("Filter by location?"):
            locations = Prompt.ask("Enter locations (comma-separated)")
            filter_config.locations = [loc.strip() for loc in locations.split(",")]
        
        # Remote filter
        if Confirm.ask("Remote jobs only?"):
            filter_config.remote_only = True
        
        # Salary filter
        if Confirm.ask("Filter by salary?"):
            min_salary = Prompt.ask("Minimum salary (or press Enter to skip)", default="")
            max_salary = Prompt.ask("Maximum salary (or press Enter to skip)", default="")
            
            if min_salary:
                filter_config.min_salary = int(min_salary.replace(",", "").replace("$", ""))
            if max_salary:
                filter_config.max_salary = int(max_salary.replace(",", "").replace("$", ""))
        
        # Keywords filter
        if Confirm.ask("Filter by keywords?"):
            keywords = Prompt.ask("Enter keywords (comma-separated)")
            filter_config.keywords = [kw.strip() for kw in keywords.split(",")]
        
        # Apply filters
        job_filter = JobFilter(filter_config)
        self.filtered_jobs = job_filter.filter_jobs(self.jobs)
        
        self.console.print(f"\n[green]✅ Filtered to {len(self.filtered_jobs)} jobs[/green]")
    
    def _view_results(self):
        """View current job results."""
        jobs_to_show = self.filtered_jobs if self.filtered_jobs else self.jobs
        
        if not jobs_to_show:
            self.console.print("[red]No jobs to display. Search first![/red]")
            return
        
        table = Table(title="Job Listings", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Position", style="cyan", max_width=35)
        table.add_column("Company", style="green", max_width=25)
        table.add_column("Location", style="yellow", max_width=20)
        table.add_column("Skills", style="blue", max_width=30)
        
        for i, job in enumerate(jobs_to_show, 1):
            skills = ", ".join(job.get("skills", [])[:3])
            table.add_row(
                str(i),
                job.get("title", "Unknown")[:35],
                job.get("company", "Unknown")[:25],
                job.get("location", "Not specified")[:20],
                skills[:30]
            )
        
        self.console.print(table)
    
    def _export_results(self):
        """Export results to file."""
        jobs_to_export = self.filtered_jobs if self.filtered_jobs else self.jobs
        
        if not jobs_to_export:
            self.console.print("[red]No jobs to export. Search first![/red]")
            return
        
        self.console.print("\n[bold]💾 Export Options[/bold]\n")
        self.console.print("1. CSV")
        self.console.print("2. Excel")
        self.console.print("3. JSON")
        self.console.print("4. Markdown")
        
        choice = Prompt.ask("Select format", choices=["1", "2", "3", "4"])
        
        exporter = JobExporter()
        
        try:
            if choice == "1":
                filepath = exporter.export_csv(jobs_to_export)
            elif choice == "2":
                filepath = exporter.export_excel(jobs_to_export)
            elif choice == "3":
                filepath = exporter.export_json(jobs_to_export)
            elif choice == "4":
                filepath = exporter.export_markdown(jobs_to_export)
            
            self.console.print(f"\n[green]✅ Exported to: {filepath}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Export failed: {e}[/red]")
    
    def _setup_notifications(self):
        """Set up email notifications."""
        self.console.print("\n[bold]📧 Email Notifications Setup[/bold]\n")
        
        sender_email = Prompt.ask("Your Gmail address")
        sender_password = Prompt.ask("App password (not regular password)", password=True)
        recipient_email = Prompt.ask("Recipient email (where to send notifications)")
        
        if Confirm.ask("Send test email now?"):
            notifier = EmailNotifier()
            new_jobs = notifier.get_new_jobs(self.jobs)
            
            if new_jobs:
                notifier.send_email(sender_email, sender_password, recipient_email, new_jobs)
            else:
                self.console.print("[yellow]No new jobs to send.[/yellow]")
        
        # Save config for future use
        config_data = {
            "sender_email": sender_email,
            "sender_password": sender_password,
            "recipient_email": recipient_email
        }
        
        with open("email_config.json", "w") as f:
            import json
            json.dump(config_data, f)
        
        self.console.print("[green]✅ Email configuration saved![/green]")
    
    def _configure_settings(self):
        """Configure agent settings."""
        self.console.print("\n[bold]⚙️ Settings[/bold]\n")
        
        self.console.print(f"Current settings:")
        self.console.print(f"  • Target role: {self.config.target_role}")
        self.console.print(f"  • Location: {self.config.location}")
        self.console.print(f"  • Results: {self.config.num_results}")
        self.console.print(f"  • Model: {self.config.model}")
        
        if Confirm.ask("\nChange target role?"):
            self.config.target_role = Prompt.ask("New target role", default=self.config.target_role)
        
        if Confirm.ask("Change location?"):
            self.config.location = Prompt.ask("New location", default=self.config.location)
        
        if Confirm.ask("Change number of results?"):
            self.config.num_results = IntPrompt.ask("New number", default=self.config.num_results)
    
    def _scrape_descriptions(self):
        """Scrape full job descriptions."""
        jobs_to_scrape = self.filtered_jobs if self.filtered_jobs else self.jobs
        
        if not jobs_to_scrape:
            self.console.print("[red]No jobs to scrape. Search first![/red]")
            return
        
        scraper = JobScraper()
        
        with self.console.status("[bold green]Scraping job descriptions...") as status:
            for i, job in enumerate(jobs_to_scrape[:10], 1):
                status.update(f"Scraping {i}/{min(len(jobs_to_scrape), 10)}...")
                url = job.get("url", "")
                source = job.get("source", "generic").lower()
                
                description_data = scraper.scrape_job(url, source)
                if description_data:
                    job["full_description"] = description_data.get("description", "")
                    job["detailed_requirements"] = description_data.get("requirements", [])
                    job["detailed_responsibilities"] = description_data.get("responsibilities", [])
        
        self.console.print(f"[green]✅ Scraped full descriptions for {min(len(jobs_to_scrape), 10)} jobs[/green]")
    
    def _view_statistics(self):
        """View job statistics."""
        jobs_to_analyze = self.filtered_jobs if self.filtered_jobs else self.jobs
        
        if not jobs_to_analyze:
            self.console.print("[red]No jobs to analyze. Search first![/red]")
            return
        
        # Count by source
        sources = {}
        for job in jobs_to_analyze:
            source = job.get("source", "Unknown")
            sources[source] = sources.get(source, 0) + 1
        
        # Count skills
        skills = {}
        for job in jobs_to_analyze:
            for skill in job.get("skills", []):
                if skill != "Not specified":
                    skills[skill] = skills.get(skill, 0) + 1
        
        # Display statistics
        self.console.print("\n[bold]📈 Job Statistics[/bold]\n")
        
        # Sources table
        source_table = Table(title="Jobs by Source", show_header=True)
        source_table.add_column("Source", style="cyan")
        source_table.add_column("Count", style="green")
        
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            source_table.add_row(source, str(count))
        
        self.console.print(source_table)
        
        # Skills table
        if skills:
            skills_table = Table(title="Top Skills", show_header=True)
            skills_table.add_column("Skill", style="cyan")
            skills_table.add_column("Count", style="green")
            
            for skill, count in sorted(skills.items(), key=lambda x: x[1], reverse=True)[:10]:
                skills_table.add_row(skill, str(count))
            
            self.console.print(skills_table)
