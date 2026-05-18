import logging
import os
import tempfile

import pdfplumber
import requests

from config import HEADERS, MAX_PDF_SIZE_MB, MAX_PDFS_PER_PAGE, PDF_DOWNLOAD_TIMEOUT

logger = logging.getLogger(__name__)

_MAX_BYTES = MAX_PDF_SIZE_MB * 1024 * 1024


def extraire_textes_pdfs(urls_pdf: list[str]) -> tuple[str, list[str]]:
    """
    Télécharge jusqu'à MAX_PDFS_PER_PAGE PDFs, en extrait le texte, puis supprime
    les fichiers temporaires.

    Retourne (texte_concatene, urls_effectivement_traitees).
    """
    morceaux: list[str] = []
    urls_traitees: list[str] = []

    for url in urls_pdf[:MAX_PDFS_PER_PAGE]:
        try:
            texte = _telecharger_et_extraire(url)
            if texte:
                morceaux.append(texte)
                urls_traitees.append(url)
                logger.debug("PDF extrait : %s (%d caractères)", url, len(texte))
        except Exception as exc:
            logger.warning("Échec extraction PDF %s : %s", url, exc)

    return "\n\n".join(morceaux), urls_traitees


def _telecharger_et_extraire(url: str) -> str:
    with requests.get(
        url,
        headers=HEADERS,
        timeout=PDF_DOWNLOAD_TIMEOUT,
        stream=True,
    ) as resp:
        resp.raise_for_status()

        # Vérification de la taille via Content-Length si disponible
        content_length = resp.headers.get("Content-Length")
        if content_length and int(content_length) > _MAX_BYTES:
            raise ValueError(
                f"PDF trop volumineux ({int(content_length) // 1024 // 1024} Mo)"
            )

        # Écriture dans un fichier temporaire
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name
            taille = 0
            for chunk in resp.iter_content(chunk_size=65536):
                taille += len(chunk)
                if taille > _MAX_BYTES:
                    raise ValueError("PDF trop volumineux (dépassement en cours de téléchargement)")
                tmp.write(chunk)

    try:
        return _extraire_texte_pdfplumber(tmp_path)
    finally:
        # Suppression immédiate — les PDFs ne sont jamais conservés
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _extraire_texte_pdfplumber(chemin: str) -> str:
    pages_texte: list[str] = []
    with pdfplumber.open(chemin) as pdf:
        for page in pdf.pages:
            texte = page.extract_text()
            if texte:
                pages_texte.append(texte.strip())
    return "\n\n".join(pages_texte)
