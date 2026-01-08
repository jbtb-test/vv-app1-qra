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

from pathlib import Path

from vv_app1_qra.report import generate_html_report


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
