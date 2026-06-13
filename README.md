# Agentic AI Job Search Platform

A full-stack web application for finding Agentic AI Engineer jobs with resume matching and tailoring.

## Features

- **Job Search** - Search across LinkedIn, Indeed, and the web
- **Job Details** - View full job descriptions with one click
- **Easy Apply** - Direct apply buttons for each job
- **Resume Matcher** - Analyze how well your resume matches a job
- **Resume Tailor** - AI-powered resume tailoring for ATS optimization
- **Dark Mode** - Beautiful dark UI

## Tech Stack

**Frontend:**
- React + Vite
- React Router
- Lucide Icons

**Backend:**
- FastAPI (Python)
- BeautifulSoup (Web Scraping)
- OpenAI (Resume Analysis)

## Quick Start

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Start both servers
cd ..
./start.sh
```

Or start separately:

```bash
# Terminal 1 - Backend
cd backend && python3 app.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

## Access

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/search` | Search for jobs |
| POST | `/api/scrape/{index}` | Get full job description |
| POST | `/api/match` | Analyze resume match |
| POST | `/api/tailor` | Tailor resume for job |
| GET | `/api/jobs/cache` | Get cached jobs |

## Project Structure

```
.
├── backend/
│   ├── app.py              # FastAPI server
│   ├── search.py           # Job search
│   ├── scraper.py          # Job description scraper
│   ├── resume_matcher.py   # AI resume analysis
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx   # Job search page
│   │   │   ├── JobView.jsx     # Job detail page
│   │   │   └── ResumePage.jsx  # Resume matcher
│   │   ├── App.jsx
│   │   └── index.css
│   └── package.json
└── start.sh
```

## Usage

1. **Search Jobs** - Enter a query and click Search
2. **View Details** - Click any job card to see full details
3. **Apply** - Click "Apply Now" to go to the job posting
4. **Match Resume** - Click "Match My Resume" to analyze your fit
5. **Tailor Resume** - Click "Tailor My Resume" to optimize for ATS

## Resume Tips

- Include keywords from the job description
- Quantify achievements (numbers, percentages)
- Use action verbs (built, led, improved)
- Keep it ATS-friendly (simple formatting)
