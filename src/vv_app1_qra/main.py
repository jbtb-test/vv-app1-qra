#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
vv_app1_qra.main
------------------------------------------------------------
Description :
    APP1 — QRA (Quality Risk Assessment)
    CLI : lecture CSV exigences, règles déterministes, suggestions IA optionnelles,
    génération d’outputs (legacy + rapports structurés).

Rôle :
    - Pipeline V&V déterministe prioritaire
    - IA "suggestion-only" : non bloquante, fallback systématique
    - Outputs :
        * legacy timestamped CSV/HTML (compat historique)
        * rapports stables qra_report.html + qra_report.csv

Architecture (repo) :
    - Code : src/vv_app1_qra/
    - Tests : tests/
    - Données : data/
    - Docs : docs/
    - Templates : templates/qra/

Usage CLI :
    python -m vv_app1_qra.main --out-dir data/outputs --verbose
    python -m vv_app1_qra.main --input data/inputs/demo_input.csv --out-dir data/outputs
    python -m vv_app1_qra.main --fail-on-empty

Mode IA (standard portfolio) :
    . .\\tools\\load_env_secret.ps1
    $env:ENABLE_AI="1"
    python -m vv_app1_qra.main --out-dir data/outputs --verbose

Notes :
    - Si ENABLE_AI=1 sans OPENAI_API_KEY => fallback [] (log warning)
