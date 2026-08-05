"""Project 7 integrated prototype components."""

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
from .profile_loader import (
    OrganizationProfileBundle,
    ProfileLoadError,
    load_organization_profile,
)
from .service_alignment import (
    AlignmentError,
    assess_service_alignment,
)

__all__ = [
    "AlignmentError",
    "HistoricalContextError",
    "IntakeError",
    "IntakeResult",
    "OrganizationProfileBundle",
    "ProfileLoadError",
    "assess_service_alignment",
    "attach_historical_context",
    "load_organization_profile",
    "normalize_opportunity",
    "run_intake_from_files",
]
