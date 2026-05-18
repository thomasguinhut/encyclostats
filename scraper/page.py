import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from config import HEADERS, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

# Balises dont le contenu est toujours ignoré
_NOISE_TAGS = {"script", "style", "nav", "header", "footer", "aside", "form"}

# Sélecteurs CSS qui correspondent souvent aux menus/sidebars
_NOISE_SELECTORS = [
    "[role='navigation']",
    "[role='banner']",
    "[role='contentinfo']",
    ".nav", ".navbar", ".menu", ".sidebar",
    ".breadcrumb", ".breadcrumbs",
    ".footer", ".header",
    "#nav", "#menu", "#footer", "#header", "#sidebar",
]


def scraper_page(url: str) -> tuple[str, str, list[str]]:
    """
    Scrape une page HTML et retourne (titre, texte_principal, liste_urls_pdf).

    Raises:
        requests.RequestException si la requête échoue.
    """
    response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    titre = _extraire_titre(soup)
    _nettoyer_soup(soup)
    texte = _extraire_texte_principal(soup)
    pdfs = _detecter_pdfs(soup, url)

    logger.debug("Page '%s' : %d caractères, %d PDF(s)", titre, len(texte), len(pdfs))
    return titre, texte, pdfs


def _extraire_titre(soup: BeautifulSoup) -> str:
    tag = soup.find("h1") or soup.find("title")
    return tag.get_text(separator=" ", strip=True) if tag else ""


def _nettoyer_soup(soup: BeautifulSoup) -> None:
    for tag in soup.find_all(_NOISE_TAGS):
        tag.decompose()
    for selector in _NOISE_SELECTORS:
        for tag in soup.select(selector):
            tag.decompose()


def _extraire_texte_principal(soup: BeautifulSoup) -> str:
    # Priorité : balise <main> ou <article>, sinon <body>
    conteneur = soup.find("main") or soup.find("article") or soup.find("body")
    if conteneur is None:
        return soup.get_text(separator="\n", strip=True)

    lignes = [
        ligne.strip()
        for ligne in conteneur.get_text(separator="\n").splitlines()
        if ligne.strip()
    ]
    return "\n".join(lignes)


def _detecter_pdfs(soup: BeautifulSoup, base_url: str) -> list[str]:
    urls_pdf = []
    base_domain = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}"

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href:
            continue

        href_lower = href.lower()
        if ".pdf" not in href_lower:
            continue

        # Résolution des URLs relatives
        if href.startswith("http"):
            pdf_url = href
        elif href.startswith("//"):
            pdf_url = "https:" + href
        elif href.startswith("/"):
            pdf_url = base_domain + href
        else:
            pdf_url = urljoin(base_url, href)

        if pdf_url not in urls_pdf:
            urls_pdf.append(pdf_url)

    return urls_pdf
