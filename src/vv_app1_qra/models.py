#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
vv_app1_qra.models
------------------------------------------------------------
Description :
    Modèles de domaine pour APP1 — QRA (Quality Risk Assessment).

Rôle :
    - Définir les structures de données stables utilisées par :
        * rules.py : Issue / AnalysisResult
        * ia_assistant.py : Suggestion (source=AI)
        * report.py : rendu HTML/CSV
    - Fournir une sérialisation simple (to_dict / from_dict) pour :
        * outputs
        * logs
        * tests

Contraintes :
    - stdlib only
    - modèles "data-only" (pas de logique métier de règles ici)
============================================================
"""

from __future__ import annotations

# ============================================================
# 📦 Imports
# ============================================================
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

# ============================================================
# 🔎 Public exports
# ============================================================
__all__ = [
    "IssueSeverity",
    "SuggestionSource",
    "Requirement",
    "Issue",
    "Suggestion",
    "AnalysisResult",
]

# ============================================================
# 🧱 Enums
# ============================================================
class IssueSeverity(str, Enum):
    """Niveau de sévérité (V&V/QA) pour classifier un défaut."""
    INFO = "INFO"
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"


class SuggestionSource(str, Enum):
    """Origine d'une suggestion (assistant = propose, humain = décide)."""
    RULE = "RULE"
    AI = "AI"
    HUMAN = "HUMAN"


# ============================================================
# 🔧 Helpers (validation / mapping)
# ============================================================
def _s(v: Any) -> str:
    """Convertit en str et trim (robuste pour None)."""
    return ("" if v is None else str(v)).strip()


def _enum_from_str(enum_cls: type[Enum], raw: Any, field_name: str) -> Enum:
    """
    Convertit un champ texte en Enum (strict).

    Accepte :
      - instance Enum
      - chaîne égalant une valeur (ex: "MAJOR")
      - chaîne égalant le nom (ex: "MAJOR")
    """
    if isinstance(raw, enum_cls):
        return raw

    s = _s(raw)
    if not s:
        raise ValueError(f"{field_name} is required (got empty).")

    # match valeur
    try:
        return enum_cls(s)  # type: ignore[misc]
    except Exception:
        pass

    # match nom
    try:
        return enum_cls[s]  # type: ignore[index]
    except Exception as e:
        allowed = ", ".join([m.value for m in enum_cls])  # type: ignore[attr-defined]
        raise ValueError(f"Invalid {field_name}='{s}'. Allowed: {allowed}") from e


# ============================================================
# 🧩 Modèles
# ============================================================
@dataclass(frozen=True)
class Requirement:
    """Exigence d'entrée (proche DOORS/Polarion), normalisée."""
    req_id: str
    title: str
    text: str
    source: str = "demo"

    system: str = ""
    component: str = ""
    priority: str = ""
    rationale: str = ""
    verification_method: str = ""
    acceptance_criteria: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "req_id", _s(self.req_id))
        object.__setattr__(self, "title", _s(self.title))
        object.__setattr__(self, "text", _s(self.text))
        object.__setattr__(self, "source", _s(self.source) or "demo")

        object.__setattr__(self, "system", _s(self.system))
        object.__setattr__(self, "component", _s(self.component))
        object.__setattr__(self, "priority", _s(self.priority))
        object.__setattr__(self, "rationale", _s(self.rationale))
        object.__setattr__(self, "verification_method", _s(self.verification_method))
        object.__setattr__(self, "acceptance_criteria", _s(self.acceptance_criteria))

        if not self.req_id:
            raise ValueError("Requirement.req_id must be non-empty.")
        if not (self.title or self.text):
            raise ValueError("Requirement must have at least title or text.")

        if self.meta is None:
            object.__setattr__(self, "meta", {})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "req_id": self.req_id,
            "title": self.title,
            "text": self.text,
            "source": self.source,
            "system": self.system,
            "component": self.component,
            "priority": self.priority,
            "rationale": self.rationale,
            "verification_method": self.verification_method,
            "acceptance_criteria": self.acceptance_criteria,
            "meta": dict(self.meta or {}),
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Requirement":
        if not isinstance(d, dict):
            raise ValueError("Requirement.from_dict expects a dict.")
        return Requirement(
            req_id=d.get("req_id", ""),
            title=d.get("title", ""),
            text=d.get("text", ""),
            source=d.get("source", "demo"),
            system=d.get("system", ""),
            component=d.get("component", ""),
            priority=d.get("priority", ""),
            rationale=d.get("rationale", ""),
            verification_method=d.get("verification_method", ""),
            acceptance_criteria=d.get("acceptance_criteria", ""),
            meta=d.get("meta", {}) or {},
        )


