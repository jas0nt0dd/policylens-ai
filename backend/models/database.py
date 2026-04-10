"""
SQLAlchemy database models for PolicyLens AI
Uses SQLite for development (zero setup), PostgreSQL for production.
"""
from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, JSON, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./policylens.db"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class AnalysisTask(Base):
    __tablename__ = "analysis_tasks"

    id = Column(String, primary_key=True)
    status = Column(String, default="pending")  # pending | processing | completed | failed
    progress = Column(Integer, default=0)
    stage = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    result_id = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(String, primary_key=True)
    document_name = Column(String)
    overall_bias_score = Column(Integer)
    bias_level = Column(String)
    sdg_scores = Column(JSON)  # Dict[str, int]
    sdg_overall_score = Column(Integer)
    flagged_clauses = Column(JSON)  # List[FlaggedClause]
    citizen_summary = Column(Text)
    recommendations = Column(JSON)
    processing_time = Column(Float)
    language = Column(String, default="en")
    readability_score = Column(Float, nullable=True)
    total_clauses = Column(Integer, default=0)
    demographic_mentions = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
