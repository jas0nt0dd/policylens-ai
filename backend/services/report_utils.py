"""
Utilities for turning clause-level analysis into judge-friendly report content.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterable, List


def derive_document_title(document_name: str, metadata: Dict[str, Any] | None = None, full_text: str = "") -> str:
    """Return a human-readable policy title."""
    metadata = metadata or {}

    explicit_title = str(metadata.get("title", "")).strip()
    if explicit_title and len(explicit_title.split()) >= 2:
        return _normalize_title(explicit_title)

    for line in full_text.splitlines()[:6]:
        cleaned = line.strip().strip("-: ")
        if len(cleaned.split()) >= 2 and 6 <= len(cleaned) <= 120:
            return _normalize_title(cleaned)

    stem = Path(document_name or "policy_document").stem
    stem = re.sub(r"[_\-]+", " ", stem).strip()
    return _normalize_title(stem or "Policy Document")


def build_top_findings(flagged_clauses: Iterable[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    ranked = sorted(
        flagged_clauses,
        key=lambda clause: (
            clause.get("bias_score", 0),
            clause.get("confidence_score", 0),
            1 if clause.get("loophole_risk") == "HIGH" else 0,
        ),
        reverse=True,
    )

    findings = []
    seen_titles = set()
    for clause in ranked:
        title = clause.get("finding_title") or clause.get("bias_type", "Policy concern").replace("_", " ")
        if title in seen_titles and len(findings) < limit:
            continue
        seen_titles.add(title)
        findings.append(
            {
                "finding_title": title,
                "clause_id": clause.get("clause_id", ""),
                "bias_type": clause.get("bias_type", "GENERAL_BIAS"),
                "bias_score": clause.get("bias_score", 0),
                "loophole_risk": clause.get("loophole_risk", "LOW"),
                "exact_clause": clause.get("original_text", ""),
                "why_risky": clause.get("why_it_matters") or clause.get("explanation", ""),
                "impacted_groups": clause.get("impacted_groups", []),
                "suggested_rewrite": clause.get("suggested_rewrite") or clause.get("recommendation", ""),
                "confidence_score": clause.get("confidence_score", 0),
            }
        )
        if len(findings) >= limit:
            break
    return findings


def collect_impacted_groups(flagged_clauses: Iterable[Dict[str, Any]]) -> List[str]:
    groups: List[str] = []
    seen = set()
    for clause in flagged_clauses:
        for group in clause.get("impacted_groups", []):
            key = group.lower()
            if key not in seen:
                seen.add(key)
                groups.append(group)
    return groups


def build_translation_status(language: str) -> str:
    if language and language.lower() != "en":
        return f"translated_{language.lower()}"
    return "original_en"


def build_citizen_summary(
    document_title: str,
    bias_score: int,
    bias_level: str,
    sdg_score: int,
    top_findings: List[Dict[str, Any]],
) -> str:
    """Create a specific, clause-backed summary without depending on an external LLM."""
    if not top_findings:
        return (
            f"{document_title} was reviewed for discrimination, loopholes, and SDG alignment. "
            f"It received a bias score of {bias_score}/100 ({bias_level}) and an SDG score of {sdg_score}/100. "
            "No major clause-level risks were strongly evidenced in this run, so a manual legal review is still recommended."
        )

    intros = {
        "LOW": "shows some limited fairness concerns",
        "MODERATE": "contains meaningful risks that should be fixed before adoption",
        "HIGH": "contains serious discrimination and governance risks",
        "CRITICAL": "contains severe exclusion and accountability failures",
    }
    intro = intros.get(bias_level, "contains policy risks")

    lead = (
        f"{document_title} {intro}. "
        f"It scored {bias_score}/100 for bias risk and {sdg_score}/100 for SDG alignment. "
    )

    detail_bits = [finding.get("finding_title", "policy concern").lower() for finding in top_findings[:5]]
    detail_sentence = f"Top clause-backed concerns include {_join_with_commas(detail_bits)}"
    groups = collect_impacted_groups(top_findings)
    group_sentence = ""
    if groups:
        group_sentence = f" The groups most affected include {_join_with_commas(groups[:5])}."

    close = " These clauses should be rewritten with clear eligibility rules, equal treatment, and real appeal rights before the policy is used."
    return (lead + detail_sentence.capitalize() + "." + group_sentence + close).strip()


def build_compare_reason(
    better_name: str,
    better_bias: int,
    better_sdg: int,
    better_findings: List[Dict[str, Any]],
    weaker_name: str,
    weaker_bias: int,
    weaker_sdg: int,
    weaker_findings: List[Dict[str, Any]],
) -> str:
    stronger_issue = weaker_findings[0]["finding_title"].lower() if weaker_findings else "fewer severe risks"
    cleaner_issue = better_findings[0]["finding_title"].lower() if better_findings else "fewer severe risks"
    return (
        f"{better_name} performs better because its bias score is lower ({better_bias} vs {weaker_bias}) "
        f"while its SDG score is stronger ({better_sdg} vs {weaker_sdg}). "
        f"{weaker_name} is held back by {stronger_issue}, while {better_name} shows {cleaner_issue} or fewer severe exclusions."
    )


def _normalize_title(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value).strip()
    if cleaned.isupper():
        return cleaned.title()
    return cleaned


def _join_with_commas(parts: List[str]) -> str:
    clean = [part for part in parts if part]
    if not clean:
        return ""
    if len(clean) == 1:
        return clean[0]
    if len(clean) == 2:
        return f"{clean[0]} and {clean[1]}"
    return ", ".join(clean[:-1]) + f", and {clean[-1]}"
