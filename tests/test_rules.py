#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
tests.test_rules
------------------------------------------------------------
Description :
    Tests unitaires (pytest) — APP1 QRA — règles déterministes.

Objectifs :
    - Vérifier détection ambiguïté (modal faible / terme ambigu)
    - Vérifier testabilité (absence VM + AC)
    - Vérifier qualité AC (trop court / terme ambigu)
    - Vérifier scope/safety
    - Vérifier score (0..100) et status=CHECKED

Usage :
    pytest -q
============================================================
"""

from __future__ import annotations

from typing import List

import pytest

from vv_app1_qra.models import IssueSeverity, Requirement, SuggestionSource
from vv_app1_qra.rules import analyze_requirement, compute_score


# ============================================================
# 🔧 Helpers
# ============================================================
def _issue_ids(result) -> List[str]:
    return [i.rule_id for i in result.issues]


def _issues_by_rule(result, rule_id: str):
    return [i for i in result.issues if i.rule_id == rule_id]


# ============================================================
# 🧪 Tests
# ============================================================
def test_rule_tst_001_not_testable_when_no_vm_and_no_ac():
    r = Requirement(
        req_id="REQ-001",
        title="Login",
        text="The system shall authenticate users.",
        verification_method="",
        acceptance_criteria="",
    )
    res = analyze_requirement(r)

    assert res.status == "CHECKED"
    assert "TST-001" in _issue_ids(res)

    issue = _issues_by_rule(res, "TST-001")[0]
    assert issue.severity == IssueSeverity.MAJOR
    assert issue.category == "TESTABILITY"
    assert issue.field in ("verification_method", "")

    # Suggestions RULE présentes et non décisionnelles
    assert len(res.suggestions) >= 1
    assert all(s.source == SuggestionSource.RULE for s in res.suggestions)


def test_rule_tst_002_acceptance_criteria_missing_only():
    r = Requirement(
        req_id="REQ-002",
        title="Timeout",
        text="The system shall timeout after inactivity.",
        verification_method="Test",
        acceptance_criteria="",
    )
    res = analyze_requirement(r)

    assert "TST-002" in _issue_ids(res)
    issue = _issues_by_rule(res, "TST-002")[0]
    assert issue.severity == IssueSeverity.MINOR


def test_rule_amb_001_detects_weak_modal():
    r = Requirement(
        req_id="REQ-003",
        title="Performance",
        text="The system should be fast and user-friendly.",
        verification_method="Test",
        acceptance_criteria="Response time < 200 ms for 95% of requests.",
    )
    res = analyze_requirement(r)

    assert "AMB-001" in _issue_ids(res)
    issue = _issues_by_rule(res, "AMB-001")[0]
    assert issue.severity == IssueSeverity.MINOR
    assert "should" in issue.message.lower()


def test_rule_amb_002_detects_ambiguous_term():
    r = Requirement(
        req_id="REQ-004",
        title="UI",
        text="The UI shall be intuitive and robust.",
        verification_method="Inspection",
        acceptance_criteria="UI passes checklist v1.",
    )
    res = analyze_requirement(r)

    assert "AMB-002" in _issue_ids(res)
    issue = _issues_by_rule(res, "AMB-002")[0]
    assert issue.severity == IssueSeverity.MINOR


def test_rule_ac_001_detects_too_short_ac():
    """
    AC-001 : AC trop courte => MINOR (contrat attendu par la suite de tests).
    """
    r = Requirement(
        req_id="REQ-005",
        title="Export",
        text="The system shall export a report.",
        verification_method="Test",
        acceptance_criteria="Works.",
    )
    res = analyze_requirement(r)

    assert "AC-001" in _issue_ids(res)
    issue = _issues_by_rule(res, "AC-001")[0]
    assert issue.severity == IssueSeverity.MINOR
    assert issue.field == "acceptance_criteria"


def test_rule_ac_002_detects_ambiguous_term_in_ac():
    r = Requirement(
        req_id="REQ-006",
        title="Security",
        text="The system shall log access attempts.",
        verification_method="Test",
        acceptance_criteria="Logging is secure and adequate.",
    )
    res = analyze_requirement(r)

    assert "AC-002" in _issue_ids(res)
    issue = _issues_by_rule(res, "AC-002")[0]
    assert issue.severity == IssueSeverity.INFO


def test_score_computation_clamped_0_100():
    r = Requirement(
        req_id="REQ-007",
        title="Bad req",
        text="The system should be fast, robust, and user-friendly.",
        verification_method="",
        acceptance_criteria="",
    )
    res = analyze_requirement(r)

    assert isinstance(res.score, int)
    assert 0 <= res.score <= 100
    assert res.score == compute_score(res.issues)


def test_no_issues_for_good_requirement():
    r = Requirement(
        req_id="REQ-008",
        title="Response time",
        text="The system shall respond within 200 ms for 95% of requests under nominal load.",
        verification_method="Test",
        acceptance_criteria="Given nominal load, when sending 1000 requests, then 95% have latency <= 200 ms.",
    )
    res = analyze_requirement(r)

    assert res.status == "CHECKED"
    assert res.issues == []
    assert res.suggestions == []
    assert res.score == 100


def test_rule_amb_002_flags_high_accuracy_and_normal_operation():
    r = Requirement(
        req_id="REQ-009",
        title="Nav accuracy",
        text="The navigation solution shall have high accuracy during normal operation.",
        verification_method="Analysis",
        acceptance_criteria="",
    )
    res = analyze_requirement(r)

    assert "AMB-002" in _issue_ids(res)
    assert res.score < 100
    assert all(s.source == SuggestionSource.RULE for s in res.suggestions)


def test_rule_amb_002_flags_reliably():
    r = Requirement(
        req_id="REQ-014",
        title="DTC reliability",
        text="The ECU shall store DTCs reliably.",
        verification_method="Test",
        acceptance_criteria="Verify DTC persistence after reboot.",
    )
    res = analyze_requirement(r)

    assert "AMB-002" in _issue_ids(res)
    assert res.score < 100


def test_rule_scp_001_flags_all_conditions_scope():
    r = Requirement(
        req_id="REQ-010",
        title="Comms latency all conditions",
        text="The onboard unit shall exchange messages with wayside within 200 ms in all conditions.",
        verification_method="Test",
        acceptance_criteria="Latency <= 200 ms in all conditions.",
    )
    res = analyze_requirement(r)

    assert "SCP-001" in _issue_ids(res)
    issue = _issues_by_rule(res, "SCP-001")[0]
    assert issue.severity == IssueSeverity.MINOR


def test_rule_saf_001_flags_shall_be_safe_as_info():
    r = Requirement(
        req_id="REQ-019",
        title="Safety",
        text="The system shall be safe.",
        verification_method="Analysis",
        acceptance_criteria="",
    )
    res = analyze_requirement(r)

    assert "SAF-001" in _issue_ids(res)
    issue = _issues_by_rule(res, "SAF-001")[0]
    assert issue.severity == IssueSeverity.INFO
