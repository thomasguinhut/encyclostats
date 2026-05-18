import csv
import logging
import os
from typing import Optional

from config import OUTPUT_CSV

logger = logging.getLogger(__name__)

_FIELDNAMES = ["titre", "url", "url_pdf", "mots_cles", "statut"]


def initialiser_csv() -> None:
    """Crée le CSV avec l'en-tête s'il n'existe pas encore."""
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    if not os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
            writer.writeheader()
        logger.info("Fichier CSV initialisé : %s", OUTPUT_CSV)


def charger_urls_traitees() -> set[str]:
    """Retourne l'ensemble des URLs déjà présentes dans le CSV (checkpoint)."""
    if not os.path.exists(OUTPUT_CSV):
        return set()
    urls = set()
    with open(OUTPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("url"):
                urls.add(row["url"].strip())
    logger.info("%d URL(s) déjà traitée(s) trouvée(s) dans le CSV.", len(urls))
    return urls


def sauvegarder_ligne(
    titre: str,
    url: str,
    urls_pdf: list[str],
    mots_cles: str,
    statut: str,
    erreur: Optional[str] = None,
) -> None:
    """Ajoute une ligne au CSV. Écriture immédiate (append) pour robustesse."""
    ligne = {
        "titre": titre,
        "url": url,
        "url_pdf": " | ".join(urls_pdf) if urls_pdf else "",
        "mots_cles": mots_cles if statut == "ok" else (erreur or ""),
        "statut": statut,
    }
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
        writer.writerow(ligne)
