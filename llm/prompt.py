import logging

from config import LLM_MAX_NEW_TOKENS, LLM_TEMPERATURE, MAX_TEXT_CHARS
from llm.model import generer_texte

logger = logging.getLogger(__name__)

_PROMPT_TEMPLATE = """\
Tu es un assistant spécialisé en statistiques publiques françaises.

Génère un résumé exhaustif de 600 mots de cette publication officielle.

Ce résumé servira à un moteur de recherche sémantique — plus il est dense et exhaustif, mieux c'est.

Retourne UNIQUEMENT le résumé, sans introduction, sans numérotation, sans explication.

Texte :
{texte}"""


def construire_prompt(texte: str) -> str:
    return _PROMPT_TEMPLATE.format(texte=texte[:MAX_TEXT_CHARS])


def analyser_url(titre: str, texte_complet: str) -> str:
    entete = f"Titre : {titre}\n\n" if titre else ""
    prompt = construire_prompt(entete + texte_complet)

    resume = generer_texte(
        prompt=prompt,
        max_new_tokens=LLM_MAX_NEW_TOKENS,
        temperature=LLM_TEMPERATURE,
    )

    logger.debug("Résumé généré (%d caractères)", len(resume))
    return resume
