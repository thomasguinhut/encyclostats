"""
Backend Claude API (Anthropic) — alternative rapide à Mistral local.

Usage : dans main.py, remplacer
    from llm.prompt import analyser_url
par
    from llm.claude_api import analyser_url

Nécessite : pip install anthropic
            export ANTHROPIC_API_KEY=sk-ant-...
"""
import logging
import os

import anthropic

from config import MAX_TEXT_CHARS
from llm.prompt import _PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

MODEL = "claude-haiku-4-5-20251001"   # rapide et peu coûteux ; passer à claude-sonnet-4-6 pour plus de qualité

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError("Variable ANTHROPIC_API_KEY non définie.")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def analyser_url(titre: str, texte_complet: str) -> str:
    entete = f"Titre : {titre}\n\n" if titre else ""
    prompt = _PROMPT_TEMPLATE.format(texte=(entete + texte_complet)[:MAX_TEXT_CHARS])

    message = _get_client().messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    resume = message.content[0].text.strip()
    logger.debug("Résumé Claude généré (%d caractères)", len(resume))
    return resume
