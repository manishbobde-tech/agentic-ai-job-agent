#!/usr/bin/env python3
"""
Agentic AI Job Search Agent - Main Entry Point
Run with: python run.py
"""

import sys
from job_scraper.interactive import InteractiveCLI


def main():
    """Main entry point with interactive CLI."""
    cli = InteractiveCLI()
    cli.run()


if __name__ == "__main__":
    main()
