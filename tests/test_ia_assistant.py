#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
tests.test_ia_assistant
------------------------------------------------------------
Description :
    Tests unitaires — APP1 QRA — module IA (suggestion-only).

Objectifs :
    - ENABLE_AI absent/0 => IA désactivée
    - ENABLE_AI=1 sans clé => fallback [] (non bloquant)
    - ENABLE_AI=1 avec clé => is_ai_enabled True

Usage :
    pytest -q
============================================================
"""

from __future__ import annotations

from vv_app1_qra.ia_assistant import is_ai_enabled, suggest_improvements
from vv_app1_qra.models import Issue, IssueSeverity, Requirement


def test_is_ai_enabled_false_by_default(monkeypatch):
    monkeypatch.delenv("ENABLE_AI", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert is_ai_enabled() is False


def test_suggest_improvements_disabled_returns_empty(monkeypatch):
    monkeypatch.setenv("ENABLE_AI", "0")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    req = Requirement(req_id="REQ-1", title="t", text="The system should be fast.")
    issues = [
        Issue(
            rule_id="AMB-001",
            category="AMBIGUITY",
            severity=IssueSeverity.MINOR,
            message="should used",
        )
    ]

    out = suggest_improvements(req, issues)
    assert out == []


def test_suggest_improvements_enabled_without_key_fallback(monkeypatch):
    monkeypatch.setenv("ENABLE_AI", "1")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    req = Requirement(req_id="REQ-1", title="t", text="The system should be fast.")
    out = suggest_improvements(req, [])
    assert out == []


def test_is_ai_enabled_requires_key(monkeypatch):
    monkeypatch.setenv("ENABLE_AI", "1")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert is_ai_enabled() is False

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    assert is_ai_enabled() is True
