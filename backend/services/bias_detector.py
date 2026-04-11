"""
Bias Detector — deterministic clause scoring with optional HuggingFace support.
Focuses on explicit exclusion, procedural unfairness, and policy loopholes.
"""
from __future__ import annotations

import logging
import re
from copy import deepcopy
from typing import Any, Dict, List

logger = logging.getLogger("policylens.bias")

HF_BIAS_MODEL_NAME = "d4data/bias-detection-model"
_bias_classifier = None
_bias_classifier_unavailable = False


RULES: List[Dict[str, Any]] = [
    {
        "id": "gendered_worker_terms",
        "title": "Gendered 'workman/workmen' terminology",
        "bias_type": "GENDER_BIAS",
        "patterns": [r"\bworkman\b", r"\bworkmen\b", r"\bmanpower\b", r"\bchairman\b", r"\bpoliceman\b"],
        "weight": 36,
        "why": "Male-coded legal terms can exclude women and non-binary people from rights, remedies, or interpretation.",
        "groups": ["women workers", "non-binary workers"],
        "rewrite": "Use gender-neutral terms such as 'worker', 'employee', or 'chairperson' throughout the clause.",
    },
    {
        "id": "marital_or_gender_leave_gap",
        "title": "Unequal leave rights based on gender or marital status",
        "bias_type": "GENDER_BIAS",
        "patterns": [r"\bwomen employees who are married\b", r"\bmale employees shall be entitled to\b", r"\bmarried shall be entitled\b"],
        "weight": 35,
        "why": "Benefits tied to gender roles or marital status can reinforce discriminatory assumptions about care work and family rights.",
        "groups": ["women employees", "single parents", "caregivers"],
        "rewrite": "Offer leave entitlements using equal, gender-neutral eligibility rules based on caregiving needs rather than marital status.",
    },
    {
        "id": "income_or_employment_exclusion",
        "title": "Income threshold and contract/gig worker exclusion",
        "bias_type": "SOCIOECONOMIC_BIAS",
        "patterns": [
            r"\bearning above\b",
            r"\bannual income above\b",
            r"\bminimum income\b",
            r"\bpermanent employees\b",
            r"\bcontract workers\b",
            r"\bgig economy workers\b",
            r"\bexcluded from the provisions\b",
            r"\bonly to\b",
        ],
        "weight": 60,
        "why": "Restricting benefits to higher-income or permanent workers can exclude the people who are often most vulnerable and least protected.",
        "groups": ["contract workers", "gig workers", "low-income workers", "informal workers"],
        "rewrite": "Set eligibility using objective need and include permanent, contract, and gig workers unless a narrowly tailored exception is justified in writing.",
    },
    {
        "id": "regional_priority_gap",
        "title": "Urban tier-1 preference over rural or tier-3 workers",
        "bias_type": "REGIONAL_BIAS",
        "patterns": [r"\btier-1 cities\b", r"\burban employees\b", r"\brural areas\b", r"\btier-3 towns\b", r"\bbasic benefits only\b"],
        "weight": 56,
        "why": "Giving stronger benefits to urban or tier-1 workers can deepen existing inequality in access to public support.",
        "groups": ["rural workers", "small-town workers", "underserved regions"],
        "rewrite": "Provide equivalent baseline benefits across regions and justify any location-based variation with transparent public-interest criteria.",
    },
    {
        "id": "disability_or_illness_exclusion",
        "title": "Disability or illness-based pension exclusion",
        "bias_type": "DISABILITY_HEALTH_BIAS",
        "patterns": [r"\bdue to disability or illness\b", r"\bshall not be eligible unless specifically approved\b", r"\bunless specifically approved\b"],
        "weight": 60,
        "why": "Penalizing people for disability, illness, or interrupted service can unlawfully block access to social protection.",
        "groups": ["workers with disabilities", "chronically ill workers", "older workers"],
        "rewrite": "Allow equivalent pension eligibility when service is interrupted by disability, illness, or caregiving, with a clear accommodation pathway.",
    },
    {
        "id": "broad_government_discretion",
        "title": "Broad government discretion and weak appeal rights",
        "bias_type": "PROCEDURAL_FAIRNESS_BIAS",
        "patterns": [
            r"\bat (?:its|the) discretion\b",
            r"\bdeemed appropriate\b",
            r"\bdeemed necessary\b",
            r"\bextend or restrict\b",
            r"\bsubject to such procedures as may be prescribed\b",
            r"\bwithout prior consultation\b",
        ],
        "weight": 36,
        "why": "Open-ended discretion lets authorities change rights without transparent standards, oversight, or affected-community input.",
        "groups": ["all affected workers", "applicants", "communities subject to the policy"],
        "rewrite": "Replace open-ended discretion with published eligibility rules, written reasons, consultation requirements, and independent review.",
    },
    {
        "id": "weak_appeal_rights",
        "title": "Broad government discretion and weak appeal rights",
        "bias_type": "PROCEDURAL_FAIRNESS_BIAS",
        "patterns": [r"\bfinal and binding\b", r"\bno further right of appeal\b", r"\bexcept as may be prescribed\b"],
        "weight": 38,
        "why": "Finality clauses can deny due process and leave affected people without a meaningful route to challenge an unfair decision.",
        "groups": ["workers denied benefits", "complainants", "affected families"],
        "rewrite": "Guarantee written reasons, a time-bound appeal, and access to independent review before a decision becomes final.",
    },
    {
        "id": "exclusionary_community_language",
        "title": "Exclusionary or stigmatizing community language",
        "bias_type": "ETHNIC_CASTE_BIAS",
        "patterns": [
            r"\billegal alien\b",
            r"\bbackward class\b",
            r"\bprimitive\b",
            r"\buncivilized\b",
            r"\bupper caste\b",
            r"\blower caste\b",
            r"\buntouchable\b",
        ],
        "weight": 40,
        "why": "Stigmatizing or caste-coded labels can directly discriminate against protected communities and legitimize unequal treatment.",
        "groups": ["marginalized communities", "minority groups", "caste-affected groups"],
        "rewrite": "Remove stigmatizing labels and replace them with rights-based, non-discriminatory language that applies equally to all communities.",
    },
]