============================================================
"""

from __future__ import annotations

# ============================================================
# 📦 Imports
# ============================================================
import argparse
import csv
import datetime as dt
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from vv_app1_qra.ia_assistant import suggest_improvements
from vv_app1_qra.models import AnalysisResult, Requirement, SuggestionSource
from vv_app1_qra.report import generate_csv_report, generate_html_report
from vv_app1_qra.rules import analyze_requirement

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
    """Erreur spécifique au module (erreur métier ou technique encapsulée)."""


# ============================================================
# 🧩 Modèle de données (optionnel)
# ============================================================
@dataclass
class ProcessResult:
    """
    Structure de sortie standardisée pour le run CLI.
    """
    ok: bool
    payload: Dict[str, Any]
    message: Optional[str] = None


# ============================================================
# 🔧 Fonctions utilitaires (CSV mapping)
# ============================================================
def _normalize_header(s: str) -> str:
    return (s or "").strip().lower()


def _pick_first(row: Dict[str, str], keys: List[str], default: str = "") -> str:
    for k in keys:
        v = (row.get(k) or "").strip()
        if v:
            return v
    return default


def load_requirements_csv(input_path: Path) -> List[Dict[str, str]]:
    """
    Charge des exigences depuis un CSV.

    Supporte plusieurs schémas (tolérant).

    Schéma "demo_input.csv" (APP1) :
      - req_id
      - system
      - component
      - priority
      - source
      - requirement_text
      - rationale
      - verification_method
      - acceptance_criteria

    Compatibilité legacy :
      - id/requirement_id
      - text/requirement/description/content
      - title/summary
    """
    if not input_path.exists():
        raise ModuleError(f"Input file not found: {input_path}")

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ModuleError("CSV has no header row (fieldnames missing).")

        rows: List[Dict[str, str]] = []
        idx = 0

        for raw in reader:
            idx += 1
            norm = {_normalize_header(k): (v or "").strip() for k, v in raw.items() if k is not None}

            req_id = _pick_first(norm, ["req_id", "id", "requirement_id"], default=f"REQ-{idx:03d}")

            text = _pick_first(
                norm,
                ["requirement_text", "text", "requirement", "description", "content"],
                default="",
            )

            title = _pick_first(norm, ["title", "summary"], default="")
            if not title:
                system = _pick_first(norm, ["system"], default="")
                component = _pick_first(norm, ["component"], default="")
                priority = _pick_first(norm, ["priority"], default="")
                parts = [p for p in [system, component, priority] if p]
                title = " / ".join(parts)

            source = _pick_first(norm, ["source", "tool", "origin"], default="demo")

            acceptance_criteria = _pick_first(norm, ["acceptance_criteria", "ac"], default="")
            verification_method = _pick_first(norm, ["verification_method", "verification"], default="")
            rationale = _pick_first(norm, ["rationale"], default="")

            system = _pick_first(norm, ["system"], default="")
            component = _pick_first(norm, ["component"], default="")
            priority = _pick_first(norm, ["priority"], default="")

            if not title and not text:
                log.warning(f"Row {idx}: empty requirement (no title/text) -> skipped")
                continue

            rows.append(
                {
                    "req_id": req_id,
                    "title": title,
                    "text": text,
                    "source": source,
                    "system": system,
                    "component": component,
                    "priority": priority,
                    "verification_method": verification_method,
                    "acceptance_criteria": acceptance_criteria,
                    "rationale": rationale,
                }
            )

        return rows


def _row_to_requirement(row: Dict[str, str]) -> Requirement:
    """
    Convertit une ligne normalisée (dict) en Requirement (modèle domaine).
    Lève ValueError si invalide (contrat Requirement.__post_init__).
    """
    return Requirement(
        req_id=row.get("req_id", ""),
        title=row.get("title", ""),
        text=row.get("text", ""),
        source=row.get("source", "demo"),
        system=row.get("system", ""),
        component=row.get("component", ""),
        priority=row.get("priority", ""),
        rationale=row.get("rationale", ""),
        verification_method=row.get("verification_method", ""),
        acceptance_criteria=row.get("acceptance_criteria", ""),
        meta={},  # réservé (extensions futures)
    )


# ============================================================
# 🧾 Outputs legacy (compat)
# ============================================================
def write_output_csv(out_path: Path, analyses: List[AnalysisResult]) -> None:
    """
    Écrit un CSV enrichi (legacy) :
      - status/score
      - issues_count/suggestions_count
      - issues_json/suggestions_json (compact JSON)
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "req_id",
        "title",
        "text",
        "source",
        "system",
        "component",
        "priority",
        "verification_method",
        "acceptance_criteria",
        "status",
        "score",
        "issues_count",
        "suggestions_count",
        "issues_json",
        "suggestions_json",
    ]

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for a in analyses:
            req = a.requirement
            issues_json = json.dumps([i.to_dict() for i in a.issues], ensure_ascii=False, separators=(",", ":"))
            suggs_json = json.dumps([s.to_dict() for s in a.suggestions], ensure_ascii=False, separators=(",", ":"))

            writer.writerow(
                {
                    "req_id": req.req_id,
                    "title": req.title,
                    "text": req.text,
                    "source": req.source,
                    "system": req.system,
                    "component": req.component,
                    "priority": req.priority,
                    "verification_method": req.verification_method,
                    "acceptance_criteria": req.acceptance_criteria,
                    "status": a.status,
                    "score": "" if a.score is None else a.score,
                    "issues_count": len(a.issues),
                    "suggestions_count": len(a.suggestions),
                    "issues_json": issues_json,
                    "suggestions_json": suggs_json,
                }
            )


