#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
vv_app1_qra.rules
------------------------------------------------------------
Description :
    Règles déterministes de qualité d’exigences (APP1 — QRA).

Rôle :
    - Analyser une Requirement via règles simples
    - Produire des défauts (Issue) + suggestions (Suggestion source=RULE)
    - Calculer un score 0..100 + statut CHECKED

Contraintes :
    - 100% déterministe (stdlib only)
    - Pas d’IA ici
============================================================
"""

from __future__ import annotations

# ============================================================
# 📦 Imports
# ============================================================
import logging
import re
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from vv_app1_qra.models import (
    AnalysisResult,
    Issue,
    IssueSeverity,
    Requirement,
    Suggestion,
    SuggestionSource,
)

# ============================================================
# 🔎 Public exports
# ============================================================
__all__ = [
    "AMBIGUOUS_TERMS",
    "WEAK_MODAL_VERBS",
    "SEVERITY_PENALTY",
    "ModuleError",
    "RuleHit",
    "compute_score",
    "analyze_requirement",
    "analyze_requirements",
    "get_logger",
]

# ============================================================
# 🧾 Logging (local, autonome)
# ============================================================
def get_logger(name: str) -> logging.Logger:
    """Crée un logger simple et stable (stdout), sans dépendance externe."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


log = get_logger(__name__)


# ============================================================
# ⚠️ Exceptions spécifiques au module
# ============================================================
class ModuleError(Exception):
    """Erreur spécifique au module (erreur métier ou technique encapsulée)."""


# ============================================================
# 🧩 Config règles (MVP)
# ============================================================
AMBIGUOUS_TERMS: Tuple[str, ...] = (
    "user-friendly",
    "intuitive",
    "fast",
    "quick",
    "efficient",
    "robust",
    "reliable",
    "secure",
    "as appropriate",
    "if necessary",
    "if needed",
    "as needed",
    "etc",
    "sufficient",
    "adequate",
    "optimize",
    "minimize",
    "maximize",
    "high accuracy",
    "normal operation",
    "reliably",
    "low jitter",
)

WEAK_MODAL_VERBS: Tuple[str, ...] = (
    "should",
    "may",
    "might",
    "could",
)

SEVERITY_PENALTY = {
    IssueSeverity.INFO: 5,
    IssueSeverity.MINOR: 10,
    IssueSeverity.MAJOR: 25,
    IssueSeverity.CRITICAL: 40,
}


@dataclass(frozen=True)
class RuleHit:
    rule_id: str
    category: str
    severity: IssueSeverity
    message: str
    field: str = ""
    evidence: str = ""
    recommendation: str = ""


# ============================================================
# 🔧 Helpers
# ============================================================
def _norm(s: str) -> str:
    return (s or "").strip()


