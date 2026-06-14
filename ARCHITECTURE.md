# Agentic AI Job Search Platform - How It Works

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER'S BROWSER                                    │
│                        http://localhost:5173                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        REACT FRONTEND                               │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │    │
│  │  │Dashboard │  │ JobView  │  │ResumePage│  │  Navbar  │           │    │
│  │  │ (Search) │  │ (Detail) │  │ (Matcher)│  │  (Nav)   │           │    │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┘           │    │
│  │       │              │              │                               │    │
│  │       └──────────────┴──────────────┘                               │    │
│  │                          │                                          │    │
│  │                    HTTP Requests                                    │    │
│  └──────────────────────────┼──────────────────────────────────────────┘    │
└─────────────────────────────┼───────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND                                     │
│                        http://localhost:8000                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         app.py (Router)                              │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │    │
│  │  │/api/     │  │/api/     │  │/api/     │  │/api/     │           │    │
│  │  │search    │  │scrape    │  │match     │  │tailor    │           │    │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │    │
│  │       │              │              │              │                 │    │
│  │  ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐           │    │
│  │  │ search.py│  │scraper.py│  │resume_   │  │resume_   │           │    │
│  │  │          │  │          │  │matcher.py│  │matcher.py│           │    │
│  │  └────┬─────┘  └──────────┘  └──────────┘  └──────────┘           │    │
│  │       │                                                              │    │
│  └───────┼──────────────────────────────────────────────────────────────┘    │
│          │                                                                  │
└──────────┼──────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL APIs                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │   LINKEDIN   │  │   REMOTIVE   │  │    GOOGLE    │                      │
│  │   (Scrape)   │  │   (Free API) │  │   (Scrape)   │                      │
│  │              │  │              │  │              │                      │
│  │ Real jobs    │  │ Remote jobs  │  │ Aggregated   │                      │
│  │ with URLs    │  │ with salary  │  │ listings     │                      │
│  └──────────────┘  └──────────────┘  └──────────────┘                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## How Each Component Works

### 1. Frontend (React + Vite)

**Location:** `/frontend/src/`

```
frontend/src/
├── App.jsx              # Main app, routes, navbar
├── main.jsx             # Entry point
├── index.css            # Global styles (dark theme)
└── pages/
    ├── Dashboard.jsx    # Job search page
    ├── JobView.jsx      # Job detail page
    └── ResumePage.jsx   # Resume matcher/tailor
```

**Dashboard.jsx** - The main search interface:

```javascript
// When user clicks "Search Jobs":
const searchJobs = async () => {
  // 1. Send POST request to backend
  const res = await axios.post('http://localhost:8000/api/search', {
    query: "AI Engineer",      // Search term
    state: "California",       // Filter by state
    city: "San Francisco",     // Filter by city
    remote_only: false,        // Remote filter
    num_results: 20            // How many results
  });
  
  // 2. Receive jobs array from backend
  setJobs(res.data.jobs);
};
```

**JobView.jsx** - Shows job details:

```javascript
// When user clicks "Get Full Description":
const scrapeFullDescription = async () => {
  // 1. Call backend scraper
  const res = await axios.post(`http://localhost:8000/api/scrape/${jobIndex}`);
  
  // 2. Get full JD, requirements, responsibilities
  setJob(res.data);
};
```

**ResumePage.jsx** - Resume analysis:

```javascript
// Analyze match between resume and job
const analyzeMatch = async () => {
  const res = await axios.post('http://localhost:8000/api/match', {
    resume_text: resumeText,
    job_description: jobDescription,
    job_title: jobTitle
  });
  // Returns: match_score, matched_skills, missing_skills, improvements
};
```

---

### 2. Backend (FastAPI + Python)

**Location:** `/backend/`

```
backend/
├── app.py              # FastAPI routes
├── search.py           # Job search logic
├── scraper.py          # Job description scraper
├── resume_matcher.py   # AI resume analysis
├── job_apis.py         # External API integrations
└── cached_jobs.json    # Temporary job cache
```

#### app.py - API Routes

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow React frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/search")
def search_jobs(request: SearchRequest):
    # 1. Call JobSearcher with filters
    jobs = searcher.search(
        query=request.query,
        state=request.state,
        city=request.city,
        remote_only=request.remote_only
    )
    return {"jobs": jobs, "total": len(jobs)}
```

#### search.py - Job Search Engine

