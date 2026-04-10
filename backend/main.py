"""
PolicyLens AI — FastAPI Backend Entry Point
Team: Cifer Troop | Kathir College of Engineering
"""
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging

from backend.api.routes.analyze import router as analyze_router
from backend.api.routes.report import router as report_router
from backend.api.routes.compare import router as compare_router
from backend.models.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("policylens")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("PolicyLens AI starting up...")
    await init_db()
    yield
    logger.info("PolicyLens AI shutting down...")


app = FastAPI(
    title="PolicyLens AI",
    description="Open-source AI-powered policy document analyzer.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://policylens-ai.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(analyze_router, prefix="/api", tags=["Analysis"])
app.include_router(report_router, prefix="/api", tags=["Reports"])
app.include_router(compare_router, prefix="/api", tags=["Compare"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "project": "PolicyLens AI",
        "status": "running",
        "version": "1.0.0",
        "team": "Cifer Troop — Kathir College of Engineering",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