def _compact_ws(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def _find_terms(text: str, terms: Sequence[str]) -> List[str]:
    """Retourne la liste des termes trouvés (dédupliqués) dans text (case-insensitive)."""
    hay = (text or "").lower()
    found: List[str] = []
    for t in terms:
        if t.lower() in hay:
            found.append(t)

    # dédup stable
    out: List[str] = []
    for x in found:
        if x not in out:
            out.append(x)
    return out


def _first_excerpt(text: str, needle: str, radius: int = 45) -> str:
    """Construit un extrait court autour du premier match."""
    t = text or ""
    low = t.lower()
    n = (needle or "").lower()
    i = low.find(n)
    if i < 0:
        return _compact_ws(t)[: max(0, radius * 2)]
    start = max(0, i - radius)
    end = min(len(t), i + len(needle) + radius)
    return _compact_ws(t[start:end])


def _mk_issue(hit: RuleHit) -> Issue:
    return Issue(
        rule_id=hit.rule_id,
        category=hit.category,
        severity=hit.severity,
        message=hit.message,
        field=hit.field,
        evidence=hit.evidence,
        recommendation=hit.recommendation,
    )


def _mk_suggestion_from_issue(issue: Issue) -> Suggestion:
    """Suggestion RULE directement dérivée de l’issue."""
    rec = _norm(issue.recommendation)
    if not rec:
        rec = "Clarifier l’exigence et ajouter des critères d’acceptation mesurables."
    return Suggestion(
        source=SuggestionSource.RULE,
        message=rec,
        rule_id=issue.rule_id,
        rationale=_norm(issue.message),
        confidence=None,
    )


# ============================================================
# 🧠 Règles (MVP)
# ============================================================
def _rule_ambiguity(req: Requirement) -> Iterable[RuleHit]:
    """Détecte termes ambigus (qualitatifs non mesurables) et modaux faibles."""
    text_blob = " ".join([req.title, req.text, req.acceptance_criteria])
    text_blob = _compact_ws(text_blob)

    hits: List[RuleHit] = []

    found_weak = _find_terms(text_blob, WEAK_MODAL_VERBS)
    if found_weak:
        w = found_weak[0]
        hits.append(
            RuleHit(
                rule_id="AMB-001",
                category="AMBIGUITY",
                severity=IssueSeverity.MINOR,
                message=f"Modal verb '{w}' detected (weak commitment). Prefer 'shall' or measurable phrasing.",
                field="text",
                evidence=_first_excerpt(text_blob, w),
                recommendation="Remplacer les modaux faibles (should/may/…) par une formulation normative mesurable (shall + métriques).",
            )
        )

    found_terms = _find_terms(text_blob, AMBIGUOUS_TERMS)
    if found_terms:
        t = found_terms[0]
        hits.append(
            RuleHit(
                rule_id="AMB-002",
                category="AMBIGUITY",
                severity=IssueSeverity.MINOR,
                message=f"Ambiguous term '{t}' detected (not measurable).",
                field="text",
                evidence=_first_excerpt(text_blob, t),
                recommendation="Remplacer les termes qualitatifs par des critères quantifiés (temps, taux, seuils, tolérances).",
            )
        )

    return hits


def _rule_testability(req: Requirement) -> Iterable[RuleHit]:
    """Testabilité : besoin d’un 'verification_method' et/ou 'acceptance_criteria'."""
    vm = _norm(req.verification_method)
    ac = _norm(req.acceptance_criteria)

    if not vm and not ac:
        return [
            RuleHit(
                rule_id="TST-001",
                category="TESTABILITY",
                severity=IssueSeverity.MAJOR,
                message="No verification method and no acceptance criteria provided (requirement not testable).",
                field="verification_method",
                evidence="verification_method='', acceptance_criteria=''",
                recommendation="Ajouter une méthode de vérification (Test/Analyse/Inspection/Démonstration) et des critères d’acceptation.",
            )
        ]

    if not ac:
        return [
            RuleHit(
                rule_id="TST-002",
                category="TESTABILITY",
                severity=IssueSeverity.MINOR,
                message="Acceptance criteria missing (verification might be unclear).",
                field="acceptance_criteria",
                evidence="acceptance_criteria=''",
                recommendation="Ajouter des critères d’acceptation concrets (Given/When/Then, seuils, tolérances).",
            )
        ]

    return []


def _rule_acceptance_criteria(req: Requirement) -> Iterable[RuleHit]:
    """Vérifie la qualité des AC : présence, longueur minimale, absence de termes ambigus."""
    ac = _compact_ws(req.acceptance_criteria)
    if not ac:
        return []

    hits: List[RuleHit] = []

    if len(ac) < 15:
        hits.append(
            RuleHit(
                rule_id="AC-001",
                category="ACCEPTANCE_CRITERIA",
                severity=IssueSeverity.MINOR,
                message="Acceptance criteria is too short; likely not actionable/measurable.",
                field="acceptance_criteria",
                evidence=ac,
                recommendation="Rédiger des critères d’acceptation vérifiables (ex: seuils, étapes, résultats attendus).",
            )
        )

    found_terms = _find_terms(ac, AMBIGUOUS_TERMS)
    if found_terms:
        t = found_terms[0]
        hits.append(
            RuleHit(
                rule_id="AC-002",
                category="ACCEPTANCE_CRITERIA",
                severity=IssueSeverity.INFO,
                message=f"Ambiguous term '{t}' in acceptance criteria.",
                field="acceptance_criteria",
                evidence=_first_excerpt(ac, t),
                recommendation="Rendre les critères d’acceptation mesurables (chiffres, seuils, tolérances, délais).",
            )
        )

    return hits


# ============================================================
# 🧮 Scoring + Orchestration
# ============================================================
def compute_score(issues: Sequence[Issue], base: int = 100) -> int:
    """
    Score simple :
      100 - somme(pénalités par sévérité), clamp [0..100]
    """
    score = int(base)
    for i in issues:
        score -= int(SEVERITY_PENALTY.get(i.severity, 0))
    return max(0, min(100, score))


def analyze_requirement(req: Requirement, *, verbose: bool = False) -> AnalysisResult:
    """
    Analyse une exigence via règles déterministes et retourne un AnalysisResult.

    Raises:
        ModuleError: si entrée invalide
    """
    try:
        if not isinstance(req, Requirement):
            raise ModuleError("Invalid input: 'req' must be a Requirement.")

        if verbose:
            log.setLevel(logging.DEBUG)

        hits: List[RuleHit] = []
        hits.extend(list(_rule_ambiguity(req)))
        hits.extend(list(_rule_testability(req)))
        hits.extend(list(_rule_acceptance_criteria(req)))

        issues = [_mk_issue(h) for h in hits]
        suggestions = [_mk_suggestion_from_issue(i) for i in issues]

        score = compute_score(issues)
        return AnalysisResult(
            requirement=req,
            issues=issues,
            suggestions=suggestions,
            score=score,
            status="CHECKED",
        )

    except ModuleError:
        raise
    except Exception as e:
        log.exception("Erreur inattendue dans analyze_requirement()")
        raise ModuleError(str(e)) from e


def analyze_requirements(reqs: Sequence[Requirement], *, verbose: bool = False) -> List[AnalysisResult]:
    """Analyse batch (liste d’exigences)."""
    return [analyze_requirement(r, verbose=verbose) for r in reqs]
