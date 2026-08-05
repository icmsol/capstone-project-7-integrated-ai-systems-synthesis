"""Project 7 integrated prototype components."""

from .clause_triage import (
    ClauseTriageError,
    Project4InferencePackage,
    TransformerClauseClassifier,
    TransformerModelConfig,
    build_clause_prediction,
    triage_passage,
)
from .decision_support_packet import (
    PacketAssemblyError,
    assemble_decision_support_packet,
    render_packet_markdown,
)
from .evidence_retrieval import (
    EvidenceToolError,
    RegisteredEvidenceCorpus,
)
from .evidence_workflow import (
    EvidenceGroundedAgentWorkflow,
    WorkflowExecution,
)
from .historical_context import (
    HistoricalContextError,
    attach_historical_context,
)
from .opportunity_intake import (
    IntakeError,
    IntakeResult,
    normalize_opportunity,
    run_intake_from_files,
)
from .p4_04_pipeline import run_evidence_workflow
from .p4_05_pipeline import run_packet_assembly
from .profile_loader import (
    OrganizationProfileBundle,
    ProfileLoadError,
    load_organization_profile,
)
from .recommendation_engine import (
    RecommendationError,
    create_nonbinding_recommendation,
)
from .service_alignment import (
    AlignmentError,
    assess_service_alignment,
)

__all__ = [
    "AlignmentError",
    "ClauseTriageError",
    "EvidenceGroundedAgentWorkflow",
    "EvidenceToolError",
    "HistoricalContextError",
    "IntakeError",
    "IntakeResult",
    "OrganizationProfileBundle",
    "PacketAssemblyError",
    "ProfileLoadError",
    "Project4InferencePackage",
    "RecommendationError",
    "RegisteredEvidenceCorpus",
    "TransformerClauseClassifier",
    "TransformerModelConfig",
    "WorkflowExecution",
    "assemble_decision_support_packet",
    "assess_service_alignment",
    "attach_historical_context",
    "build_clause_prediction",
    "create_nonbinding_recommendation",
    "load_organization_profile",
    "normalize_opportunity",
    "render_packet_markdown",
    "run_evidence_workflow",
    "run_intake_from_files",
    "run_packet_assembly",
    "triage_passage",
]
