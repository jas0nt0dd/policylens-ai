"""
/api/report/{id} endpoint — fetch completed analysis report
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.schemas import ReportResponse, BiasLevel, FlaggedClause, TopFinding
from backend.models.database import AnalysisReport, get_db
from backend.services.report_utils import build_top_findings, build_translation_status, collect_impacted_groups, derive_document_title

router = APIRouter()


@router.get("/report/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch full analysis report by report ID."""
    result = await db.execute(
        select(AnalysisReport).where(AnalysisReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    flagged_clauses = [FlaggedClause(**c) for c in (report.flagged_clauses or [])]
    top_findings = build_top_findings(report.flagged_clauses or [])
    document_title = derive_document_title(report.document_name)

    return ReportResponse(
        report_id=report.id,
        document_name=report.document_name,
        document_title=document_title,
        overall_bias_score=report.overall_bias_score,
        bias_level=BiasLevel(report.bias_level),
        sdg_compliance_score=report.sdg_scores,
        sdg_overall_score=report.sdg_overall_score,
        flagged_clauses=flagged_clauses,
        top_findings=[TopFinding(**finding) for finding in top_findings],
        impacted_groups=collect_impacted_groups(report.flagged_clauses or []),
        evidence_clauses=[TopFinding(**finding) for finding in top_findings],
        citizen_summary=report.citizen_summary,
        recommendations=report.recommendations or [],
        processing_time_seconds=report.processing_time,
        language=report.language,
        translation_status=build_translation_status(report.language),
        readability_score=report.readability_score,
        total_clauses_analyzed=report.total_clauses,
        demographic_mentions=report.demographic_mentions or {},
        created_at=report.created_at,
    )


@router.get("/sdg/{report_id}")
async def get_sdg_details(report_id: str, db: AsyncSession = Depends(get_db)):
    """Return detailed SDG breakdown for a report."""
    result = await db.execute(
        select(AnalysisReport).where(AnalysisReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    sdg_names = {
        1: "No Poverty", 2: "Zero Hunger", 3: "Good Health",
        4: "Quality Education", 5: "Gender Equality",
        6: "Clean Water", 7: "Clean Energy", 8: "Decent Work",
        9: "Industry & Innovation", 10: "Reduced Inequalities",
        11: "Sustainable Cities", 12: "Responsible Consumption",
        13: "Climate Action", 14: "Life Below Water",
        15: "Life on Land", 16: "Peace & Justice", 17: "Partnerships",
    }

    scores = report.sdg_scores or {}
    detailed = []
    for k, v in scores.items():
        num = int(k.replace("SDG_", ""))
        detailed.append({
            "sdg_number": num,
            "sdg_name": sdg_names.get(num, f"SDG {num}"),
            "score": v,
        })

    return {"report_id": report_id, "sdg_scores": detailed, "overall": report.sdg_overall_score}
