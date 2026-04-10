# PolicyLens AI

> Upload any government policy PDF → get a full bias report, SDG score, loophole flags, and plain-English summary — in under 90 seconds. Free. Open-source. Forever.

**Team:** Cifer Troop — Selvaragavan M & Vikashni M  
**Institution:** Kathir College of Engineering, Coimbatore  
**Hackathon:** AI Tool Development Challenge 2.0 — OneEarth Theme  
**Primary SDG:** SDG 16 — Peace, Justice and Strong Institutions

---

## Quick Start

```bash
# Backend
cd policylens-ai
pip install -r backend/requirements.txt
python -m spacy download en_core_web_sm
uvicorn backend.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend && npm install && npm run dev
```

Open http://localhost:3000 and upload `data/sample_policies/test_policy.txt`

**→ See `SETUP_INSTRUCTIONS.md` for full setup, Docker, Groq free API, and demo script.**

---

## Tech Stack (100% Open Source)

| Layer | Tools |
|---|---|
| LLM | Ollama + Mistral 7B (local) / Groq Free API |
| Bias Detection | HuggingFace BERT + IBM AIF360 + Lexicons |
| SDG Classification | DistilBERT fine-tuned on SDG dataset |
| Embeddings | sentence-transformers + FAISS |
| NLP | spaCy NER |
| Backend | FastAPI + SQLite/PostgreSQL |
| Frontend | React 18 + Tailwind CSS + Recharts |
| Translation | LibreTranslate + Argos Translate |
| Deployment | Docker Compose |

