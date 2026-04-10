# PolicyLens AI — Deployment Guide
## Backend on Render + Frontend on Vercel

---

## Quick Start (Local Development)

### Option 1: Unified Startup (Recommended)

**Windows (PowerShell):**
```bash
cd policylens-ai
.\run.ps1
```

**Windows (Command Prompt):**
```bash
cd policylens-ai
run.bat
```

**Mac/Linux:**
```bash
cd policylens-ai
python run.py
```

This will:
- ✅ Start backend on http://127.0.0.1:8000
- ✅ Start frontend on http://localhost:3000
- ✅ Create .env file automatically

---

## Deployment: Step-by-Step

### Step 1: Prepare Repository

#### 1.1 Create .gitignore

```bash
# In project root (policylens-ai/)
# Add these entries:
__pycache__/
*.pyc
*.egg-info/
.env
node_modules/
build/
dist/
.DS_Store
venv/
```

#### 1.2 Initialize Git & Push to GitHub

```bash
cd policylens-ai
git init
git add .
git commit -m "Initial commit: PolicyLens AI full stack"
git remote add origin https://github.com/YOUR-USERNAME/policylens-ai.git
git branch -M main
git push -u origin main
```

---

### Step 2: Deploy Backend to Render

#### 2.1 Create Render Account
- Go to https://render.com
- Sign up with GitHub
- Connect your GitHub account

#### 2.2 Create Web Service (Backend)

1. Click **New +** → **Web Service**
2. Connect your GitHub repository
3. Fill in the details:
   - **Name**: `policylens-ai-backend`
   - **Root Directory**: *(leave blank)*
   - **Environment**: `Python 3.12`
   - **Build Command**: 
     ```bash
     pip install -r backend/requirements.txt && python -m spacy download en_core_web_sm
     ```
   - **Start Command**: 
     ```bash
     cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

4. **Environment Variables** (click "Advanced"):
   ```
   DATABASE_URL=sqlite+aiosqlite:///./policylens.db
   GROQ_API_KEY=gsk_... (get from https://console.groq.com)
   ```

5. Click **Create Web Service**

#### 2.3 Wait for Deployment
- Render will automatically:
  - Clone your repo
  - Install dependencies
  - Download spaCy model (~40MB)
  - Start the server
  - Assign you a URL: `https://policylens-ai-backend.onrender.com`

✅ Backend is live! Test it:
```bash
curl https://policylens-ai-backend.onrender.com/health
```

---

### Step 3: Deploy Frontend to Vercel

#### 3.1 Create Vercel Account
- Go to https://vercel.com
- Sign up with GitHub
- Authorize Vercel to access your repos

#### 3.2 Import Project

1. Click **Add New** → **Project**
2. Select your GitHub repo: `policylens-ai`
3. Fill in the details:
   - **Framework**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

#### 3.3 Environment Variables
- Click **Environment Variables**
- Add:
  ```
  VITE_API_URL=https://policylens-ai-backend.onrender.com
  ```

4. Click **Deploy**

✅ Frontend is live! You'll get a URL like:
- `https://policylens-ai.vercel.app`

---

### Step 4: Update Frontend API Connection

Create/update `frontend/.env.production`:
```
VITE_API_URL=https://policylens-ai-backend.onrender.com
```

Update `frontend/src/api.js` (or wherever API calls are made):
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function analyzeDocument(formData) {
  const response = await fetch(`${API_URL}/api/analyze`, {
    method: 'POST',
    body: formData,
  });
  return response.json();
}
```

---

## Troubleshooting Deployment

### Backend (Render) Issues

**"No module named 'backend'"**
- Make sure Build Command includes the spaCy download
- Frontend path should be correct in build command

**"ModuleNotFoundError: No module named 'aiosqlite'"**
- Update `backend/requirements.txt` to include aiosqlite
- Render will reinstall on next deployment

**Slow first request (>30 seconds)**
- HuggingFace models (~500MB) download on first use
- Cache persists after first download
- This is normal; subsequent requests are fast

### Frontend (Vercel) Issues

**"Cannot find module backend.main"**
- Verify Root Directory is set to `frontend`
- Check that build command is correct

**API calls fail with CORS error**
- Backend needs CORS headers enabled
- Add to `backend/main.py`:
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["https://policylens-ai.vercel.app"],
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

---

## Environment Variables Reference

### Backend (.env or Render)
```
DATABASE_URL=sqlite+aiosqlite:///./policylens.db
GROQ_API_KEY=gsk_...
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
LIBRETRANSLATE_URL=http://localhost:5000
```

### Frontend (.env.production)
```
VITE_API_URL=https://policylens-ai-backend.onrender.com
```

---

## Rolling Back Deployments

### Render (Backend)
1. Go to your service → **Deployments**
2. Find the previous deployment
3. Click **Redeploy**

### Vercel (Frontend)
1. Go to your project → **Deployments**
2. Find the previous deployment
3. Click **Promote to Production**

---

## Monitoring & Logs

### Render Backend Logs
- Service Dashboard → **Logs** tab
- Real-time error tracking

### Vercel Frontend Logs
- Project Dashboard → **Deployments** → Click deployment → **View Build Logs**

---

## Custom Domain Setup (Optional)

### Render (Backend)
1. Service → **Settings** → **Custom Domain**
2. Add your domain: `api.yourdomain.com`
3. Follow DNS instructions

### Vercel (Frontend)
1. Project → **Settings** → **Domains**
2. Add your domain: `yourdomain.com`
3. Follow DNS instructions

---

## Scaling Notes

- **Render**: Upgrade to paid plan for auto-scaling
- **Vercel**: Automatic scaling included (pay per request)
- **Database**: SQLite works for demo; use PostgreSQL in production
  - Render provides free PostgreSQL databases
  - Update `DATABASE_URL` to: `postgresql+asyncpg://user:pass@host:5432/db`

---

*PolicyLens AI — Deployed!*
