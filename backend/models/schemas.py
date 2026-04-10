"""
Pydantic request/response models for PolicyLens AI
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid
from datetime import datetime


class BiasType(str, Enum):
    GENDER = "GENDER_BIAS"
    SOCIOECONOMIC = "SOCIOECONOMIC_BIAS"
    ETHNIC = "ETHNIC_CASTE_BIAS"
    REGIONAL = "REGIONAL_BIAS"
    AGE = "AGE_BIAS"
    DISABILITY = "DISABILITY_HEALTH_BIAS"
    PROCEDURAL = "PROCEDURAL_FAIRNESS_BIAS"
    GENERAL = "GENERAL_BIAS"


class LoopholeRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class BiasLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FlaggedClause(BaseModel):
    clause_id: str
    original_text: str
    bias_type: BiasType
    bias_score: int = Field(ge=0, le=100)
    confidence_score: int = Field(default=0, ge=0, le=100)
    finding_title: str = ""
    explanation: str
    why_it_matters: str = ""
    loophole_risk: LoopholeRisk
    plain_english: str
    recommendation: str
    suggested_rewrite: str = ""
    impacted_groups: List[str] = Field(default_factory=list)
    matched_signals: List[str] = Field(default_factory=list)
    sdg_violations: List[str] = Field(default_factory=list)
    sentence_index: Optional[int] = None


class TopFinding(BaseModel):
    finding_title: str
    clause_id: str
    bias_type: BiasType
    bias_score: int = Field(ge=0, le=100)
    loophole_risk: LoopholeRisk
    exact_clause: str
    why_risky: str
    impacted_groups: List[str] = Field(default_factory=list)
    suggested_rewrite: str = ""
    confidence_score: int = Field(default=0, ge=0, le=100)


class SDGScore(BaseModel):
    sdg_number: int
    sdg_name: str
    score: int = Field(ge=0, le=100)
    evidence_clauses: List[str] = Field(default_factory=list)
    alignment_notes: str = ""


class AnalysisRequest(BaseModel):
    url: Optional[str] = None
    language_output: str = "en"


class AnalysisResponse(BaseModel):
    task_id: str
    status: str
    message: str


class AnalysisStatusResponse(BaseModel):
    task_id: str
    status: str  # pending | processing | completed | failed
    progress: int = Field(ge=0, le=100, default=0)
    stage: Optional[str] = None
    result_id: Optional[str] = None
    error: Optional[str] = None


class ReportResponse(BaseModel):
    report_id: str
    document_name: str
    document_title: str
    overall_bias_score: int = Field(ge=0, le=100)
    bias_level: BiasLevel
    sdg_compliance_score: Dict[str, int]
    sdg_overall_score: int
    flagged_clauses: List[FlaggedClause]
    top_findings: List[TopFinding] = Field(default_factory=list)
    impacted_groups: List[str] = Field(default_factory=list)
    evidence_clauses: List[TopFinding] = Field(default_factory=list)
    citizen_summary: str
    recommendations: List[str]
    processing_time_seconds: float
    language: str = "en"
    translation_status: str = "original_en"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    readability_score: Optional[float] = None
    total_clauses_analyzed: int = 0
    demographic_mentions: Dict[str, int] = Field(default_factory=dict)


class CompareRequest(BaseModel):
    report_id_1: str
    report_id_2: str


class CompareResponse(BaseModel):
    document_1: str
    document_2: str
    document_1_title: str
    document_2_title: str
    document_1_bias_score: int
    document_2_bias_score: int
    document_1_sdg_score: int
    document_2_sdg_score: int
    bias_score_diff: int
    sdg_score_diff: int
    common_issues: List[str]
    doc1_unique_issues: List[str]
    doc2_unique_issues: List[str]
    similarity_score: float
    better_document: str
    better_document_reason: str
    document_1_top_findings: List[str] = Field(default_factory=list)
    document_2_top_findings: List[str] = Field(default_factory=list)
    comparison_summary: str
