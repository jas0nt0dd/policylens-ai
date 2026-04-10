"""
/api/compare endpoint — compare two policy documents
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.schemas import CompareRequest, CompareResponse
from backend.models.database import AnalysisReport, get_db
from backend.services.report_utils import build_compare_reason, build_top_findings, derive_document_title

router = APIRouter()


@router.post("/compare", response_model=CompareResponse)
async def compare_documents(req: CompareRequest, db: AsyncSession = Depends(get_db)):
    """Compare two previously analyzed policy documents."""
    r1 = await db.execute(select(AnalysisReport).where(AnalysisReport.id == req.report_id_1))
    r2 = await db.execute(select(AnalysisReport).where(AnalysisReport.id == req.report_id_2))
    doc1 = r1.scalar_one_or_none()
    doc2 = r2.scalar_one_or_none()

    if not doc1:
        raise HTTPException(status_code=404, detail=f"Report {req.report_id_1} not found.")
    if not doc2:
        raise HTTPException(status_code=404, detail=f"Report {req.report_id_2} not found.")

    bias_diff = doc1.overall_bias_score - doc2.overall_bias_score
    sdg_diff = doc1.sdg_overall_score - doc2.sdg_overall_score

    title1 = derive_document_title(doc1.document_name)
    title2 = derive_document_title(doc2.document_name)
    top1 = build_top_findings(doc1.flagged_clauses or [])
    top2 = build_top_findings(doc2.flagged_clauses or [])

    issues1 = set(finding.get("finding_title", "") for finding in top1)
    issues2 = set(finding.get("finding_title", "") for finding in top2)
    common = sorted(issue for issue in issues1 & issues2 if issue)
    doc1_unique = sorted(issue for issue in issues1 - issues2 if issue)
    doc2_unique = sorted(issue for issue in issues2 - issues1 if issue)

    if doc1.overall_bias_score == doc2.overall_bias_score:
        better_doc = doc1 if doc1.sdg_overall_score >= doc2.sdg_overall_score else doc2
        weaker_doc = doc2 if better_doc is doc1 else doc1
        better_title = title1 if better_doc is doc1 else title2
        weaker_title = title2 if better_doc is doc1 else title1
        better_findings = top1 if better_doc is doc1 else top2
        weaker_findings = top2 if better_doc is doc1 else top1
    else:
        better_doc = doc1 if doc1.overall_bias_score < doc2.overall_bias_score else doc2
        weaker_doc = doc2 if better_doc is doc1 else doc1
        better_title = title1 if better_doc is doc1 else title2
        weaker_title = title2 if better_doc is doc1 else title1
        better_findings = top1 if better_doc is doc1 else top2
        weaker_findings = top2 if better_doc is doc1 else top1

    better_reason = build_compare_reason(
        better_name=better_title,
        better_bias=better_doc.overall_bias_score,
        better_sdg=better_doc.sdg_overall_score,
        better_findings=better_findings,
        weaker_name=weaker_title,
        weaker_bias=weaker_doc.overall_bias_score,
        weaker_sdg=weaker_doc.sdg_overall_score,
        weaker_findings=weaker_findings,
    )
    summary = (
        f"{title1} scores {doc1.overall_bias_score}/100 for bias risk and {doc1.sdg_overall_score}/100 on SDG alignment. "
        f"{title2} scores {doc2.overall_bias_score}/100 for bias risk and {doc2.sdg_overall_score}/100 on SDG alignment. "
        f"{better_reason}"
    )

    return CompareResponse(
        document_1=doc1.document_name,
        document_2=doc2.document_name,
        document_1_title=title1,
        document_2_title=title2,
        document_1_bias_score=doc1.overall_bias_score,
        document_2_bias_score=doc2.overall_bias_score,
        document_1_sdg_score=doc1.sdg_overall_score,
        document_2_sdg_score=doc2.sdg_overall_score,
        bias_score_diff=abs(bias_diff),
        sdg_score_diff=abs(sdg_diff),
        common_issues=common,
        doc1_unique_issues=doc1_unique,
        doc2_unique_issues=doc2_unique,
        similarity_score=round(1 - abs(bias_diff) / 100, 2),
        better_document=better_title,
        better_document_reason=better_reason,
        document_1_top_findings=[finding["finding_title"] for finding in top1[:3]],
        document_2_top_findings=[finding["finding_title"] for finding in top2[:3]],
        comparison_summary=summary,
    )
