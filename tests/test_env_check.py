"""
============================================================
test_env_check.py
------------------------------------------------------------
Description :
    Tests unitaires (pytest) — tools/env_check.py

Objectifs :
    - Vérifier la collecte d'informations d'environnement (nominal)
    - Vérifier le rendu Markdown (sections attendues)
    - Vérifier l'écriture des sorties (texte + JSON)
    - Vérifier des invariants simples (types / clés / bool)

Usage :
    pytest -vv
============================================================
"""

import json
from pathlib import Path

import pytest

from tools.env_check import (
    collect_env_info,
    env_info_to_dict,
    render_markdown,
    write_json,
    write_text,
    is_healthy_minimal,
)


# ============================================================
# 🔧 Fixtures
# ============================================================
@pytest.fixture
def env_info():
    """Collecte un snapshot d'environnement pour les tests."""
    return collect_env_info()


@pytest.fixture
def env_dict(env_info):
    """Retourne la version dict stable du snapshot environnement."""
    return env_info_to_dict(env_info)


# ============================================================
# 🧪 Tests
# ============================================================
def test_collect_env_info_has_expected_fields(env_dict):
    """
    Vérifie la présence des champs attendus dans la structure dict.
    """
    expected_keys = {
        "timestamp_utc",
        "cwd",
        "project_root",
        "python_version",
        "python_executable",
        "pip_version",
        "is_venv",
        "venv_prefix",
        "os_name",
        "os_release",
        "platform",
    }

    assert expected_keys.issubset(set(env_dict.keys()))
    assert isinstance(env_dict["python_version"], str)
    assert isinstance(env_dict["python_executable"], str)
    assert isinstance(env_dict["pip_version"], str)
    assert isinstance(env_dict["is_venv"], bool)


def test_render_markdown_contains_sections(env_info):
    """
    Vérifie que le rendu Markdown contient les sections clés (format stable).
    """
    md = render_markdown(env_info)

    assert "# Environment Healthcheck Report" in md
    assert "## Checks" in md
    assert "## Runtime" in md
    assert "## System" in md
    assert "## Project" in md
    assert "Verdict:" in md


def test_render_markdown_redact_paths_is_safe(env_info):
    """
    Vérifie que le mode redact ne casse pas le rendu (pas d'exigence sur la valeur exacte).
    """
    md = render_markdown(env_info, redact_paths=True)

    assert "Environment Healthcheck Report" in md
    assert "## Project" in md
    # On s'assure juste que le report reste cohérent et non vide.
    assert len(md) > 100


def test_is_healthy_minimal_returns_bool(env_info):
    """
    Vérifie que le healthcheck minimal renvoie toujours un bool.
    """
    assert isinstance(is_healthy_minimal(env_info), bool)


def test_write_text_creates_file(tmp_path: Path):
    """
    Vérifie l'écriture texte et la création du fichier.
    """
    out = tmp_path / "env_report.md"
    content = "hello"

    write_text(out, content)

    assert out.exists()
    assert out.read_text(encoding="utf-8") == content


def test_write_json_creates_valid_json(tmp_path: Path):
    """
    Vérifie l'écriture JSON et la validité du contenu.
    """
    out = tmp_path / "env_report.json"
    payload = {"a": 1, "b": "x"}

    write_json(out, payload)

    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data == payload
