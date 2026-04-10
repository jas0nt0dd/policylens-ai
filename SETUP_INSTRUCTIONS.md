# PolicyLens AI — Setup Instructions
### Team: Cifer Troop | Kathir College of Engineering
### AI Tool Development Challenge 2.0

---

## What You Have

This is a fully structured project with:
- **Backend** — FastAPI + SQLite + all 5 AI pipeline stages
- **Frontend** — React 18 + Tailwind CSS + interactive dashboards
- **Docker** — One-command full-stack deployment
- **Test Data** — Sample biased policy text to demo immediately

---

## Option A — Quickest Demo (Recommended for Hackathon)

### Step 1: Set up Python backend

```bash
cd policylens-ai/backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Download spaCy model

```bash
python -m spacy download en_core_web_sm
```

### Step 3: Start the backend

```bash
cd policylens-ai   # go back to project root
uvicorn backend.main:app --reload --port 8000
```

You should see: `PolicyLens AI starting up...`
API docs available at: http://localhost:8000/docs

### Step 4: Set up React frontend

Open a NEW terminal:

```bash
cd policylens-ai/frontend
npm install
npm run dev
```

Frontend opens at: http://localhost:3000

### Step 5: Test the pipeline

1. Go to http://localhost:3000
2. Click **Analyze**
3. Upload the file: `data/sample_policies/test_policy.txt`
4. Click **Analyze Document**
5. Watch the 5-stage pipeline run
6. View the bias report, SDG scores, clause highlights

---

## Option B — Full Stack with Ollama (LLM Enabled)

### Install Ollama (local LLM — free, runs offline)

```bash
# Linux/Mac:
curl -fsSL https://ollama.com/install.sh | sh

# Windows: Download from https://ollama.com/download
```

### Pull Mistral 7B model (~4GB, one-time download)

```bash
ollama pull mistral
ollama serve   # starts on http://localhost:11434
```

### Re-run backend (Ollama will now be used automatically)

The backend auto-detects Ollama. No config change needed.

---

## Option C — Docker Compose (Full Production Stack)

```bash
cd policylens-ai

# Copy environment file
cp .env.example .env

# Build and start everything
docker-compose -f docker/docker-compose.yml up --build

# In a separate terminal, pull the Mistral model into Ollama container:
docker exec -it $(docker ps -q -f name=ollama) ollama pull mistral
```

Services will be running at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- LibreTranslate: http://localhost:5000
- Ollama: http://localhost:11434

---

## Option D — Free Cloud Deployment (No Local GPU Needed)

### Backend on Railway (free tier)

```bash
# Install Railway CLI
npm install -g @railway/cli
railway login
railway init
railway up
```

### Frontend on Vercel (free)

```bash
npm install -g vercel
cd frontend
vercel --prod
```

### LLM via Groq Free API (zero GPU needed)

1. Go to https://console.groq.com → Create account → Get free API key
2. Add to your `.env`: `GROQ_API_KEY=your_key_here`
3. Backend will automatically use Groq when Ollama is unavailable

---

## Feature Status

| Feature | Status | Notes |
|---|---|---|
| PDF/DOCX Upload | ✅ Ready | PyMuPDF + pdfplumber |
| URL Scraping | ✅ Ready | BeautifulSoup4 |
| Bias Detection (Lexicon) | ✅ Ready | Works offline immediately |
| Bias Detection (BERT) | ⚡ Optional | Auto-downloads on first run |
| SDG Classification (Keywords) | ✅ Ready | Works offline immediately |
| SDG Classification (DistilBERT) | ⚡ Optional | Auto-downloads on first run |
| LLM Deep Analysis | ⚡ Optional | Needs Ollama or Groq key |
| Translation | ⚡ Optional | Needs LibreTranslate running |
| Interactive Dashboard | ✅ Ready | Full React UI |
| PDF Export | ✅ Ready | jsPDF client-side |
| JSON Export | ✅ Ready | Client-side |
| Compare Policies | ✅ Ready | Needs 2 completed reports |

**The pipeline gracefully degrades** — even without Ollama or BERT, you get a complete bias + SDG report using the lexicon and keyword engines.

---

## Getting a Groq API Key (Free — 2 Minutes)

1. Visit https://console.groq.com
2. Sign up with Google/GitHub
3. Go to **API Keys** → **Create API Key**
4. Copy key → add to `.env` as `GROQ_API_KEY=gsk_...`
5. You now have free, ultra-fast Llama 3.1 inference — no GPU needed

---

## Quick API Test (curl)

```bash
# Health check
curl http://localhost:8000/health

