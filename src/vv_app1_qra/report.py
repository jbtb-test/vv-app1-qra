"""
============================================================
report.py
------------------------------------------------------------
Génération du rapport HTML QRA (APP1)

- HTML statique ouvrable localement
- Vue synthèse + détails par exigence
- Suggestions RULES (déterministes) vs IA (LLM) selon le mode
============================================================
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Any, Dict

import csv
import logging
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

log = logging.getLogger(__name__)


def _resolve_template_dir() -> Path:
    base_dir = Path(__file__).resolve().parents[2]  # repo root
    template_dir = base_dir / "templates" / "qra"
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")
    return template_dir


def _compute_ai_enabled() -> bool:
    """
    Détermine si l'IA doit être considérée active pour le rendu.

    Règle :
      - ENABLE_AI doit être truthy (1/true/yes/on)
      - OPENAI_API_KEY doit être présent
    """
    enable_ai = (os.getenv("ENABLE_AI") or "").strip().lower()
    key = (os.getenv("OPENAI_API_KEY") or "").strip()
    return enable_ai in {"1", "true", "yes", "on"} and bool(key)


def generate_html_report(qra_result: dict, output_path: Path, *, verbose: bool = False) -> Path:
    """
    Génère le rapport HTML QRA.

    Parameters
    ----------
    qra_result : dict
        Résultat structuré du pipeline QRA.
    output_path : Path
        Chemin du fichier HTML de sortie.
    verbose : bool
        Mode verbeux.

    Returns
    -------
    Path
        Chemin du fichier HTML généré.
    """
    template_dir = _resolve_template_dir()

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html"]),
    )

    template = env.get_template("report_qra.html")

    requirements = qra_result["requirements"]
    global_score = qra_result["global_score"]
    global_status = qra_result["global_status"]

    ai_enabled = _compute_ai_enabled()
    suggestions_label = "IA" if ai_enabled else "RULES"

    html = template.render(
        title="Quality Risk Assessment — Rapport",
        header="Quality Risk Assessment — Outil V&V",
        subtitle=f"Mode suggestions : {suggestions_label}",
        badge=datetime.now().strftime("%Y-%m-%d %H:%M"),
        global_score=global_score,
        global_status=global_status,
        requirements=requirements,
        ai_enabled=ai_enabled,
        suggestions_label=suggestions_label,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    if verbose:
        log.info("[REPORT] HTML generated: %s", output_path)

    return output_path


def generate_csv_report(qra_result: Dict[str, Any], output_path: Path, *, verbose: bool = False) -> Path:
    rows = qra_result.get("requirements", []) or []

    fieldnames = [
        "id",
        "score",
        "raw_status",
        "display_status",
        "text",
        "issues_count",
        "suggestions_label",
        "suggestions_count",
    ]

    ai_enabled = _compute_ai_enabled()
    suggestions_label = "IA" if ai_enabled else "RULES"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            issues = r.get("issues", []) or []
            sugs = r.get("ai_suggestions", []) or []  # (nom historique côté pipeline)

            w.writerow(
                {
                    "id": r.get("id", ""),
                    "score": r.get("score", ""),
                    "raw_status": r.get("raw_status", ""),
                    "display_status": r.get("display_status", ""),
                    "text": r.get("text", ""),
                    "issues_count": len(issues),
                    "suggestions_label": suggestions_label,
                    "suggestions_count": len(sugs),
                }
            )

    if verbose:
        log.info("[REPORT] CSV generated: %s", output_path)

    return output_path
