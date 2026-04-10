"""
Translator — LibreTranslate with offline/LLM fallbacks.
Translates policy summaries into Hindi, Tamil, French, Spanish, Arabic.
"""
import logging
import os
from typing import Optional

logger = logging.getLogger("policylens.translator")

LIBRETRANSLATE_URL = os.getenv("LIBRETRANSLATE_URL", "http://localhost:5000")

SUPPORTED_LANGUAGES = {
    "en": "English", "hi": "Hindi", "ta": "Tamil",
    "fr": "French", "es": "Spanish", "ar": "Arabic",
    "kn": "Kannada", "te": "Telugu",
}


def translate_text(text: str, target_lang: str, source_lang: str = "en") -> str:
    """Translate text using service, offline, or LLM fallbacks."""
    if target_lang == source_lang or target_lang == "en":
        return text

    if target_lang not in SUPPORTED_LANGUAGES:
        logger.warning(f"Unsupported language: {target_lang}, returning original.")
        return text

    result = _libretranslate(text, source_lang, target_lang)
    if result:
        return result

    result = _argos_translate(text, source_lang, target_lang)
    if result:
        return result

    result = _llm_translate(text, source_lang, target_lang)
    if result:
        return result

    logger.warning(f"All translation methods failed for lang={target_lang}")
    return text


def _libretranslate(text: str, source: str, target: str) -> Optional[str]:
    """Call self-hosted LibreTranslate API."""
    try:
        import requests
        resp = requests.post(
            f"{LIBRETRANSLATE_URL}/translate",
            json={"q": text, "source": source, "target": target, "format": "text"},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("translatedText", "")
    except Exception as e:
        logger.debug(f"LibreTranslate error: {e}")
    return None


def _argos_translate(text: str, source: str, target: str) -> Optional[str]:
    """Fallback: Argos Translate (offline Python library)."""
    try:
        import argostranslate.package
        import argostranslate.translate

        installed = argostranslate.translate.get_installed_languages()
        source_lang = next((l for l in installed if l.code == source), None)
        target_lang = next((l for l in installed if l.code == target), None)

        if source_lang and target_lang:
            translation = source_lang.get_translation(target_lang)
            if translation:
                return translation.translate(text)
        logger.debug(f"Argos language pair {source}->{target} not installed.")
    except Exception as e:
        logger.debug(f"Argos translate error: {e}")
    return None


def _llm_translate(text: str, source: str, target: str) -> Optional[str]:
    """Fallback: reuse the app's LLM stack for translation when services are unavailable."""
    try:
        from backend.services.llm_analyzer import _call_llm

        source_name = SUPPORTED_LANGUAGES.get(source, source)
        target_name = SUPPORTED_LANGUAGES.get(target, target)
        prompt = (
            f"Translate the following citizen policy summary from {source_name} to {target_name}. "
            "Preserve meaning, tone, brevity, and all numbers. "
            "Return only the translated text with no explanation, no markdown, and no quotes.\n\n"
            f"{text}"
        )
        response = _call_llm(prompt, max_tokens=400)
        if not response:
            return None

        cleaned = response.strip().strip('"').strip("'")
        if cleaned and cleaned.lower() != text.strip().lower():
            return cleaned
    except Exception as e:
        logger.debug(f"LLM translate error: {e}")
    return None


def translate_report_summary(summary: str, target_lang: str) -> str:
    """Translate the citizen-friendly summary."""
    return translate_text(summary[:2000], target_lang)


def get_supported_languages() -> dict:
    return SUPPORTED_LANGUAGES