def _html_escape(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def write_output_html(out_path: Path, analyses: List[AnalysisResult]) -> None:
    """
    Génère un HTML standalone minimal (legacy) ouvrable localement.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def _issues_summary(a: AnalysisResult) -> str:
        if not a.issues:
            return '<span style="color:#2e7d32;font-weight:bold">OK</span>'
        items = "".join(
            f"<li><b>{_html_escape(i.rule_id)}</b> [{_html_escape(i.severity.value)}] — {_html_escape(i.message)}</li>"
            for i in a.issues
        )
        return f"<ul style='margin:0;padding-left:18px'>{items}</ul>"

    rows = "\n".join(
        f"""
        <tr>
          <td>{_html_escape(a.requirement.req_id)}</td>
          <td>{_html_escape(a.requirement.title)}</td>
          <td style="white-space:pre-wrap">{_html_escape(a.requirement.text)}</td>
          <td>{_html_escape(a.requirement.source)}</td>
          <td>{_html_escape(a.status)}</td>
          <td style="text-align:right">{"" if a.score is None else a.score}</td>
          <td>{_issues_summary(a)}</td>
        </tr>
        """.strip()
        for a in analyses
    )

    html = f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>APP1 QRA — Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; background: #f5f7fa; color: #333; }}
    header {{ font-size: 24px; font-weight: bold; padding-bottom: 10px; margin-bottom: 20px; border-bottom: 2px solid #888; }}
    .badge {{ display:inline-block; padding:2px 8px; border-radius:12px; font-size:12px; background:#e9eef6; border:1px solid #c9d6ea; color:#234; margin-left: 8px; }}
    table {{ border-collapse: collapse; width: 100%; background: #fff; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    th {{ background: #f0f0f0; text-align: left; }}
    .meta {{ color:#555; margin: 10px 0 18px 0; }}
  </style>
</head>
<body>
  <header>
    APP1 — QRA (Quality Risk Assessment)
    <span class="badge">MVP CLI 1.8.2</span>
  </header>

  <div class="meta">
    Généré le {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} — Exigences analysées : {len(analyses)}
  </div>

  <table>
    <thead>
      <tr>
        <th>ID</th><th>Titre</th><th>Texte</th><th>Source</th>
        <th>Status</th><th>Score</th><th>Issues</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>
"""
    out_path.write_text(html, encoding="utf-8")


# ============================================================
# 🔧 Fonction principale (pipeline)
# ============================================================
def process(data: Dict[str, Any]) -> ProcessResult:
    """
    Pipeline QRA :
      1) charge CSV
      2) map -> Requirement
      3) règles déterministes
      4) suggestions IA optionnelles (non bloquantes)
      5) outputs legacy + rapports structurés
    """
    try:
        if not isinstance(data, dict):
            raise ModuleError("Invalid input: 'data' must be a dict.")

        input_path = Path(str(data.get("input_path", "data/inputs/demo_input.csv")))
        out_dir = Path(str(data.get("out_dir", os.getenv("OUTPUT_DIR", "data/outputs"))))
        fail_on_empty = bool(data.get("fail_on_empty", False))
        verbose = bool(data.get("verbose", False))

        if verbose:
            log.setLevel(logging.DEBUG)

        log.info("Démarrage APP1 QRA — CLI (1.8.2)")
        log.info(f"Input   : {input_path}")
        log.info(f"Out dir : {out_dir}")

        enable_ai_env = str(os.getenv("ENABLE_AI", "0"))
        has_key = bool((os.getenv("OPENAI_API_KEY") or "").strip())
        log.info(
            f"AI      : {'enabled' if enable_ai_env.strip() in {'1','true','yes','on'} else 'disabled'} "
            f"(ENABLE_AI={enable_ai_env}, key={'yes' if has_key else 'no'})"
        )

        # 1) Load raw rows
        rows = load_requirements_csv(input_path)
        if fail_on_empty and not rows:
            raise ModuleError("Empty dataset (0 valid requirements).")

        # 2) Map rows -> Requirement
        requirements: List[Requirement] = []
        for idx, row in enumerate(rows, start=1):
            try:
                requirements.append(_row_to_requirement(row))
            except Exception as e:
                raise ModuleError(f"Invalid requirement at row#{idx}: {e}") from e

        log.info("Rules   : enabled (1.8.2)")

        # 3) Analyze (rules)
        analyses: List[AnalysisResult] = [analyze_requirement(r, verbose=verbose) for r in requirements]

        # 3bis) AI suggestions (optional, non-blocking)
        log.info("AI      : optional suggestions (1.9.2)")
        ai_candidates = [a for a in analyses if a.issues]  # ONLY at-risk
        log.info(f"AI      : candidates={len(ai_candidates)}/{len(analyses)} (issues>0)")

        for analysis in ai_candidates:
            try:
                ai_suggestions = suggest_improvements(
                    req=analysis.requirement,
                    issues=analysis.issues,
                    max_suggestions=3,
                    verbose=verbose,
                )
                if ai_suggestions:
                    analysis.suggestions.extend(ai_suggestions)
            except Exception as e:
                log.warning(f"AI suggestion skipped for {analysis.requirement.req_id}: {e}")

        # 4) Outputs legacy (CSV + HTML)
        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir.mkdir(parents=True, exist_ok=True)

        out_csv = out_dir / f"qra_output_{stamp}.csv"
        out_html = out_dir / f"qra_output_{stamp}.html"

        write_output_csv(out_csv, analyses)
        write_output_html(out_html, analyses)

        # 4bis) Rapport HTML/CSV QRA structuré (stable paths)
        qra_report_path = out_dir / "qra_report.html"
        qra_report_csv_path = out_dir / "qra_report.csv"

        def _display_status(a: AnalysisResult) -> str:
            if a.status == "CHECKED" and not a.issues:
                return "OK"
            if a.status == "CHECKED" and a.issues:
                return "À risque"
            return a.status

        qra_result = {
            "requirements": [
                {
                    "id": a.requirement.req_id,
                    "text": a.requirement.text,
                    "score": a.score,
                    "raw_status": a.status,
                    "display_status": _display_status(a),
                    "issues": [{"severity": i.severity.value, "message": i.message} for i in a.issues],
                    "ai_suggestions": [s.message for s in a.suggestions if s.source == SuggestionSource.AI],
                }
                for a in analyses
            ],
            "global_score": (
                round(sum(valid_scores) / len(valid_scores), 1)
                if (valid_scores := [a.score for a in analyses if isinstance(a.score, int)])
                else 0.0
            ),
            "global_status": "OK" if all(_display_status(a) == "OK" for a in analyses) else "À risque",
        }

        generate_html_report(qra_result=qra_result, output_path=qra_report_path, verbose=verbose)
        generate_csv_report(qra_result=qra_result, output_path=qra_report_csv_path, verbose=verbose)

        # 5) Payload final
        payload = {
            "count": len(analyses),
            "input": str(input_path),
            "out_dir": str(out_dir),
            "output_legacy_csv": str(out_csv),
            "output_legacy_html": str(out_html),
            "output_qra_report_html": str(qra_report_path),
            # backward compatibility
            "output_csv": str(out_csv),
            "output_html": str(out_html),
            "output_qra_report": str(qra_report_path),
            "output_qra_report_csv": str(qra_report_csv_path),
        }

        return ProcessResult(ok=True, payload=payload, message="OK")

    except ModuleError:
        raise
    except Exception as e:
        log.exception("Erreur inattendue dans process()")
        raise ModuleError(str(e)) from e


# ============================================================
# ▶️ Main (CLI)
# ============================================================
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="vv-app1-qra",
        description=(
            "APP1 QRA — CLI: read requirements CSV, run deterministic rules, "
            "optionally add AI suggestions (non-blocking), and generate outputs (CSV + HTML reports)."
        ),
    )

    p.add_argument(
        "--input",
        default="data/inputs/demo_input.csv",
        help="Path to input CSV (default: data/inputs/demo_input.csv)",
    )

    p.add_argument(
        "--out-dir",
        default=os.getenv("OUTPUT_DIR", "data/outputs"),
        help="Output directory (default: OUTPUT_DIR or data/outputs)",
    )

    p.add_argument(
        "--fail-on-empty",
        action="store_true",
        help="Fail (non-zero) if no valid requirement is loaded.",
    )

    p.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG logs.",
    )

    return p


def main() -> None:
    args = _build_parser().parse_args()
    out = process(
        {
            "input_path": args.input,
            "out_dir": args.out_dir,
            "fail_on_empty": args.fail_on_empty,
            "verbose": args.verbose,
        }
    )
    log.info(f"Résultat : ok={out.ok}, message={out.message}")
    log.info(f"Payload  : {out.payload}")


if __name__ == "__main__":
    main()
