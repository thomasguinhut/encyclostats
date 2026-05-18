"""
Encyclostat — pipeline principal.

Pour chaque URL de publication statistique :
  1. Scrape le HTML (titre + texte principal + liens PDF)
  2. Télécharge jusqu'à MAX_PDFS_PER_PAGE PDFs, extrait leur texte, supprime les fichiers
  3. Envoie le texte agrégé à Mistral-7B pour générer des mots-clés
  4. Sauvegarde immédiatement la ligne dans output.csv
  5. Reprend automatiquement après un plantage (checkpoint)
"""
import logging
import sys
import time

# On s'assure que les imports relatifs fonctionnent quel que soit le CWD
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DELAY_BETWEEN_URLS
from scraper.page import scraper_page
from scraper.pdf import extraire_textes_pdfs
from llm.prompt import analyser_url
from llm.model import get_pipeline          # préchauffe le singleton au démarrage
from storage.csv_writer import (
    charger_urls_traitees,
    initialiser_csv,
    sauvegarder_ligne,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")

# ---------------------------------------------------------------------------
# URLs de test
# ---------------------------------------------------------------------------
URLS_TEST = [
    "https://www.insee.fr/fr/statistiques/8296252",
    "https://www.justice.gouv.fr/documentation/etudes-et-statistiques/condamnations-inscrites-au-casier-judiciaire-2019-2020",
    "https://www.statistiques.developpement-durable.gouv.fr/milieux-agricoles-et-enjeux-environnementaux-en-france-etat-des-connaissances-en-2025",
]


def traiter_url(url: str) -> None:
    titre = ""
    urls_pdf_traitees: list[str] = []

    try:
        # --- 1. Scraping HTML ---
        logger.info("Scraping : %s", url)
        titre, texte_html, urls_pdf = scraper_page(url)

        # --- 2. Extraction PDFs ---
        texte_pdf, urls_pdf_traitees = extraire_textes_pdfs(urls_pdf)

        # --- 3. Agrégation du texte ---
        texte_complet = texte_html
        if texte_pdf:
            texte_complet += "\n\n" + texte_pdf

        # --- 4. Génération des mots-clés ---
        logger.info("Génération des mots-clés pour : %s", titre or url)
        mots_cles = analyser_url(titre, texte_complet)

        # --- 5. Sauvegarde ---
        sauvegarder_ligne(
            titre=titre,
            url=url,
            urls_pdf=urls_pdf_traitees,
            mots_cles=mots_cles,
            statut="ok",
        )
        logger.info("OK — %d mots-clés sauvegardés.", len(mots_cles.split(",")))

    except Exception as exc:
        message_erreur = f"{type(exc).__name__}: {exc}"
        logger.error("Échec pour %s — %s", url, message_erreur)
        sauvegarder_ligne(
            titre=titre,
            url=url,
            urls_pdf=urls_pdf_traitees,
            mots_cles="",
            statut="erreur",
            erreur=message_erreur,
        )


def main(urls: list[str]) -> None:
    # Initialisation du CSV et chargement du checkpoint
    initialiser_csv()
    deja_traitees = charger_urls_traitees()

    # Préchargement du modèle une seule fois avant la boucle
    get_pipeline()

    urls_a_traiter = [u for u in urls if u not in deja_traitees]
    logger.info(
        "%d URL(s) à traiter (%d ignorée(s) déjà traitées).",
        len(urls_a_traiter),
        len(urls) - len(urls_a_traiter),
    )

    for i, url in enumerate(urls_a_traiter):
        logger.info("--- [%d/%d] %s ---", i + 1, len(urls_a_traiter), url)
        traiter_url(url)

        if i < len(urls_a_traiter) - 1:
            time.sleep(DELAY_BETWEEN_URLS)

    logger.info("Pipeline terminé.")


if __name__ == "__main__":
    # Possibilité de passer des URLs en arguments, sinon on utilise la liste de test
    urls = sys.argv[1:] if len(sys.argv) > 1 else URLS_TEST
    main(urls)