@dataclass(frozen=True)
class Issue:
    """Défaut détecté par règle déterministe."""
    rule_id: str
    category: str
    severity: IssueSeverity
    message: str
    field: str = ""
    evidence: str = ""
    recommendation: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "rule_id", _s(self.rule_id))
        object.__setattr__(self, "category", _s(self.category))
        object.__setattr__(self, "message", _s(self.message))
        object.__setattr__(self, "field", _s(self.field))
        object.__setattr__(self, "evidence", _s(self.evidence))
        object.__setattr__(self, "recommendation", _s(self.recommendation))

        if not self.rule_id:
            raise ValueError("Issue.rule_id must be non-empty.")
        if not self.category:
            raise ValueError("Issue.category must be non-empty.")
        if not self.message:
            raise ValueError("Issue.message must be non-empty.")

        sev = _enum_from_str(IssueSeverity, self.severity, "Issue.severity")
        object.__setattr__(self, "severity", sev)  # type: ignore[arg-type]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "category": self.category,
            "severity": self.severity.value,
            "message": self.message,
            "field": self.field,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Issue":
        if not isinstance(d, dict):
            raise ValueError("Issue.from_dict expects a dict.")
        sev = _enum_from_str(IssueSeverity, d.get("severity"), "Issue.severity")
        return Issue(
            rule_id=d.get("rule_id", ""),
            category=d.get("category", ""),
            severity=sev,  # type: ignore[arg-type]
            message=d.get("message", ""),
            field=d.get("field", ""),
            evidence=d.get("evidence", ""),
            recommendation=d.get("recommendation", ""),
        )


@dataclass(frozen=True)
class Suggestion:
    """Suggestion (RULE/AI/HUMAN). Non décisionnelle par design."""
    source: SuggestionSource
    message: str
    rule_id: str = ""
    rationale: str = ""
    confidence: Optional[float] = None

    def __post_init__(self) -> None:
        src = _enum_from_str(SuggestionSource, self.source, "Suggestion.source")
        object.__setattr__(self, "source", src)  # type: ignore[arg-type]

        object.__setattr__(self, "message", _s(self.message))
        object.__setattr__(self, "rule_id", _s(self.rule_id))
        object.__setattr__(self, "rationale", _s(self.rationale))

        if not self.message:
            raise ValueError("Suggestion.message must be non-empty.")

        if self.confidence is not None:
            if not isinstance(self.confidence, (int, float)):
                raise ValueError("Suggestion.confidence must be a number (float) or None.")
            if float(self.confidence) < 0.0 or float(self.confidence) > 1.0:
                raise ValueError("Suggestion.confidence must be in [0.0, 1.0].")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source.value,
            "message": self.message,
            "rule_id": self.rule_id,
            "rationale": self.rationale,
            "confidence": self.confidence,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Suggestion":
        if not isinstance(d, dict):
            raise ValueError("Suggestion.from_dict expects a dict.")
        src = _enum_from_str(SuggestionSource, d.get("source"), "Suggestion.source")
        return Suggestion(
            source=src,  # type: ignore[arg-type]
            message=d.get("message", ""),
            rule_id=d.get("rule_id", ""),
            rationale=d.get("rationale", ""),
            confidence=d.get("confidence", None),
        )


@dataclass(frozen=True)
class AnalysisResult:
    """
    Résultat d'analyse pour une exigence :
    - issues = défauts détectés par règles
    - suggestions = propositions (règles/IA/humain)
    - score/status optionnels
    """
    requirement: Requirement
    issues: List[Issue] = field(default_factory=list)
    suggestions: List[Suggestion] = field(default_factory=list)
    score: Optional[int] = None
    status: str = "LOADED"

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", _s(self.status) or "LOADED")

        if self.score is not None:
            if not isinstance(self.score, int):
                raise ValueError("AnalysisResult.score must be int or None.")
            if self.score < 0 or self.score > 100:
                raise ValueError("AnalysisResult.score must be in [0..100].")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement": self.requirement.to_dict(),
            "issues": [i.to_dict() for i in self.issues],
            "suggestions": [s.to_dict() for s in self.suggestions],
            "score": self.score,
            "status": self.status,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AnalysisResult":
        if not isinstance(d, dict):
            raise ValueError("AnalysisResult.from_dict expects a dict.")
        req = Requirement.from_dict(d.get("requirement", {}) or {})
        issues = [Issue.from_dict(x) for x in (d.get("issues", []) or [])]
        suggs = [Suggestion.from_dict(x) for x in (d.get("suggestions", []) or [])]
        return AnalysisResult(
            requirement=req,
            issues=issues,
            suggestions=suggs,
            score=d.get("score", None),
            status=d.get("status", "LOADED"),
        )