def detect_bias(semantic_doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run clause-level bias detection and compute a stronger overall risk score.
    """
    clauses = semantic_doc.get("clauses", [])
    flagged = []
    total_score = 0

    for clause in clauses:
        result = _analyze_clause_bias(
            clause.get("text", ""),
            clause.get("clause_id", ""),
            clause.get("index"),
        )
        total_score += result["bias_score"]
        if result["bias_score"] >= 25 or result["loophole_risk"] == "HIGH":
            flagged.append(result)

    overall = _compute_overall_score(flagged, len(clauses), total_score)
    bias_level = _score_to_level(overall)

    logger.info("Bias detection: %s flagged clauses, overall score=%s", len(flagged), overall)
    return {
        **semantic_doc,
        "flagged_clauses": flagged,
        "overall_bias_score": overall,
        "bias_level": bias_level,
    }


def _analyze_clause_bias(text: str, clause_id: str, sentence_index: int | None = None) -> Dict[str, Any]:
    text_lower = text.lower()
    matched_rules: List[Dict[str, Any]] = []
    rule_matches: List[str] = []
    impacted_groups: List[str] = []
    why_parts: List[str] = []
    total_weight = 0

    for rule in RULES:
        matched_terms = _find_rule_matches(rule["patterns"], text_lower)
        if not matched_terms:
            continue
        matched_rules.append(rule)
        rule_matches.extend(matched_terms)
        impacted_groups.extend(rule["groups"])
        why_parts.append(rule["why"])
        total_weight += rule["weight"]

    # ADD — explicit percentage-based discrimination
    pay_gap_patterns = [
        "wage adjustment", "15% lower", "lower than male", "productivity considerations",
        "consent from husband", "consent from father", "letter of consent",
        "reduced maternity", "4 weeks without pay",
    ]
    for term in pay_gap_patterns:
        if term.lower() in text_lower:
            total_weight += 35
            if not matched_rules or matched_rules[0].get("bias_type") != "GENDER_BIAS":
                rule_matches.append(f"Explicit gender discrimination: '{term}' found")
                why_parts.append(f"Explicit gender discrimination: '{term}' found")

    # ADD — disability discrimination
    disability_patterns = ["50% of the standard rate", "degree of disability", 
                            "persons with disabilities shall", "disability shall receive pension at"]
    for term in disability_patterns:
        if term.lower() in text_lower:
            total_weight += 30
            if not matched_rules or matched_rules[0].get("bias_type") != "DISABILITY_HEALTH_BIAS":
                rule_matches.append(f"Disability discrimination: '{term}' found")
                why_parts.append(f"Disability discrimination: '{term}' found")

    # ADD — child labour
    if "children above the age of 12" in text_lower or "employment of children" in text_lower:
        total_weight += 50
        if not matched_rules or matched_rules[0].get("bias_type") != "AGE_BIAS":
            rule_matches.append("Child labour provision detected")
            why_parts.append("Child labour provision detected")

    loophole_risk = _detect_loophole(text)
    if loophole_risk == "HIGH":
        total_weight += 14
        if not matched_rules:
            matched_rules.append(
                {
                    "id": "high_loophole_risk",
                    "title": "High-risk loophole and discretion language",
                    "bias_type": "PROCEDURAL_FAIRNESS_BIAS",
                    "why": "Vague discretion clauses can be misused because they do not define objective standards or review rights.",
                    "groups": ["people affected by administrative decisions"],
                    "rewrite": "Define objective criteria, written reasons, and a right to appeal before the clause can be used.",
                }
            )
            why_parts.append(matched_rules[-1]["why"])
            impacted_groups.extend(matched_rules[-1]["groups"])
            rule_matches.append("vague discretion language")

    hf_score = _run_hf_bias_model(text)
    if hf_score is not None:
        total_weight = int(total_weight * 0.75 + hf_score * 0.25)

    primary_rule = max(
        matched_rules,
        key=lambda rule: next((candidate["weight"] for candidate in RULES if candidate["id"] == rule["id"]), 30),
        default={
            "title": "General fairness concern",
            "bias_type": "GENERAL_BIAS",
            "why": "The clause contains language that may create unequal outcomes or weak accountability.",
            "groups": ["affected policy beneficiaries"],
            "rewrite": "Clarify the clause with equal eligibility standards, transparent reasoning, and review rights.",
        },
    )

    bias_score = min(total_weight, 100)
    confidence_score = _compute_confidence_score(matched_rules, loophole_risk, hf_score)
    impacted_groups = _unique_preserve_order(impacted_groups)[:6]
    rule_matches = _unique_preserve_order(rule_matches)[:8]
    explanation = "; ".join(_unique_preserve_order(why_parts)) if why_parts else "No strong bias signal was detected."

    return {
        "clause_id": clause_id,
        "original_text": text[:800],
        "bias_type": primary_rule["bias_type"],
        "bias_score": bias_score,
        "confidence_score": confidence_score,
        "finding_title": primary_rule["title"],
        "explanation": explanation,
        "why_it_matters": primary_rule["why"],
        "loophole_risk": loophole_risk,
        "plain_english": text,
        "recommendation": primary_rule["rewrite"],
        "suggested_rewrite": primary_rule["rewrite"],
        "impacted_groups": impacted_groups,
        "matched_signals": rule_matches,
        "sdg_violations": [],
        "sentence_index": sentence_index,
    }


def _find_rule_matches(patterns: List[str], text_lower: str) -> List[str]:
    matches = []
    for pattern in patterns:
        found = re.finditer(pattern, text_lower)
        for match in found:
            matches.append(match.group(0))
    return matches


def _compute_overall_score(flagged: List[Dict[str, Any]], total_clauses: int, total_score: int) -> int:
    if flagged:
        top_scores = sorted([f["bias_score"] for f in flagged], reverse=True)[:20]
        flagged_avg = int(sum(top_scores) / len(top_scores))
        all_avg = int(total_score / max(total_clauses, 1))
        overall = int(flagged_avg * 0.7 + all_avg * 0.3)  # weight toward worst clauses
    else:
        overall = int(total_score / max(total_clauses, 1))
    return overall


def _compute_confidence_score(matched_rules: List[Dict[str, Any]], loophole_risk: str, hf_score: float | None) -> int:
    base = 45 + len(matched_rules) * 12
    if loophole_risk == "HIGH":
        base += 12
    if hf_score is not None:
        base += 8
    if any(rule.get("bias_type") != "GENERAL_BIAS" for rule in matched_rules):
        base += 10
    return min(base, 97)


def _run_hf_bias_model(text: str) -> float | None:
    classifier = _get_hf_bias_classifier()
    if classifier is None:
        return None

    try:
        result = classifier(text[:512])[0]
        if result["label"] == "LABEL_1":
            return result["score"] * 100
        return result["score"] * 10
    except Exception as exc:
        logger.debug("HF bias model unavailable: %s", exc)
        return None


def _get_hf_bias_classifier():
    global _bias_classifier, _bias_classifier_unavailable

    if _bias_classifier_unavailable:
        return None
    if _bias_classifier is not None:
        return _bias_classifier

    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

        tokenizer = AutoTokenizer.from_pretrained(HF_BIAS_MODEL_NAME, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(HF_BIAS_MODEL_NAME, local_files_only=True)
        _bias_classifier = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer,
            truncation=True,
            max_length=512,
        )
        return _bias_classifier
    except Exception as exc:
        logger.info("HF bias model unavailable locally (%s). Using rule-based scoring.", exc)
        _bias_classifier_unavailable = True
        return None


def _detect_loophole(text: str) -> str:
    vague_patterns = [
        r"\bas\s+(?:may\s+be\s+)?deemed\s+(?:fit|appropriate|necessary)\b",
        r"\bat\s+(?:its|the)\s+discretion\s+of\b",
        r"\bat\s+its\s+discretion\b",
        r"\bsubject\s+to\s+(?:such\s+)?conditions?\s+as\s+may\s+be\b",
        r"\bnotwithstanding\s+anything\b",
        r"\bin\s+such\s+manner\s+as\s+(?:may\s+be\s+)?prescribed\b",
        r"\bno\s+further\s+right\s+of\s+appeal\b",
        r"\bwithout\s+prior\s+consultation\b",
    ]
    text_lower = text.lower()
    for pattern in vague_patterns:
        if re.search(pattern, text_lower):
            return "HIGH"
    if len(text.split()) > 40 and any(word in text_lower for word in ["may", "might", "could", "unless"]):
        return "MEDIUM"
    return "LOW"


def _score_to_level(score: int) -> str:
    if score >= 75:
        return "CRITICAL"
    if score >= 55:
        return "HIGH"
    if score >= 35:
        return "MODERATE"
    return "LOW"


def _unique_preserve_order(values: List[str]) -> List[str]:
    seen = set()
    ordered = []
    for value in values:
        key = value.lower()
        if key not in seen:
            seen.add(key)
            ordered.append(value)
    return ordered
