import logging
from typing import Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline, Pipeline

from config import LLM_DEVICE, LLM_MAX_NEW_TOKENS, LLM_MODEL_NAME, LLM_TEMPERATURE

logger = logging.getLogger(__name__)

_pipeline_instance: Optional[Pipeline] = None

_bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
)


def get_pipeline() -> Pipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        logger.info("Chargement du modèle %s en 4-bit sur GPU %d …", LLM_MODEL_NAME, LLM_DEVICE)
        tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(
            LLM_MODEL_NAME,
            quantization_config=_bnb_config,
            device_map="auto",
        )
        _pipeline_instance = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
        )
        logger.info("Modèle chargé (~4 Go VRAM).")
    return _pipeline_instance


def generer_texte(prompt: str, max_new_tokens: int, temperature: float) -> str:
    pipe = get_pipeline()
    messages = [{"role": "user", "content": prompt}]
    resultat = pipe(
        messages,
        max_new_tokens=max_new_tokens,
        do_sample=temperature > 0,
        temperature=temperature if temperature > 0 else None,
        pad_token_id=pipe.tokenizer.eos_token_id,
    )
    return resultat[0]["generated_text"][-1]["content"].strip()
