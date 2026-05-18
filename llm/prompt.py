import logging
import re

from config import LLM_MAX_NEW_TOKENS, LLM_TEMPERATURE, MAX_TEXT_CHARS
from llm.model import generer_texte

logger = logging.getLogger(__name__)

_PROMPT_TEMPLATE = """\
Tu es un expert en statistiques publiques françaises. À partir du texte suivant extrait d'une publication statistique officielle, génère entre 30 et 50 mots-clés exhaustifs en français.

Les mots-clés doivent couvrir obligatoirement :
- Le sujet principal et les sous-thèmes abordés
- Les années ou périodes de référence mentionnées
- Les groupes démographiques concernés (âge, sexe, catégorie socioprofessionnelle, etc.)
- Les territoires ou niveaux géographiques (France, régions, départements, etc.)
- Les chiffres ou indicateurs clés cités
- Les concepts statistiques utilisés (taux, indice, enquête, cohorte, etc.)
- Les sources de données ou organismes producteurs mentionnés
- Les synonymes et termes proches qu'un utilisateur pourrait employer pour chercher cette publication

Retourne UNIQUEMENT les mots-clés séparés par des virgules, sans introduction, sans numérotation, sans explication.

Texte :
{texte}

Mots-clés :"""


def construire_prompt(texte: str) -> str:
    texte_tronque = texte[:MAX_TEXT_CHARS]
    return _PROMPT_TEMPLATE.format(texte=texte_tronque)


def extraire_mots_cles(reponse_brute: str) -> str:
    """Nettoie la réponse LLM pour ne garder que les mots-clés."""
    # On prend tout jusqu'à la première ligne vide ou un double saut de ligne
    premiere_section = reponse_brute.split("\n\n")[0]

    # On vire les éventuelles listes à puces ou numérotées
    premiere_section = re.sub(r"^\s*[-•*\d.]+\s*", "", premiere_section, flags=re.MULTILINE)

    # Normalisation des séparateurs (point-virgule → virgule)
    premiere_section = premiere_section.replace(";", ",")

    # On supprime les lignes vides et on rejoint
    mots = [m.strip() for m in premiere_section.split(",") if m.strip()]
    return ", ".join(mots)


def analyser_url(titre: str, texte_complet: str) -> str:
    """
    Génère les mots-clés pour une publication.

    Args:
        titre: titre de la page (peut être vide)
        texte_complet: concaténation du texte HTML + texte PDFs

    Returns:
        Chaîne de mots-clés séparés par des virgules.
    """
    entete = f"Titre : {titre}\n\n" if titre else ""
    prompt = construire_prompt(entete + texte_complet)

    reponse = generer_texte(
        prompt=prompt,
        max_new_tokens=LLM_MAX_NEW_TOKENS,
        temperature=LLM_TEMPERATURE,
    )

    mots_cles = extraire_mots_cles(reponse)
    logger.debug("Mots-clés générés (%d) : %s", len(mots_cles.split(",")), mots_cles[:120])
    return mots_cles
