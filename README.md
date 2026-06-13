# Agentic AI Job Search Agent

An intelligent agent that scans job listings for Agentic AI Engineer positions, extracts key requirements, and provides clear analysis.

## Features

- 🔍 **Multi-source job search** (Google, Indeed, LinkedIn)
- 📊 **Structured JD extraction** - Skills, requirements, responsibilities
- 🎯 **Advanced filtering** - By location, salary, keywords, remote
- 💾 **Export to multiple formats** - CSV, Excel, JSON, Markdown
- 📧 **Email notifications** - Get notified of new jobs
- 📈 **Statistics dashboard** - Skills demand, source breakdown
- 🔄 **Full JD scraping** - Get complete job descriptions
- 🤖 **AI-powered analysis** (optional with OpenAI API key)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run interactive mode
python run.py

# Or run simple search
python main.py
```

## Interactive CLI

Run `python run.py` for the full interactive experience:

```
╔═══════════════════════════════════════════╗
║  Main Menu                                ║
╠═══════════════════════════════════════════╣
║  1. 🔍 Search for jobs                    ║
║  2. 🎯 Filter jobs                        ║
║  3. 📊 View current results               ║
║  4. 💾 Export to CSV/Excel/JSON            ║
║  5. 📧 Set up email notifications         ║
║  6. ⚙️  Configure settings                 ║
║  7. 🔄 Scrape full job descriptions       ║
║  8. 📈 View statistics                    ║
║  0. 🚪 Exit                               ║
╚═══════════════════════════════════════════╝
```

## Filtering Options

- **Location**: Filter by specific cities or "Remote"
- **Salary**: Set minimum/maximum salary range
- **Keywords**: Include/exclude specific skills
- **Experience**: Filter by years of experience

## Export Formats

| Format | File | Best For |
|--------|------|----------|
| CSV | `jobs.csv` | Spreadsheet analysis |
| Excel | `jobs.xlsx` | Advanced formatting |
| JSON | `jobs.json` | Data processing |
| Markdown | `jobs.md` | Documentation |

## Email Notifications

1. Set up Gmail App Password (not regular password)
2. Run `python run.py` → Select option 5
3. Enter your credentials
4. Get beautiful HTML email digests

## Configuration

Edit `job_scraper/config.py`:

```python
@dataclass
class Config:
    target_role: str = "Agentic AI Engineer"
    location: str = "Remote"
    num_results: int = 10
    model: str = "gpt-4o-mini"  # For AI analysis
```

## Project Structure

```
.
├── run.py                  # Interactive CLI (recommended)
├── main.py                 # Simple search
├── run_enhanced.py         # With full JD scraping
├── test_features.py        # Feature tests
├── requirements.txt        # Dependencies
├── .env.example           # API keys template
└── job_scraper/
    ├── __init__.py
    ├── agent.py            # Main agent logic
    ├── config.py           # Configuration
    ├── search.py           # Job search
    ├── parser.py           # JD parsing
    ├── scraper.py          # Full JD scraper
    ├── filters.py          # Advanced filtering
    ├── exporter.py         # CSV/Excel/JSON export
    ├── notifications.py    # Email notifications
    └── interactive.py      # Interactive CLI
```

## Without API Key

The agent works without an API key for:
- ✅ Job search across platforms
- ✅ Basic skill extraction
- ✅ Filtering and export
- ✅ Email notifications

With OpenAI API key, you get:
- ✨ AI-generated job summaries
- ✨ Key requirements extraction
- ✨ Skills matching insights

## Job Sources

- **Google Jobs**: Aggregated from multiple platforms
- **Indeed**: Direct job listings
- **LinkedIn**: Professional network listings

## Tips

1. **Use App Password for Gmail** - Regular passwords won't work
2. **Run regularly** - Check for new jobs daily
3. **Export results** - Keep track of applications
4. **Scrape full descriptions** - Get complete JD details
