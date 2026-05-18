"""
Singleton pour le pipeline Mistral-7B-v0.1.
Le modèle est chargé une seule fois au premier appel de get_pipeline().
"""
import logging
from typing import Optional

from transformers import pipeline, Pipeline

from config import LLM_DEVICE, LLM_MODEL_NAME

logger = logging.getLogger(__name__)

_pipeline_instance: Optional[Pipeline] = None


def get_pipeline() -> Pipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        logger.info("Chargement du modèle %s sur GPU %d …", LLM_MODEL_NAME, LLM_DEVICE)
        _pipeline_instance = pipeline(
            "text-generation",
            model=LLM_MODEL_NAME,
            device=LLM_DEVICE,
            # Chargement en demi-précision pour tenir sur un GPU de 16 Go
            torch_dtype="auto",
            trust_remote_code=False,
        )
        logger.info("Modèle chargé.")
    return _pipeline_instance


def generer_texte(prompt: str, max_new_tokens: int, temperature: float) -> str:
    """Envoie un prompt au pipeline et retourne uniquement le texte généré."""
    pipe = get_pipeline()
    resultat = pipe(
        prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=temperature > 0,
        return_full_text=False,   # on ne veut que la complétion, pas le prompt répété
        pad_token_id=pipe.tokenizer.eos_token_id,
    )
    return resultat[0]["generated_text"].strip()
