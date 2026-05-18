import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.page import scraper_page
from scraper.pdf import extraire_textes_pdfs
from llm.prompt import analyser_url
from llm.model import get_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")

URLS_TEST = [
    "https://www.insee.fr/fr/statistiques/8296252",
    "https://www.justice.gouv.fr/documentation/etudes-et-statistiques/condamnations-inscrites-au-casier-judiciaire-2019-2020",
    "https://www.statistiques.developpement-durable.gouv.fr/milieux-agricoles-et-enjeux-environnementaux-en-france-etat-des-connaissances-en-2025",
]


def traiter_url(url: str) -> None:
    try:
        logger.info("Scraping : %s", url)
        titre, texte_html, urls_pdf = scraper_page(url)

        texte_pdf, urls_pdf_traitees = extraire_textes_pdfs(urls_pdf)

        texte_complet = texte_html
        if texte_pdf:
            texte_complet += "\n\n" + texte_pdf

        logger.info("Génération du résumé…")
        resume = analyser_url(titre, texte_complet)

        print(f"\n{'='*60}")
        print(f"URL   : {url}")
        print(f"Titre : {titre}")
        print(f"PDFs  : {', '.join(urls_pdf_traitees) or '—'}")
        print(f"\nRésumé :\n{resume}")
        print(f"{'='*60}\n")

    except Exception as exc:
        logger.error("Échec pour %s — %s: %s", url, type(exc).__name__, exc)


def mode_interactif() -> None:
    get_pipeline()
    print("Modèle chargé. Entrez une URL par ligne (q pour quitter).\n")
    while True:
        try:
            url = input("URL > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nArrêt.")
            break
        if url.lower() in ("q", "quit", "exit", ""):
            break
        traiter_url(url)


def main(urls: list[str]) -> None:
    get_pipeline()
    for url in urls:
        traiter_url(url)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1:])
    else:
        mode_interactif()
