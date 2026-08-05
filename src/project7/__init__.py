"""Project 7 integrated prototype components."""

from .opportunity_intake import (
    IntakeError,
    IntakeResult,
    normalize_opportunity,
    run_intake_from_files,
)

__all__ = [
    "IntakeError",
    "IntakeResult",
    "normalize_opportunity",
    "run_intake_from_files",
]
