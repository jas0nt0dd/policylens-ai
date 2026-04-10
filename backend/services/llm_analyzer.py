"""
LLM Analyzer — Ollama (Mistral 7B) orchestration with Groq free-tier fallback.
Runs deep analysis and plain-English rewriting via local LLM.
"""
import json
import logging
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger("policylens.llm")

from backend.services.report_utils import build_citizen_summary, build_top_findings, derive_document_title

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # Free tier at console.groq.com
_ollama_unavailable = False
_groq_unavailable = False
_hf_inference_unavailable = False

BIAS_ANALYSIS_PROMPT = """You are a policy analysis AI expert specializing in bias detection and SDG compliance.

Analyze the following policy clause and respond ONLY with valid JSON matching this exact schema:
{{
  "bias_found": true/false,
  "bias_explanation": "Detailed explanation with evidence from the text",
  "bias_types": ["GENDER_BIAS", "SOCIOECONOMIC_BIAS", etc.],
  "sdg_alignment": "Which SDGs this clause aligns with or violates",
  "loopholes": "Any vague language that could be misused",
  "missing_provisions": "What vulnerable groups are excluded",
  "plain_english": "Rewrite this clause at Grade 8 reading level",
  "recommendation": "Specific amendment suggestion"
}}

Policy Clause:
{clause_text}

Respond ONLY with the JSON object. No preamble."""

def run_llm_analysis(sdg_doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run LLM deep analysis on high-bias clauses and generate citizen summary.
    """
    flagged = sdg_doc.get("flagged_clauses", [])
    doc_name = derive_document_title(
        sdg_doc.get("source", "Policy Document"),
        metadata=sdg_doc.get("metadata", {}),
        full_text=sdg_doc.get("full_text", ""),
    )

    # Only send top 10 flagged clauses to LLM to stay within context limits
    top_clauses = sorted(flagged, key=lambda x: x.get("bias_score", 0), reverse=True)[:10]

    enriched_clauses = []
    for clause in top_clauses:
        enriched = _analyze_clause_with_llm(clause)
        enriched_clauses.append(enriched)

    # Update flagged clauses with LLM analysis
    enriched_ids = {c["clause_id"] for c in enriched_clauses}
    all_flagged = enriched_clauses + [c for c in flagged if c["clause_id"] not in enriched_ids]

    top_findings = build_top_findings(all_flagged)
    summary = build_citizen_summary(
        document_title=doc_name,
        bias_score=sdg_doc.get("overall_bias_score", 0),
        bias_level=sdg_doc.get("bias_level", "UNKNOWN"),
        sdg_score=sdg_doc.get("sdg_overall_score", 0),
        top_findings=top_findings,
    )

    # Generate recommendations
    recommendations = _generate_recommendations(all_flagged)

    logger.info(f"LLM analysis complete for {len(enriched_clauses)} clauses")
    return {
        **sdg_doc,
        "flagged_clauses": all_flagged,
        "top_findings": top_findings,
        "citizen_summary": summary,
        "recommendations": recommendations,
    }


def _analyze_clause_with_llm(clause: Dict[str, Any]) -> Dict[str, Any]:
    """Send a single clause to LLM for deep analysis."""
    prompt = BIAS_ANALYSIS_PROMPT.format(clause_text=clause.get("original_text", "")[:800])
    response = _call_llm(prompt)
    if response:
        try:
            data = json.loads(response)
            clause["plain_english"] = data.get("plain_english", clause.get("original_text", ""))
            clause["explanation"] = data.get("bias_explanation", clause.get("explanation", ""))
            clause["recommendation"] = data.get("recommendation", clause.get("recommendation", ""))
            if data.get("loopholes"):
                clause["loophole_risk"] = "HIGH"
        except json.JSONDecodeError:
            # LLM returned non-JSON, extract plain_english heuristically
            if "plain english" in response.lower():
                parts = response.split("plain_english")
                if len(parts) > 1:
                    clause["plain_english"] = parts[1][:300].strip(' :"')
    return clause

def _generate_recommendations(flagged_clauses: List[Dict]) -> List[str]:
    """Aggregate top recommendations from all flagged clauses."""
    recs = set()
    for clause in flagged_clauses[:15]:
        rec = clause.get("suggested_rewrite") or clause.get("recommendation", "")
        if rec and len(rec) > 20:
            recs.add(rec)
    return list(recs)[:8]


def _call_llm(prompt: str, max_tokens: int = 500) -> Optional[str]:
    """
    Call LLM with fallback chain: Ollama → Groq Free API → HuggingFace Inference API
    """
    # 1. Try Ollama (local)
    response = _call_ollama(prompt, max_tokens)
    if response:
        return response

    # 2. Try Groq Free API
    if GROQ_API_KEY:
        response = _call_groq(prompt, max_tokens)
        if response:
            return response

    # 3. Try HuggingFace Inference API (free tier)
    response = _call_hf_inference(prompt, max_tokens)
    return response


def _call_ollama(prompt: str, max_tokens: int) -> Optional[str]:
    """Call local Ollama instance."""
    global _ollama_unavailable

    if _ollama_unavailable:
        return None

    try:
        import requests
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": max_tokens, "temperature": 0.2},
            },
            timeout=60,
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
        _ollama_unavailable = True
    except Exception as e:
        logger.debug(f"Ollama unavailable: {e}")
        _ollama_unavailable = True
    return None


def _call_groq(prompt: str, max_tokens: int) -> Optional[str]:
    """Call Groq free-tier API (ultra-fast inference)."""
    global _groq_unavailable

    if _groq_unavailable:
        return None

    try:
        import requests
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.2,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
        _groq_unavailable = True
    except Exception as e:
        logger.debug(f"Groq API error: {e}")
        _groq_unavailable = True
    return None


def _call_hf_inference(prompt: str, max_tokens: int) -> Optional[str]:
    """Fallback: HuggingFace free inference API."""
    global _hf_inference_unavailable

    if _hf_inference_unavailable:
        return None

    try:
        import requests
        resp = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
            headers={"Content-Type": "application/json"},
            json={"inputs": prompt[:1000], "parameters": {"max_new_tokens": max_tokens}},
            timeout=45,
        )
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and data:
                return data[0].get("generated_text", "").replace(prompt, "").strip()
        _hf_inference_unavailable = True
    except Exception as e:
        logger.debug(f"HF inference error: {e}")
        _hf_inference_unavailable = True
    return None
