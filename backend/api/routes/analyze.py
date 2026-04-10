"""
/api/analyze endpoint — accepts PDF upload or URL, queues analysis task
"""
from pathlib import Path
import logging
import os
import shutil
import tempfile
import uuid

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.schemas import AnalysisResponse, AnalysisStatusResponse
from backend.models.database import AnalysisTask, get_db
from backend.workers.celery_tasks import run_analysis_pipeline_in_background

router = APIRouter()
logger = logging.getLogger("policylens.analyze")

UPLOAD_DIR = Path(
    os.getenv(
        "POLICYLENS_UPLOAD_DIR",
        str(Path(tempfile.gettempdir()) / "policylens_uploads"),
    )
)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(None),
    url: str = Form(None),
    language_output: str = Form("en"),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a PDF/DOCX file OR provide a URL to a policy document.
    Returns a task_id to poll for results.
    """
    if not file and not url:
        raise HTTPException(status_code=400, detail="Provide either a file or a URL.")

    task_id = str(uuid.uuid4())
    file_path = None

    if file:
        allowed = [".pdf", ".docx", ".txt"]
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

        upload_path = UPLOAD_DIR / f"{task_id}{ext}"
        with upload_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        file_path = str(upload_path)
        logger.info("Saved upload: %s", file_path)

    # Create task record
    task = AnalysisTask(
        id=task_id,
        status="pending",
        progress=0,
        file_path=file_path or url,
    )
    db.add(task)
    await db.commit()

    # Queue background analysis
    background_tasks.add_task(
        run_analysis_pipeline_in_background,
        task_id=task_id,
        file_path=file_path,
        url=url,
        language_output=language_output,
    )

    return AnalysisResponse(
        task_id=task_id,
        status="queued",
        message="Analysis started. Poll /api/status/{task_id} for progress.",
    )


@router.get("/status/{task_id}", response_model=AnalysisStatusResponse)
async def get_status(task_id: str, db: AsyncSession = Depends(get_db)):
    """Poll analysis task status."""
    result = await db.execute(select(AnalysisTask).where(AnalysisTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return AnalysisStatusResponse(
        task_id=task.id,
        status=task.status,
        progress=task.progress,
        stage=task.stage,
        result_id=task.result_id,
        error=task.error,
    )
