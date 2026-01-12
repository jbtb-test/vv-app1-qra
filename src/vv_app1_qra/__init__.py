"""
vv_app1_qra
===========

APP1 QRA — Requirement Quality Risk Assessment.

Public API volontairement petite et stable (demo/portfolio).
"""

from .models import (
    AnalysisResult,
    Issue,
    IssueSeverity,
    Requirement,
    Suggestion,
    SuggestionSource,
)
from .rules import analyze_requirement, analyze_requirements, compute_score

__all__ = [
    "AnalysisResult",
    "Issue",
    "IssueSeverity",
    "Requirement",
    "Suggestion",
    "SuggestionSource",
    "analyze_requirement",
    "analyze_requirements",
    "compute_score",
]
