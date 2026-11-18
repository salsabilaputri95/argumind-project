from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class UserRole(StrEnum):
    AUTHOR = "author"
    REVIEWER = "reviewer"
    ANNOTATOR = "annotator"
    ORG_ADMIN = "org_admin"


class DomainStrata(StrEnum):
    ACADEMIC = "academic"
    POLICY_BUSINESS = "policy_business"


class SourceFormat(StrEnum):
    TXT = "txt"
    MD = "md"
    DOCX = "docx"
    PDF = "pdf"


class RunSource(StrEnum):
    AI_HYBRID = "ai_hybrid"
    HUMAN_ANNOTATOR = "human_annotator"
    GOLD_ADJUDICATED = "gold_adjudicated"


class RunStatus(StrEnum):
    QUEUED = "QUEUED"
    STAGE_1_STRUCTURE = "STAGE_1_STRUCTURE"
    STAGE_2_IMPLICIT = "STAGE_2_IMPLICIT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SCORING_VALIDATION_FAILED = "SCORING_VALIDATION_FAILED"


class NodeType(StrEnum):
    CLAIM = "Claim"
    EXPLICIT_PREMISE = "ExplicitPremise"
    IMPLICIT_PREMISE = "ImplicitPremise"
    EVIDENCE = "Evidence"
    COUNTERARGUMENT = "Counterargument"


class RelationType(StrEnum):
    SUPPORT = "Support"
    ATTACK = "Attack"


class GapType(StrEnum):
    UNSUPPORTED_CLAIM = "UnsupportedClaim"
    HASTY_GENERALIZATION = "HastyGeneralization"
    FALSE_CAUSE = "FalseCause"
    CIRCULAR_REASONING = "CircularReasoning"
    MISSING_COUNTERARGUMENT = "MissingCounterargumentConsideration"
    WEAK_EVIDENCE = "WeakEvidence"


class SeverityLevel(StrEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class RubricDimension(StrEnum):
    CLARITY_OF_CLAIM = "ClarityOfClaim"
    PREMISE_SUPPORT_AND_COHERENCE = "PremiseSupportAndCoherence"
    EVIDENCE_ADEQUACY = "EvidenceAdequacy"
    COUNTERARGUMENT_AND_LIMITATION = "CounterargumentAndLimitationAwareness"


class FeedbackStatus(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


SPAN_NODE_TYPES: frozenset[NodeType] = frozenset(
    {NodeType.CLAIM, NodeType.EXPLICIT_PREMISE, NodeType.EVIDENCE}
)
GENERATED_NODE_TYPES: frozenset[NodeType] = frozenset(
    {NodeType.IMPLICIT_PREMISE, NodeType.COUNTERARGUMENT}
)


class ArgumentNodeSchema(BaseModel):
    """Komponen graf argumen sesuai kontrak docs/DATA_MODEL.md#1.6."""

    node_key: str = Field(..., min_length=2, max_length=16)
    node_type: NodeType
    start_char: int | None = Field(default=None, ge=0)
    end_char: int | None = Field(default=None, ge=1)
    text_content: str = Field(..., min_length=1)
    evidence_strength: int | None = Field(default=None, ge=1, le=5)
    target_node_key: str | None = Field(default=None, max_length=16)
    user_feedback: FeedbackStatus = FeedbackStatus.PENDING

    @model_validator(mode="after")
    def validate_span_and_type_rules(self) -> ArgumentNodeSchema:
        if self.node_type in SPAN_NODE_TYPES:
            if self.start_char is None or self.end_char is None:
                raise ValueError("Komponen eksplisit wajib memiliki start_char dan end_char.")
            if self.end_char <= self.start_char:
                raise ValueError("end_char wajib lebih besar dari start_char.")
        elif self.node_type in GENERATED_NODE_TYPES:
            if self.start_char is not None or self.end_char is not None:
                raise ValueError("ImplicitPremise/Counterargument wajib memiliki span null.")
            if not self.target_node_key:
                raise ValueError("ImplicitPremise/Counterargument wajib merujuk target_node_key.")
        if self.node_type == NodeType.EVIDENCE and self.evidence_strength is None:
            raise ValueError("Komponen Evidence wajib memiliki evidence_strength (1..5).")
        return self


class ArgumentEdgeSchema(BaseModel):
    """Relasi graf berarah antar komponen argumen tanpa self-loop."""

    edge_key: str = Field(..., min_length=2, max_length=16)
    source_key: str = Field(..., min_length=2, max_length=16)
    target_key: str = Field(..., min_length=2, max_length=16)
    relation_type: RelationType
    confidence: float = Field(..., ge=0.0, le=1.0)
    nli_probs: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_no_self_loop(self) -> ArgumentEdgeSchema:
        if self.source_key == self.target_key:
            raise ValueError("Self-loop dilarang: source_key tidak boleh sama dengan target_key.")
        return self


class ReasoningGapSchema(BaseModel):
    """Celah penalaran terstruktur pada node atau edge."""

    gap_key: str = Field(..., min_length=2, max_length=16)
    gap_type: GapType
    severity: SeverityLevel
    target_node_key: str | None = None
    target_edge_key: str | None = None
    explanation: str = Field(..., min_length=5)

    @model_validator(mode="after")
    def validate_target_ref(self) -> ReasoningGapSchema:
        if not self.target_node_key and not self.target_edge_key:
            raise ValueError("ReasoningGap wajib merujuk target_node_key atau target_edge_key.")
        return self


class RubricScoreSchema(BaseModel):
    """Skor rubrik 1..5 yang wajib memiliki minimal satu grounded_refs valid."""

    dimension: RubricDimension
    ai_score: int = Field(..., ge=1, le=5)
    grounded_refs: list[str] = Field(..., min_length=1)
    rationale: str = Field(..., min_length=5)
    human_override_score: int | None = Field(default=None, ge=1, le=5)
    reviewer_id: str | None = None
    override_note: str | None = None

    @model_validator(mode="after")
    def validate_override_consistency(self) -> RubricScoreSchema:
        if self.human_override_score is not None:
            if not self.override_note or len(self.override_note.strip()) < 10:
                raise ValueError("override_note wajib diisi minimal 10 karakter saat override.")
        return self


class ProblemDetails(BaseModel):
    """Format error standar RFC 9457."""

    type: str
    title: str
    status: int
    code: str
    detail: str
    trace_id: str
    extra: dict[str, Any] | None = None
