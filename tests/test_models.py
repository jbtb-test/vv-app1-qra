#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
tests.test_models
------------------------------------------------------------
Description :
    Tests unitaires pytest — APP1 QRA — modèles (models.py)

Objectifs :
    - Création nominale
    - Validation des entrées (ValueError)
    - Sérialisation / désérialisation (to_dict/from_dict)
    - Conversions Enum strictes

Usage :
    pytest -q
============================================================
"""

from __future__ import annotations

import pytest

from vv_app1_qra.models import (
    AnalysisResult,
    Issue,
    IssueSeverity,
    Requirement,
    Suggestion,
    SuggestionSource,
)


# ============================================================
# 🔧 Fixtures
# ============================================================
@pytest.fixture
def sample_requirement() -> Requirement:
    return Requirement(
        req_id="REQ-001",
        title="Train Control / Brake / High",
        text="The braking system shall stop the train within 800 m.",
        source="Stakeholder",
        system="Train Control",
        component="Brake",
        priority="High",
        acceptance_criteria="Stopping distance <= 800 m in 10 runs.",
    )


# ============================================================
# 🧪 Tests — Requirement
# ============================================================
def test_requirement_nominal(sample_requirement: Requirement):
    assert sample_requirement.req_id == "REQ-001"
    assert sample_requirement.title != ""
    assert sample_requirement.text != ""


def test_requirement_validation_req_id_empty():
    with pytest.raises(ValueError):
        Requirement(req_id="", title="t", text="x")


def test_requirement_validation_title_and_text_empty():
    with pytest.raises(ValueError):
        Requirement(req_id="REQ-XXX", title="", text="")


def test_requirement_roundtrip_dict(sample_requirement: Requirement):
    d = sample_requirement.to_dict()
    out = Requirement.from_dict(d)
    assert out == sample_requirement


# ============================================================
# 🧪 Tests — Issue
# ============================================================
def test_issue_nominal():
    i = Issue(
        rule_id="R-AMB-001",
        category="Ambiguity",
        severity=IssueSeverity.MAJOR,
        message="Ambiguous term detected: 'quickly'.",
        field="text",
        evidence="quickly",
        recommendation="Replace with measurable timing (ms).",
    )
    assert i.severity == IssueSeverity.MAJOR
    assert i.to_dict()["severity"] == "MAJOR"


def test_issue_from_dict_accepts_enum_value():
    d = {
        "rule_id": "R-TST-001",
        "category": "Testability",
        "severity": "CRITICAL",
        "message": "No acceptance criteria.",
    }
    i = Issue.from_dict(d)
    assert i.severity == IssueSeverity.CRITICAL


def test_issue_from_dict_rejects_unknown_severity():
    d = {
        "rule_id": "R-TST-001",
        "category": "Testability",
        "severity": "BLOCKER",
        "message": "Invalid severity value.",
    }
    with pytest.raises(ValueError):
        Issue.from_dict(d)


def test_issue_validation_requires_fields():
    with pytest.raises(ValueError):
        Issue(rule_id="", category="Ambiguity", severity=IssueSeverity.MINOR, message="x")
    with pytest.raises(ValueError):
        Issue(rule_id="R1", category="", severity=IssueSeverity.MINOR, message="x")
    with pytest.raises(ValueError):
        Issue(rule_id="R1", category="Ambiguity", severity=IssueSeverity.MINOR, message="")


# ============================================================
# 🧪 Tests — Suggestion
# ============================================================
def test_suggestion_nominal():
    s = Suggestion(
        source=SuggestionSource.RULE,
        message="Add measurable acceptance criteria.",
        rule_id="R-AC-001",
        rationale="Criteria are missing or vague.",
    )
    assert s.source == SuggestionSource.RULE
    assert s.to_dict()["source"] == "RULE"


def test_suggestion_validation_message_required():
    with pytest.raises(ValueError):
        Suggestion(source=SuggestionSource.AI, message="")


def test_suggestion_validation_confidence_range():
    with pytest.raises(ValueError):
        Suggestion(source=SuggestionSource.AI, message="x", confidence=-0.1)
    with pytest.raises(ValueError):
        Suggestion(source=SuggestionSource.AI, message="x", confidence=1.1)


def test_suggestion_from_dict_strict_source():
    ok = Suggestion.from_dict({"source": "AI", "message": "Propose rewrite", "confidence": 0.8})
    assert ok.source == SuggestionSource.AI

    with pytest.raises(ValueError):
        Suggestion.from_dict({"source": "LLM", "message": "x"})


# ============================================================
# 🧪 Tests — AnalysisResult
# ============================================================
def test_analysis_result_roundtrip(sample_requirement: Requirement):
    i = Issue(
        rule_id="R-AMB-001",
        category="Ambiguity",
        severity=IssueSeverity.MINOR,
        message="Ambiguous term detected.",
    )
    s = Suggestion(source=SuggestionSource.RULE, message="Clarify term.", rule_id="R-AMB-001")

    ar = AnalysisResult(requirement=sample_requirement, issues=[i], suggestions=[s], score=80, status="CHECKED")
    d = ar.to_dict()
    out = AnalysisResult.from_dict(d)

    assert out.requirement == sample_requirement
    assert len(out.issues) == 1
    assert out.issues[0].severity == IssueSeverity.MINOR
    assert len(out.suggestions) == 1
    assert out.suggestions[0].source == SuggestionSource.RULE
    assert out.score == 80
    assert out.status == "CHECKED"


def test_analysis_result_score_validation(sample_requirement: Requirement):
    with pytest.raises(ValueError):
        AnalysisResult(requirement=sample_requirement, score=101)
    with pytest.raises(ValueError):
        AnalysisResult(requirement=sample_requirement, score=-1)
    with pytest.raises(ValueError):
        AnalysisResult(requirement=sample_requirement, score=12.5)  # type: ignore[arg-type]
