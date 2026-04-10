"""
Report Generator — aggregates all pipeline outputs into final ReportResponse.
"""
import uuid
import time
import logging
from typing import Dict, Any

from backend.services.report_utils import (
    build_top_findings,
    build_translation_status,
    collect_impacted_groups,
    derive_document_title,
)

logger = logging.getLogger("policylens.report")


def generate_report(llm_doc: Dict[str, Any], document_name: str,
                    processing_start: float, language: str = "en") -> Dict[str, Any]:
    """
    Aggregate the full pipeline output into a structured report.
    """
    import textstat

    report_id = str(uuid.uuid4())
    full_text = llm_doc.get("full_text", "")
    document_title = derive_document_title(
        document_name=document_name,
        metadata=llm_doc.get("metadata", {}),
        full_text=full_text,
    )

    # Readability
    try:
        readability = textstat.flesch_kincaid_grade(full_text[:5000])
    except Exception:
        readability = None

    # Translate summary if needed
    summary = llm_doc.get("citizen_summary", "Analysis complete.")
    summary_language = "en"
    if language != "en":
        from backend.services.translator import translate_report_summary

        translated_summary = translate_report_summary(summary, language)
        if translated_summary and translated_summary != summary:
            summary = translated_summary
            summary_language = language

    top_findings = build_top_findings(llm_doc.get("flagged_clauses", []))
    impacted_groups = collect_impacted_groups(llm_doc.get("flagged_clauses", []))

    report = {
        "report_id": report_id,
        "document_name": document_title,
        "overall_bias_score": llm_doc.get("overall_bias_score", 0),
        "bias_level": llm_doc.get("bias_level", "LOW"),
        "sdg_scores": llm_doc.get("sdg_scores", {}),
        "sdg_overall_score": llm_doc.get("sdg_overall_score", 50),
        "flagged_clauses": llm_doc.get("flagged_clauses", [])[:20],  # cap at 20
        "top_findings": top_findings,
        "impacted_groups": impacted_groups,
        "citizen_summary": summary,
        "recommendations": llm_doc.get("recommendations", []),
        "processing_time": round(time.time() - processing_start, 2),
        "language": summary_language,
        "translation_status": build_translation_status(summary_language),
        "readability_score": readability,
        "total_clauses": len(llm_doc.get("clauses", [])),
        "demographic_mentions": llm_doc.get("demographic_mentions", {}),
    }

    logger.info(f"Report generated: {report_id}, bias={report['overall_bias_score']}, sdg={report['sdg_overall_score']}")
    return report