```python
class JobSearcher:
    def search(self, query, state, city, remote_only):
        all_jobs = []
        
        # 1. Search Remotive API (real remote jobs)
        remotive_jobs = self._search_remotive(query)
        all_jobs.extend(remotive_jobs)
        
        # 2. Search LinkedIn (real jobs, scraped)
        linkedin_jobs = self._search_linkedin(query, state, city)
        all_jobs.extend(linkedin_jobs)
        
        # 3. Search Google (aggregated)
        google_jobs = self._search_google_usa(query, state, city)
        all_jobs.extend(google_jobs)
        
        # 4. Deduplicate by title+company
        unique_jobs = self._deduplicate(all_jobs)
        
        return unique_jobs
```

**How LinkedIn Scraping Works:**

```python
def _search_linkedin(self, query, state, city):
    # 1. Build LinkedIn URL
    url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={state}"
    
    # 2. Send HTTP request with browser User-Agent
    response = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
    })
    
    # 3. Parse HTML with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 4. Extract job cards
    for card in soup.select("div.base-card"):
        title = card.select_one("h3.base-search-card__title").text
        company = card.select_one("h4.base-search-card__subtitle").text
        link = card.select_one("a.base-card__full-link")["href"]
        location = card.select_one("span.job-search-card__location").text
        
        jobs.append({
            "title": title,
            "company": company,
            "url": link,        # REAL URL to apply
            "location": location,
            "source": "LinkedIn"
        })
```

**How Remotive API Works:**

```python
def _search_remotive(self, query):
    # 1. Call Remotive API (free, no auth required)
    response = requests.get(
        "https://remotive.com/api/remote-jobs",
        params={"search": query}
    )
    
    # 2. Parse JSON response
    data = response.json()
    
    for job in data["jobs"]:
        jobs.append({
            "title": job["title"],
            "company": job["company_name"],
            "url": job["url"],           # REAL apply URL
            "salary": job["salary"],     # Real salary data
            "skills": job["tags"],       # Real skills
            "remote": True               # All Remotive jobs are remote
        })
```

---

### 3. Resume Matcher (AI-Powered)

**Location:** `/backend/resume_matcher.py`

```python
from openai import OpenAI

class ResumeMatcher:
    def analyze_match(self, resume_text, job_description, job_title):
        # 1. Create prompt for GPT
        prompt = f"""
        Analyze how well this resume matches the job.
        
        Job: {job_title}
        Job Description: {job_description}
        
        Resume: {resume_text}
        
        Return JSON with:
        - match_score (0-100)
        - matched_skills
        - missing_skills
        - improvements
        """
        
        # 2. Call OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        # 3. Parse and return analysis
        return json.loads(response.choices[0].message.content)
    
    def tailor_resume(self, resume_text, job_description, job_title):
        # 1. Ask GPT to rewrite resume for the job
        prompt = f"""
        Tailor this resume for the job. Make it ATS-friendly.
        
        Job: {job_title}
        Resume: {resume_text}
        
        Return JSON with:
        - tailored_resume (full rewritten resume)
        - changes_made
        - tips
        """
        
        # 2. Get tailored version
        response = self.client.chat.completions.create(...)
        
        return json.loads(response.choices[0].message.content)
```

---

### 4. Job Description Scraper

**Location:** `/backend/scraper.py`

When user clicks "Get Full Description":

```python
class JobScraper:
    def scrape_job(self, url, source):
        # 1. Fetch the job posting page
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 2. Try different selectors to find description
        selectors = [
            "div.show-more-less-html__markup",  # LinkedIn
            "div.job-description",              # Indeed
            "article",                          # Generic
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                description = elem.get_text()
                break
        
        # 3. Extract requirements using regex
        requirements = self._extract_requirements(description)
        
        # 4. Extract responsibilities
        responsibilities = self._extract_responsibilities(description)
        
        return {
            "description": description,
            "requirements": requirements,
            "responsibilities": responsibilities
        }
```

---

## Data Flow Diagrams

### Job Search Flow

```
User types "AI Engineer" + selects "California"
        │
        ▼
┌─────────────────┐
│  React Dashboard │
│  (Dashboard.jsx) │
└────────┬────────┘
         │ POST /api/search
         │ {query: "AI Engineer", state: "California"}
         ▼
┌─────────────────┐
│  FastAPI Backend │
│   (app.py)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  JobSearcher     │
│  (search.py)     │
└────────┬────────┘
         │
    ┌────┴────┬────────────┐
    ▼         ▼            ▼
┌────────┐ ┌────────┐ ┌────────┐
│LinkedIn│ │Remotive│ │ Google │
│  API   │ │  API   │ │ Search │
└───┬────┘ └───┬────┘ └───┬────┘
    │          │          │
    └────┬─────┴──────────┘
         │ Merge & Deduplicate
         ▼
┌─────────────────┐
│  Return jobs[]   │
│  to Frontend     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Display Job     │
│  Cards in UI     │
└─────────────────┘
```

