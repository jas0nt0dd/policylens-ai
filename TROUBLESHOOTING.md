# PolicyLens AI — Feature Troubleshooting Guide

## Issue 1: Output Language Not Working (Always English)

### Root Cause
Translation requires **LibreTranslate** service or **Groq API key** to be configured.

### Quick Diagnosis
```bash
python diagnostics.py
```

### How to Fix

#### Option A: Enable Translation via Groq Free API (Recommended - 2 minutes)
1. Go to https://console.groq.com
2. Sign up with GitHub/Google
3. Create API key → Copy it
4. Create `.env` file in `policylens-ai/` root (if not exists):
   ```
   GROQ_API_KEY=gsk_[your-key-here]
   ```
5. Restart backend: `python run.py`
6. Now language selection will work!

#### Option B: Setup LibreTranslate via Docker
1. Install Docker (https://www.docker.com/products/docker-desktop)
2. Run:
   ```bash
   docker run -d -p 5000:8000 libretranslate/libretranslate
   ```
3. Restart backend
4. Language translation is now active

#### Option C: Use Argos Translate (Offline, Already Installed)
- It's installed but limited language support
- Language selection may be partially active

---

## Issue 2: SDG Classification Not Working

### Root Cause
SDG classification has **two modes**:
- **Keyword-based** (always works, offline)
- **DistilBERT model** (optional, requires HuggingFace download)

### Quick Check
The system **automatically selects keyword-based** if the ML model isn't available. This is **working as designed**.

### How to Enable ML-Based SDG Classification (Optional)
The DistilBERT model downloads automatically on first run (~300MB).
- First analysis with SDG: Takes 2-3 minutes (downloads model)
- Subsequent analyses: Fast (uses cached model)

### Verify It's Working
Check the report's "SDG Scores" section:
- Should have scores for all 17 SDGs
- Keywords matching should show in clauses

---

## Issue 3: LLM Deep Analysis Not Working

### Root Cause
LLM analysis requires **one of these configured**:
1. **Ollama** (local, fast, free)
2. **Groq API** (cloud, ultra-fast, free tier amazing)
3. **HuggingFace** (free but slow)

### Current Status
By default, system tries the fallback chain:
```
Try Ollama → Try Groq → Try HuggingFace → Use Template Fallback
```

### How to Enable LLM Analysis

#### Option 1: Groq Free API (Fastest - Recommended)
1. Get Groq key (see Issue 1 Option A)
2. Add to `.env`:
   ```
   GROQ_API_KEY=gsk_[your-key]
   ```
3. Restart backend
4. LLM analysis now active!

#### Option 2: Ollama (Local, Fastest, Fully Free)
1. Download Ollama: https://ollama.com
2. Install and run: `ollama serve`
3. In **new terminal**, pull model:
   ```bash
   ollama pull mistral
   ```
4. Restart PolicyLens backend
5. Watch the analysis speed improve dramatically!

#### Option 3: Check if HuggingFace works
- HuggingFace fallback is built-in
- But it's slower (~30 seconds per clause)
- To optimize: Get Groq key or setup Ollama

---

## Complete Setup (All Features Enabled)

If you want **all features working perfectly**:

### Step 1: Add Groq API Key
```bash
# File: policylens-ai/.env
GROQ_API_KEY=gsk_[get-from-console.groq.com]
```

This enables:
- ✅ Language translation
- ✅ LLM deep analysis (ultra-fast)

### Step 2: Setup Ollama (Optional but Recommended)
```bash
# Download from https://ollama.com
# Run:
ollama serve

# In another terminal:
ollama pull mistral
```

This enables:
- ✅ Local, private LLM analysis
- ✅ No API rate limits
- ✅ Works offline

### Step 3: Restart Backend
```bash
python run.py
```

---

## Verification Checklist

### ✅ Language Translation
1. Run analysis, select different language (e.g., Spanish)
2. Check "Citizen Summary" in report
3. Should be in selected language

**If it's still English:**
- Check `.env` has `GROQ_API_KEY` or LibreTranslate is running
- Check backend logs for translation errors
- Run `python diagnostics.py` to verify services

### ✅ SDG Classification
1. Check report's "SDG Scores" section
2. Should show scores for all 17 SDGs (0-100)
3. Clauses should have SDG tags

**If SDG scores are missing or all zeros:**
- Keyword classifier should still work
- DistilBERT model may not have downloaded
- Check backend logs for errors

### ✅ LLM Deep Analysis
1. Check "Plain English" rewrites in flagged clauses
2. Should show simplified versions of policy text
3. Check "Recommendations" section (should have specific suggestions)

**If recommendations are templates:**
- LLM not running
- Run `python diagnostics.py` to check services
- Setup Groq key or Ollama

---

## Performance Expectations

| Feature | Without Setup | With Setup |
|---------|--------------|-----------|
| Language Translation | ❌ Always English | ✅ ~1 second |
| SDG Classification | ✅ Keywords only | ✅ ML-enhanced |
| LLM Analysis | ❌ Templates | ✅ ~2 mins (first), 30s (subsequent) |
| Overall Analysis | ~2 minutes | ~3 minutes (first), ~1.5 min (cached) |

---

## Deployment Notes

When deploying to **Render + Vercel**:

### Backend (Render)
- Add environment variables in Render dashboard:
  - `GROQ_API_KEY=gsk_...` (enables translation + LLM)
  - `DATABASE_URL=sqlite:///policylens.db`
- HuggingFace models auto-cache in `/home/ey...` (persistent across deploys)

### Caveats
- First request will download models (~10-30 mins)
- Render free tier has 30-min timeout, so first analysis might timeout
- Solution: Upgrade to paid tier or use persistent volumes

---

## Testing Commands

```bash
# Run diagnostics
python diagnostics.py

# Test translation endpoint
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@data/sample_policies/test_policy.txt" \
  -F "language_output=es"  # Spanish

# Check backend health
curl http://localhost:8000/health
```

---

## Still Having Issues?

1. Run `python diagnostics.py` — identifies exact problem
2. Check backend logs in terminal running `python run.py`
3. Verify `.env` file exists with correct keys
4. Try with just English first to isolate language issue
5. Contact support with diagnostics output

---

*PolicyLens AI — Fully configurable bias detection*