# Upload and analyze a policy file
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@data/sample_policies/test_policy.txt" \
  -F "language_output=en"

# Response: {"task_id": "abc-123", "status": "queued", ...}

# Poll status (replace abc-123 with your task_id)
curl http://localhost:8000/api/status/abc-123

# Get full report (replace REPORT_ID with result_id from status)
curl http://localhost:8000/api/report/REPORT_ID
```

---

## Hackathon Demo Script (10 Minutes)

1. **(0:00 – 1:30)** Open http://localhost:3000 — show the Home page, explain the problem
2. **(1:30 – 3:00)** Click Analyze, explain the 5-stage pipeline visually
3. **(3:00 – 3:30)** Upload `data/sample_policies/test_policy.txt`
4. **(3:30 – 5:00)** Watch live progress bar — call out each stage
5. **(5:00 – 6:30)** Show Bias Report — click a flagged clause, show plain-English rewrite
6. **(6:30 – 7:30)** Switch to SDGs tab — explain the 17-SDG scorecard
7. **(7:30 – 8:00)** Switch to Demographics tab — show equity chart
8. **(8:00 – 8:30)** Click Export → Download PDF report
9. **(8:30 – 10:00)** Talk about impact: $5,000 → $0, 2 weeks → 90 seconds

---

## Troubleshooting

**Backend won't start:**
- Make sure you're in the project ROOT (not inside `/backend`)
- Run: `pip install aiosqlite` if SQLite driver missing

**Frontend shows blank page:**
- Make sure backend is running on port 8000
- Check browser console for CORS errors
- Verify `npm install` completed without errors

**Analysis gets stuck at "LLM deep analysis":**
- This is normal if Ollama is not running — it falls back gracefully
- Set `GROQ_API_KEY` for faster LLM results
- The report will still generate without LLM (uses template fallback)

**HuggingFace model download is slow:**
- Models download once on first use (~500MB total)
- After first download they're cached in `~/.cache/huggingface/`
- Use the lexicon/keyword pipeline first to show judges, models load in background

**spaCy model not found:**
- Run: `python -m spacy download en_core_web_sm`

---

## Project Architecture Recap

```
policylens-ai/
├── backend/
│   ├── main.py                  ← FastAPI app entry point
│   ├── api/routes/
│   │   ├── analyze.py           ← POST /api/analyze (upload)
│   │   ├── report.py            ← GET /api/report/{id}
│   │   └── compare.py           ← POST /api/compare
│   ├── services/
│   │   ├── document_parser.py   ← PyMuPDF + pdfplumber
│   │   ├── semantic_analyzer.py ← FAISS + sentence-transformers
│   │   ├── bias_detector.py     ← AIF360 + BERT + lexicons
│   │   ├── sdg_classifier.py    ← DistilBERT SDG model
│   │   ├── llm_analyzer.py      ← Ollama → Groq → HF fallback
│   │   ├── translator.py        ← LibreTranslate + Argos
│   │   └── report_generator.py  ← Final report aggregation
│   ├── models/
│   │   ├── schemas.py           ← Pydantic models
│   │   └── database.py          ← SQLAlchemy + SQLite/PostgreSQL
│   ├── workers/
│   │   └── celery_tasks.py      ← Background pipeline runner
│   └── requirements.txt
├── frontend/src/
│   ├── App.jsx                  ← Router + Navbar
│   ├── pages/
│   │   ├── Home.jsx             ← Landing page
│   │   ├── Analyze.jsx          ← Upload + results page
│   │   └── Compare.jsx          ← Side-by-side comparison
│   └── components/
│       ├── UploadZone.jsx       ← Drag-drop upload UI
│       ├── AnalysisProgress.jsx ← Live progress tracker
│       ├── BiasReport.jsx       ← Full results dashboard
│       ├── SDGScoreCard.jsx     ← 17-SDG visual grid
│       ├── ClauseHighlighter.jsx← Clause-level drill-down
│       └── ExportPanel.jsx      ← PDF + JSON export
├── data/
│   ├── sample_policies/         ← test_policy.txt ready to use
│   └── bias_lexicons/           ← gender, caste, socioeconomic
├── docker/                      ← Full Docker Compose stack
└── .env.example                 ← Copy to .env
```

---

*PolicyLens AI — One planet. One purpose. Powered by AI.*
*Cifer Troop | Kathir College of Engineering | AI Tool Development Challenge 2.0*
