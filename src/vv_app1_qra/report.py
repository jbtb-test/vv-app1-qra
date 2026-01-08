"""
============================================================
report.py
------------------------------------------------------------
Génération du rapport HTML QRA (APP1)

- HTML statique ouvrable localement
- Vue synthèse + détails par exigence
- IA = suggestions uniquement (non décisionnelle)
============================================================
"""

from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape


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

    base_dir = Path(__file__).resolve().parents[2]
    template_dir = base_dir / "templates" / "qra"

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html"])
    )

    template = env.get_template("report_qra.html")

    requirements = qra_result["requirements"]
    global_score = qra_result["global_score"]
    global_status = qra_result["global_status"]

    html = template.render(
        title="Quality Risk Assessment — Rapport",
        header="Quality Risk Assessment — Outil V&V",
        badge=datetime.now().strftime("%Y-%m-%d %H:%M"),
        global_score=global_score,
        global_status=global_status,
        requirements=requirements,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    if verbose:
        print(f"[REPORT] HTML généré : {output_path}")

    return output_path
