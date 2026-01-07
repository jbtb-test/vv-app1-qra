"""
============================================================
tests/test_main.py
------------------------------------------------------------
Description :
    Tests unitaires pytest pour APP1 QRA — étape 1.6 (CLI main)

Objectifs :
    - Vérifier comportement nominal (CSV chargé + outputs générés)
    - Vérifier validation des entrées
    - Vérifier encapsulation des erreurs (ModuleError)

Usage :
    pytest
============================================================
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from vv_app1_qra.main import ModuleError, process


# ============================================================
# 🔧 Fixtures
# ============================================================
@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    """
    Génère un CSV réaliste conforme au schéma demo_input.csv (APP1).
    """
    p = tmp_path / "demo_input.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "req_id",
                "system",
                "component",
                "priority",
                "source",
                "requirement_text",
                "rationale",
                "verification_method",
                "acceptance_criteria",
            ],
        )
        w.writeheader()
        w.writerow(
            {
                "req_id": "REQ-001",
                "system": "Train Control",
                "component": "Brake",
                "priority": "High",
                "source": "Stakeholder",
                "requirement_text": "The braking system shall stop the train within 800 m when the emergency brake is applied at 160 km/h on dry track.",
                "rationale": "Ensure safe stopping distance in emergency scenarios.",
                "verification_method": "Test",
                "acceptance_criteria": "Given speed = 160 km/h and emergency brake applied on dry track, then stopping distance <= 800 m in 10 consecutive runs.",
            }
        )
        w.writerow(
            {
                "req_id": "REQ-002",
                "system": "Train Control",
                "component": "HMI",
                "priority": "Medium",
                "source": "System",
                "requirement_text": "The HMI shall display the brake status within 200 ms after any state change.",
                "rationale": "Provide timely feedback to the driver.",
                "verification_method": "Test",
                "acceptance_criteria": "When brake state changes, display update latency <= 200 ms in 20 consecutive changes.",
            }
        )
    return p


@pytest.fixture
def out_dir(tmp_path: Path) -> Path:
    return tmp_path / "out"


@pytest.fixture
def invalid_input():
    return None


# ============================================================
# 🧪 Tests
# ============================================================
def test_process_nominal(sample_csv: Path, out_dir: Path):
    out = process({"input_path": str(sample_csv), "out_dir": str(out_dir), "verbose": False})

    assert out.ok is True
    assert out.message == "OK"
    assert out.payload["count"] == 2

    csv_path = Path(out.payload["output_csv"])
    html_path = Path(out.payload["output_html"])

    assert csv_path.exists()
    assert html_path.exists()
    assert csv_path.read_text(encoding="utf-8").strip() != ""
    assert html_path.read_text(encoding="utf-8").strip().lower().startswith("<!doctype html>")

    # Sanity: output CSV contains header + at least 2 rows
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) >= 3


def test_process_error(invalid_input):
    with pytest.raises(ModuleError):
        process(invalid_input)
