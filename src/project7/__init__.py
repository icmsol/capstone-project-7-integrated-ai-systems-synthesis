"""Project 7 integrated prototype components."""

from .clause_triage import (
    ClauseTriageError,
    Project4InferencePackage,
    TransformerClauseClassifier,
    TransformerModelConfig,
    build_clause_prediction,
    triage_passage,
)
from .historical_context import HistoricalContextError, attach_historical_context
from .opportunity_intake import (
    IntakeError,
    IntakeResult,
    normalize_opportunity,
    run_intake_from_files,
)
from .profile_loader import (
    OrganizationProfileBundle,
    ProfileLoadError,
    load_organization_profile,
)
from .service_alignment import AlignmentError, assess_service_alignment

__all__ = [
    "AlignmentError",
    "ClauseTriageError",
    "HistoricalContextError",
    "IntakeError",
    "IntakeResult",
    "OrganizationProfileBundle",
    "ProfileLoadError",
    "Project4InferencePackage",
    "TransformerClauseClassifier",
    "TransformerModelConfig",
    "assess_service_alignment",
    "attach_historical_context",
    "build_clause_prediction",
    "load_organization_profile",
    "normalize_opportunity",
    "run_intake_from_files",
    "triage_passage",
]
