"""
Backend Groq — gratuit, rapide (~1-3s), pas de GPU requis.

Inscription : https://console.groq.com  (gratuit, sans CB)
Modèles disponibles : llama-3.1-70b-versatile, mixtral-8x7b-32768, gemma2-9b-it

Usage : dans main.py, remplacer
    from llm.prompt import analyser_url
par
    from llm.groq_api import analyser_url

Nécessite : pip install groq
            export GROQ_API_KEY=gsk_...
"""
import logging
import os

from groq import Groq

from config import MAX_TEXT_CHARS
from llm.prompt import _PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

MODEL = "llama-3.1-70b-versatile"


_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("Variable GROQ_API_KEY non définie.")
        _client = Groq(api_key=api_key)
    return _client


def analyser_url(titre: str, texte_complet: str) -> str:
    entete = f"Titre : {titre}\n\n" if titre else ""
    prompt = _PROMPT_TEMPLATE.format(texte=(entete + texte_complet)[:MAX_TEXT_CHARS])

    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.2,
    )

    resume = response.choices[0].message.content.strip()
    logger.debug("Résumé Groq généré (%d caractères)", len(resume))
    return resume
