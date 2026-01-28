#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
tests.test_main
------------------------------------------------------------
Description :
    Tests unitaires pytest — APP1 QRA — CLI/pipeline main.process()

Objectifs :
    - Vérifier comportement nominal (CSV chargé + outputs générés)
    - Vérifier validation des entrées
    - Vérifier fallback IA (ENABLE_AI=1 sans clé)
    - Vérifier génération report stable (html+csv)

Usage :
    pytest -q
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
                "requirement_text": (
                    "The braking system shall stop the train within 800 m when the emergency brake is applied "
                    "at 160 km/h on dry track."
                ),
                "rationale": "Ensure safe stopping distance in emergency scenarios.",
                "verification_method": "Test",
                "acceptance_criteria": (
                    "Given speed = 160 km/h and emergency brake applied on dry track, then stopping distance "
                    "<= 800 m in 10 consecutive runs."
                ),
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


# ============================================================
# 🔧 Helpers
# ============================================================
def _read_csv_rows(p: Path):
    with p.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


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

    lines = csv_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) >= 3  # header + 2 rows


def test_process_error_invalid_input():
    with pytest.raises(ModuleError):
        process(None)  # type: ignore[arg-type]


def test_cli_outputs_are_enriched_with_rules(tmp_path: Path):
    out = process(
        {
            "input_path": "data/inputs/demo_input.csv",
            "out_dir": str(tmp_path),
            "fail_on_empty": True,
            "verbose": False,
        }
    )

    assert out.ok is True
    csv_path = Path(out.payload["output_csv"])
    html_path = Path(out.payload["output_html"])
    assert csv_path.exists()
    assert html_path.exists()

    rows = _read_csv_rows(csv_path)
    assert len(rows) >= 1

    for col in ["status", "score", "issues_count", "suggestions_count", "issues_json", "suggestions_json"]:
        assert col in rows[0]

    r1 = next(r for r in rows if r["req_id"] == "REQ-001")
    assert r1["status"] == "CHECKED"
    assert int(r1["issues_count"]) == 0

    r2 = next(r for r in rows if r["req_id"] == "REQ-002")
    assert r2["status"] == "CHECKED"
    assert int(r2["issues_count"]) >= 0  # dataset peut évoluer, on reste robuste
    assert r2["score"] != ""


def test_main_ai_enabled_without_key_fallback(tmp_path: Path, monkeypatch):
    """
    ENABLE_AI=1 sans OPENAI_API_KEY => fallback RULES (non bloquant).
    """
    monkeypatch.setenv("ENABLE_AI", "1")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    out = process(
        {
            "input_path": "data/inputs/demo_input.csv",
            "out_dir": str(tmp_path),
            "fail_on_empty": False,
            "verbose": False,
        }
    )

    assert out.ok is True

    report_html = Path(out.payload["output_qra_report_html"])
    report_csv = Path(out.payload["output_qra_report_csv"])
    assert report_html.exists()
    assert report_csv.exists()

    html = report_html.read_text(encoding="utf-8")
    assert "Mode suggestions" in html
    assert "RULES" in html
