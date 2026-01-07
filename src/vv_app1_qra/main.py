#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
vv_app1_qra.main
------------------------------------------------------------
Description :
    APP1 — QRA (Quality Risk Assessment)
    Étape 1.6 — CLI main

Rôle :
    - Fournir une CLI robuste (sans IA) :
        * lecture CSV exigences
        * orchestration MVP (chargement + préparation)
        * génération outputs (CSV + HTML)
    - Aucune dépendance aux modules futurs (models/rules/ia/report),
      ceux-ci arriveront aux étapes 1.7+.

Architecture (repo) :
    - Code : src/vv_app1_qra/
    - Tests : tests/
    - Données : data/
    - Docs : docs/
    - Templates : templates/

Usage CLI :
    python -m vv_app1_qra.main
    python -m vv_app1_qra.main --input data/inputs/demo_input.csv --out-dir data/outputs
    python -m vv_app1_qra.main --verbose
    python -m vv_app1_qra.main --fail-on-empty

Usage test :
    pytest

Notes :
    - L’IA est volontairement ABSENTE en 1.6 (ENABLE_AI ignoré ici).
    - Le HTML est un rendu standalone minimal (ouvrable localement).
============================================================
"""

from __future__ import annotations

# ============================================================
# 📦 Imports
# ============================================================
import argparse
import csv
import datetime as dt
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


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
# 🔧 Fonctions principales
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

    Retour :
      - Liste de dict normalisés (minimum : req_id, title, text, source)
        + champs conservés utiles pour 1.8+
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


def write_output_csv(out_path: Path, requirements: List[Dict[str, str]]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
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
            ],
        )
        writer.writeheader()
        for r in requirements:
            writer.writerow(
                {
                    "req_id": r.get("req_id", ""),
                    "title": r.get("title", ""),
                    "text": r.get("text", ""),
                    "source": r.get("source", ""),
                    "system": r.get("system", ""),
                    "component": r.get("component", ""),
                    "priority": r.get("priority", ""),
                    "verification_method": r.get("verification_method", ""),
                    "acceptance_criteria": r.get("acceptance_criteria", ""),
                    "status": "LOADED",  # les règles enrichiront plus tard (1.8)
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


def write_output_html(out_path: Path, requirements: List[Dict[str, str]]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = "\n".join(
        f"""
        <tr>
          <td>{_html_escape(r.get("req_id", ""))}</td>
          <td>{_html_escape(r.get("title", ""))}</td>
          <td style="white-space:pre-wrap">{_html_escape(r.get("text", ""))}</td>
          <td>{_html_escape(r.get("source", ""))}</td>
        </tr>
        """.strip()
        for r in requirements
    )

    html = f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>APP1 QRA — Demo Report</title>
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
    <span class="badge">MVP CLI 1.6</span>
  </header>

  <div class="meta">
    Généré le {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} — Exigences chargées : {len(requirements)}
  </div>

  <p>
    Rapport minimal pour l’étape 1.6 : chargement CSV + outputs.
    Les règles déterministes et suggestions (IA optionnelle) arriveront aux étapes 1.8–1.10.
  </p>

  <table>
    <thead>
      <tr><th>ID</th><th>Titre</th><th>Texte</th><th>Source</th></tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>
"""
    out_path.write_text(html, encoding="utf-8")


def process(data: Dict[str, Any]) -> ProcessResult:
    """
    Fonction principale du module.
    """
    try:
        if not isinstance(data, dict):
            raise ModuleError("Invalid input: 'data' must be a dict.")

        input_path = Path(str(data.get("input_path", "data/demo_input.csv")))
        out_dir = Path(str(data.get("out_dir", os.getenv("OUTPUT_DIR", "data"))))
        fail_on_empty = bool(data.get("fail_on_empty", False))
        verbose = bool(data.get("verbose", False))

        if verbose:
            log.setLevel(logging.DEBUG)

        log.info("Démarrage APP1 QRA — CLI (1.6)")
        log.info(f"Input   : {input_path}")
        log.info(f"Out dir : {out_dir}")
        log.info("AI      : disabled (1.6)")

        requirements = load_requirements_csv(input_path)

        if fail_on_empty and not requirements:
            raise ModuleError("Empty dataset (0 valid requirements).")

        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_csv = out_dir / f"qra_output_{stamp}.csv"
        out_html = out_dir / f"qra_output_{stamp}.html"

        write_output_csv(out_csv, requirements)
        write_output_html(out_html, requirements)

        payload = {
            "count": len(requirements),
            "input": str(input_path),
            "out_dir": str(out_dir),
            "output_csv": str(out_csv),
            "output_html": str(out_html),
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
            "APP1 QRA — CLI (MVP 1.6): "
            "read CSV requirements and generate demo outputs (no AI)."
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
