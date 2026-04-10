"""
Async pipeline runner.
Uses FastAPI BackgroundTasks (no Celery broker needed for dev).
For production, replace with Celery tasks using Redis broker.
"""
import asyncio
import logging
import os
import time

logger = logging.getLogger("policylens.worker")


async def run_analysis_pipeline(
    task_id: str,
    file_path: str = None,
    url: str = None,
    language_output: str = "en",
):
    """
    Full 5-stage PolicyLens AI pipeline:
    Stage 1: Document Parsing
    Stage 2: Semantic Analysis
    Stage 3: Bias Detection
    Stage 4: SDG Classification
    Stage 5: LLM Deep Analysis + Report Generation
    """
    from backend.models.database import AsyncSessionLocal, AnalysisTask, AnalysisReport
    from sqlalchemy import update

    start_time = time.time()

    async def update_task(status, progress, stage=None, result_id=None, error=None):
        async with AsyncSessionLocal() as db:
            vals = {"status": status, "progress": progress}
            if stage:
                vals["stage"] = stage
            if result_id:
                vals["result_id"] = result_id
            if error:
                vals["error"] = error
            await db.execute(update(AnalysisTask).where(AnalysisTask.id == task_id).values(**vals))
            await db.commit()

    try:
        await update_task("processing", 5, "Parsing document")
        logger.info(f"[{task_id}] Stage 1: Document Parsing")

        # ── Stage 1: Parse ─────────────────────────────────────────────────────
        from backend.services.document_parser import parse_document, parse_url
        if file_path and os.path.exists(file_path):
            parsed = parse_document(file_path)
            doc_name = os.path.basename(file_path)
        elif url:
            parsed = parse_url(url)
            doc_name = url[:60]
        else:
            raise ValueError("No file or URL provided")

        await update_task("processing", 20, "Semantic analysis")
        logger.info(f"[{task_id}] Stage 2: Semantic Analysis")

        # ── Stage 2: Semantic Analysis ─────────────────────────────────────────
        from backend.services.semantic_analyzer import analyze_semantics
        semantic_doc = analyze_semantics(parsed)

        await update_task("processing", 40, "Detecting bias")
        logger.info(f"[{task_id}] Stage 3: Bias Detection")

        # ── Stage 3: Bias Detection ────────────────────────────────────────────
        from backend.services.bias_detector import detect_bias
        bias_doc = detect_bias(semantic_doc)

        await update_task("processing", 60, "SDG classification")
        logger.info(f"[{task_id}] Stage 4: SDG Classification")

        # ── Stage 4: SDG Classification ────────────────────────────────────────
        from backend.services.sdg_classifier import classify_sdgs
        sdg_doc = classify_sdgs(bias_doc)

        await update_task("processing", 80, "LLM deep analysis")
        logger.info(f"[{task_id}] Stage 5: LLM Analysis")

        # ── Stage 5: LLM Analysis + Report ────────────────────────────────────
        from backend.services.llm_analyzer import run_llm_analysis
        llm_doc = run_llm_analysis(sdg_doc)

        from backend.services.report_generator import generate_report
        report_data = generate_report(llm_doc, doc_name, start_time, language_output)

        # ── Persist Report ────────────────────────────────────────────────────
        async with AsyncSessionLocal() as db:
            report = AnalysisReport(
                id=report_data["report_id"],
                document_name=report_data["document_name"],
                overall_bias_score=report_data["overall_bias_score"],
                bias_level=report_data["bias_level"],
                sdg_scores=report_data["sdg_scores"],
                sdg_overall_score=report_data["sdg_overall_score"],
                flagged_clauses=report_data["flagged_clauses"],
                citizen_summary=report_data["citizen_summary"],
                recommendations=report_data["recommendations"],
                processing_time=report_data["processing_time"],
                language=report_data["language"],
                readability_score=report_data.get("readability_score"),
                total_clauses=report_data["total_clauses"],
                demographic_mentions=report_data["demographic_mentions"],
            )
            db.add(report)
            await db.commit()

        await update_task("completed", 100, "Complete", result_id=report_data["report_id"])
        logger.info(f"[{task_id}] Pipeline complete in {round(time.time()-start_time,1)}s → report {report_data['report_id']}")

    except Exception as e:
        logger.error(f"[{task_id}] Pipeline failed: {e}", exc_info=True)
        await update_task("failed", 0, error=str(e))


def run_analysis_pipeline_in_background(
    task_id: str,
    file_path: str = None,
    url: str = None,
    language_output: str = "en",
):
    """
    Run the async pipeline in a worker thread so the main FastAPI event loop
    stays responsive while models load or CPU-heavy analysis runs.
    """
    asyncio.run(
        run_analysis_pipeline(
            task_id=task_id,
            file_path=file_path,
            url=url,
            language_output=language_output,
        )
    )
