"""
============================================================
tests.test_report
------------------------------------------------------------
Description :
    Tests unitaires (pytest) — APP1 QRA — Étape 1.12
    Validation de la génération du rapport HTML structuré.

Objectifs :
    - Vérifier que le rapport HTML est généré
    - Vérifier que le fichier n’est pas vide
    - Vérifier la présence d’éléments clés (score, statut, exigences)
============================================================
"""

import csv
import re
from pathlib import Path

from vv_app1_qra.report import generate_csv_report, generate_html_report

# ============================================================
# 🧪 Tests
# ============================================================
def test_generate_html_report_creates_valid_html(tmp_path: Path):
    """
    Vérifie que generate_html_report() produit un fichier HTML valide.
    """
    output_path = tmp_path / "qra_report.html"

    qra_result = {
        "global_score": 85,
        "global_status": "À risque",
        "requirements": [
            {
                "id": "REQ-001",
                "text": "The system shall respond within 200 ms.",
                "score": 100,
                "raw_status": "CHECKED",
                "display_status": "OK",
                "issues": [],
                "ai_suggestions": [],
            },
            {
                "id": "REQ-002",
                "text": "The UI should be fast.",
                "score": 70,
                "raw_status": "CHECKED",
                "display_status": "À risque",
                "issues": [
                    {
                        "severity": "MINOR",
                        "message": "Weak modal detected",
                    }
                ],
                "ai_suggestions": [
                    "Use shall with measurable criteria"
                ],
            },
        ],
    }

    result_path = generate_html_report(
        qra_result=qra_result,
        output_path=output_path,
        verbose=False,
    )

    # Fichier créé
    assert result_path.exists()

    # Contenu HTML
    content = result_path.read_text(encoding="utf-8")

    assert "<html" in content.lower()
    assert "Quality Risk Assessment" in content
    assert "REQ-001" in content
    assert "REQ-002" in content
    assert "OK" in content
    assert "À risque" in content


def _normalize_report_html(html: str) -> str:
    # supprime le timestamp "YYYY-MM-DD HH:MM" dans le badge
    html = re.sub(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}", "<TS>", html)
    return html

def test_report_is_deterministic_except_timestamp(tmp_path, monkeypatch):
    # NO-AI forcé
    monkeypatch.setenv("ENABLE_AI", "0")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    from vv_app1_qra.report import generate_html_report

    qra_result = {
        "global_score": 90.0,
        "global_status": "À risque",
        "requirements": [
            {"id": "REQ-001", "score": 100, "display_status": "OK", "raw_status": "CHECKED", "text": "t1", "issues": [], "ai_suggestions": []},
            {"id": "REQ-002", "score": 70, "display_status": "À risque", "raw_status": "CHECKED", "text": "t2", "issues": [{"severity":"MAJOR","message":"m"}], "ai_suggestions": ["s1"]},
        ],
    }

    p1 = tmp_path / "r1.html"
    p2 = tmp_path / "r2.html"

    generate_html_report(qra_result, p1, verbose=False)
    generate_html_report(qra_result, p2, verbose=False)

    h1 = _normalize_report_html(p1.read_text(encoding="utf-8"))
    h2 = _normalize_report_html(p2.read_text(encoding="utf-8"))

    assert h1 == h2


def test_csv_report_contains_expected_ids_and_scores(tmp_path, monkeypatch):
    monkeypatch.setenv("ENABLE_AI", "0")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    from vv_app1_qra.report import generate_csv_report

    qra_result = {
        "global_score": 90.0,
        "global_status": "À risque",
        "requirements": [
            {"id": "REQ-001", "score": 100, "display_status": "OK", "raw_status": "CHECKED", "text": "t1", "issues": [], "ai_suggestions": []},
            {"id": "REQ-002", "score": 70, "display_status": "À risque", "raw_status": "CHECKED", "text": "t2", "issues": [{"severity":"MAJOR","message":"m"}], "ai_suggestions": ["s1"]},
        ],
    }

    out = tmp_path / "qra_report.csv"
    generate_csv_report(qra_result, out, verbose=False)

    with out.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    assert [r["id"] for r in rows] == ["REQ-001", "REQ-002"]
    assert [r["score"] for r in rows] == ["100", "70"]
