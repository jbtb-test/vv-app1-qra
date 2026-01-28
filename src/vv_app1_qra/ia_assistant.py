#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
vv_app1_qra.ia_assistant
------------------------------------------------------------
Description :
    Module IA (OpenAI) encapsulé pour suggestions d’amélioration
    (APP1 — QRA) — IA "suggestion-only" et non bloquante.

Rôle :
    - Aucune dépendance IA obligatoire pour faire tourner l’app
    - IA activable via ENABLE_AI=1 (env var) + OPENAI_API_KEY présent
    - Fallback systématique : aucune exception propagée vers le pipeline

Variables d'environnement :
    - ENABLE_AI         : 0/1 (default: 0)
    - OPENAI_API_KEY    : clé API (si absent -> IA désactivée)
    - OPENAI_MODEL      : modèle (default: gpt-5) [ajustable]

Usage :
    - Appel depuis vv_app1_qra.main via suggest_improvements()

Notes :
    - Sortie attendue strictement JSON (contrat interne).
    - Si JSON invalide / SDK absent / appel échoue => fallback [].
============================================================
"""

from __future__ import annotations

# ============================================================
# 📦 Imports
# ============================================================
import json
import logging
import os
from typing import List, Optional, Sequence

from vv_app1_qra.models import Issue, Requirement, Suggestion, SuggestionSource

# ============================================================
# 🧾 Logging (local, autonome)
# ============================================================
def get_logger(name: str) -> logging.Logger:
    """
    Crée un logger simple et stable (stdout), sans dépendance externe.
    """
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
    """Erreur spécifique au module ia_assistant."""


# ============================================================
# 🔧 Config / Helpers
# ============================================================
def _truthy(value: str | None) -> bool:
    v = (value or "").strip().lower()
    return v in {"1", "true", "yes", "y", "on"}


def is_ai_enabled() -> bool:
    """
    IA activée seulement si ENABLE_AI est truthy ET OPENAI_API_KEY présent.
    """
    if not _truthy(os.getenv("ENABLE_AI", "0")):
        return False
    if not (os.getenv("OPENAI_API_KEY") or "").strip():
        return False
    return True


def _get_model() -> str:
    """
    Modèle par défaut. Ajustable via OPENAI_MODEL.
    """
    return (os.getenv("OPENAI_MODEL") or "gpt-5").strip()


def _build_prompt(req: Requirement, issues: Sequence[Issue], max_suggestions: int) -> str:
    """
    Prompt orienté V&V : suggestions concrètes, testables, mesurables.
    Réponse attendue STRICTEMENT en JSON.
    """
    issues_lines = "\n".join(
        f"- {i.rule_id} [{i.severity.value}] {i.category}: {i.message}"
        for i in issues
    ) or "- (none)"

    return f"""
You are a senior V&V / Requirements Engineering assistant.

TASK:
Given a requirement and detected quality issues, propose up to {max_suggestions} improved requirement formulations
and/or acceptance criteria suggestions.

RULES:
- Suggestions must be measurable and testable.
- Avoid vague terms (e.g. fast, robust, if needed, as appropriate).
- Keep each suggestion short and actionable.
- Output MUST be valid JSON ONLY (no markdown, no prose).

INPUT REQUIREMENT (fields):
req_id: {req.req_id}
title: {req.title}
text: {req.text}
verification_method: {req.verification_method}
acceptance_criteria: {req.acceptance_criteria}

DETECTED ISSUES:
{issues_lines}

OUTPUT JSON SCHEMA:
{{
  "suggestions": [
    {{
      "message": "string",
      "rationale": "string",
      "confidence": 0.0
    }}
  ]
}}
""".strip()


def _safe_parse_json(text: str) -> dict:
    """
    Parse JSON robuste : lève ModuleError si invalide.
    """
    try:
        return json.loads(text)
    except Exception as e:
        raise ModuleError(f"Invalid JSON from AI: {e}") from e


# ============================================================
# 🤖 API principale
# ============================================================
def suggest_improvements(
    req: Requirement,
    issues: Sequence[Issue],
    *,
    max_suggestions: int = 3,
    model: Optional[str] = None,
    verbose: bool = False,
) -> List[Suggestion]:
    """
    Retourne une liste de Suggestion (source=AI), ou [] si IA désactivée/indisponible.

    Contrats :
      - Non bloquant : aucune exception ne remonte
      - Suggestion-only : ne modifie jamais l'exigence
    """
    if verbose:
        log.setLevel(logging.DEBUG)

    if not is_ai_enabled():
        enable_ai_env = (os.getenv("ENABLE_AI", "0") or "").strip().lower()
        has_key = bool((os.getenv("OPENAI_API_KEY") or "").strip())
        if enable_ai_env in {"1", "true", "yes", "on"} and not has_key:
            log.warning("AI requested (ENABLE_AI=1) but OPENAI_API_KEY missing -> fallback []")
        else:
            log.debug("AI disabled -> fallback []")
        return []

    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        log.warning("openai-python not installed -> fallback []")
        return []

    used_model = (model or _get_model()).strip()
    prompt = _build_prompt(req, issues, max_suggestions=max_suggestions)

    try:
        client = OpenAI()
        resp = client.responses.create(model=used_model, input=prompt)

        output_text = (getattr(resp, "output_text", None) or "").strip()
        if not output_text:
            output_text = str(resp).strip()

        try:
            data = _safe_parse_json(output_text)
        except Exception as e:
            log.warning(f"AI returned invalid JSON -> fallback [] ({e})")
            return []

        raw = data.get("suggestions", [])
        if not isinstance(raw, list):
            log.warning("AI JSON invalid: 'suggestions' is not a list -> fallback []")
            return []

        out: List[Suggestion] = []
        for item in raw[:max_suggestions]:
            if not isinstance(item, dict):
                continue
            msg = (item.get("message") or "").strip()
            if not msg:
                continue
            rationale = (item.get("rationale") or "").strip()
            conf = item.get("confidence", None)

            out.append(
                Suggestion(
                    source=SuggestionSource.AI,
                    message=msg,
                    rule_id="AI-001",
                    rationale=rationale,
                    confidence=conf if isinstance(conf, (int, float)) else None,
                )
            )

        return out

    except Exception as e:
        log.warning(f"AI call failed -> fallback [] ({e})")
        return []