### Resume Match Flow

```
User pastes resume + job description
        │
        ▼
┌─────────────────┐
│  ResumePage.jsx  │
└────────┬────────┘
         │ POST /api/match
         │ {resume_text, job_description}
         ▼
┌─────────────────┐
│  FastAPI         │
│  /api/match      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ResumeMatcher   │
│  (AI Analysis)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  OpenAI GPT-4   │
│  API Call        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Return:         │
│  - match_score   │
│  - skills match  │
│  - improvements  │
└─────────────────┘
```

---

## Technologies Used

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React 18 | UI components |
| | Vite | Build tool, dev server |
| | React Router | Page navigation |
| | Axios | HTTP requests |
| | Lucide Icons | UI icons |
| **Backend** | FastAPI | REST API server |
| | Uvicorn | ASGI server |
| | Pydantic | Data validation |
| **Data Sources** | LinkedIn | Real job listings |
| | Remotive API | Remote tech jobs |
| | Google Search | Aggregated jobs |
| **AI** | OpenAI GPT-4 | Resume analysis |
| **Scraping** | BeautifulSoup | HTML parsing |
| | Requests | HTTP client |

---

## File Structure

```
learnAI/
├── ARCHITECTURE.md          # This file
├── README.md                # User guide
├── start.sh                 # Start both servers
├── requirements.txt         # Python dependencies
│
├── backend/                 # Python FastAPI
│   ├── app.py              # Main server, routes
│   ├── search.py           # Job search engine
│   ├── scraper.py          # JD scraper
│   ├── resume_matcher.py   # AI resume analysis
│   ├── job_apis.py         # External API wrappers
│   ├── requirements.txt    # Backend dependencies
│   └── cached_jobs.json    # Job cache
│
├── frontend/                # React app
│   ├── src/
│   │   ├── App.jsx         # Main app
│   │   ├── main.jsx        # Entry point
│   │   ├── index.css       # Styles
│   │   └── pages/
│   │       ├── Dashboard.jsx   # Search page
│   │       ├── JobView.jsx     # Job details
│   │       └── ResumePage.jsx  # Resume matcher
│   ├── package.json        # Dependencies
│   └── vite.config.js      # Vite config
│
└── job_scraper/             # Original CLI agent
    ├── agent.py
    ├── search.py
    ├── filters.py
    ├── exporter.py
    └── notifications.py
```

---

## API Endpoints

| Method | Endpoint | Request Body | Response |
|--------|----------|--------------|----------|
| `POST` | `/api/search` | `{query, state, city, remote_only}` | `{jobs: [...]}` |
| `POST` | `/api/scrape/{index}` | - | `{full_description, requirements}` |
| `POST` | `/api/match` | `{resume_text, job_description}` | `{match_score, skills}` |
| `POST` | `/api/tailor` | `{resume_text, job_description}` | `{tailored_resume}` |
| `GET` | `/api/jobs/cache` | - | `{jobs: [...]}` |
| `GET` | `/api/locations` | - | `{states: {...}}` |

---

## How Jobs Are Real

1. **LinkedIn Jobs** - Scraped directly from LinkedIn's public job search
   - Real job titles, companies, locations
   - Direct apply URLs (linkedin.com/jobs/view/...)
   - Clicking opens actual job posting

2. **Remotive Jobs** - From Remotive's free API
   - Real remote tech jobs
   - Includes salary data
   - Tags/skills from job posters

3. **Google Jobs** - Aggregated from multiple sources
   - Combines results from various job boards
   - Links to original postings

---

## Running the App

```bash
# 1. Start backend
cd backend
python3 app.py

# 2. Start frontend (new terminal)
cd frontend
npm run dev

# 3. Open browser
http://localhost:5173
```

---

## Why This Architecture?

1. **Separation of Concerns**
   - Frontend: UI only
   - Backend: Business logic
   - APIs: Data sources

2. **Real-Time Data**
   - No mock data
   - Live API calls
   - Actual job postings

3. **Scalability**
   - Can add more APIs
   - Can add database
   - Can add authentication

4. **User Experience**
   - Fast search
   - One-click apply
   - AI-powered resume matching
