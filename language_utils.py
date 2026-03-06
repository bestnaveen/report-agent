from config import MULTILINGUAL_ENABLED, DEFAULT_LANGUAGE

LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "zh-cn": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "pt": "Portuguese",
    "ru": "Russian",
    "it": "Italian",
    "nl": "Dutch",
    "tr": "Turkish",
    "th": "Thai",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "ur": "Urdu",
    "pl": "Polish",
    "uk": "Ukrainian",
    "vi": "Vietnamese",
    "id": "Indonesian",
    "ms": "Malay",
    "fa": "Persian",
    "he": "Hebrew",
    "sv": "Swedish",
    "da": "Danish",
    "fi": "Finnish",
    "no": "Norwegian",
    "cs": "Czech",
    "ro": "Romanian",
    "hu": "Hungarian",
}

# Languages that use RTL text direction
RTL_LANGUAGES = {"ar", "he", "fa", "ur"}


def detect_language(text: str) -> dict:
    """
    Detect language of given text.

    Returns:
        {"code": "hi", "name": "Hindi", "confidence": 0.95}
    """
    if not MULTILINGUAL_ENABLED or not text or len(text.strip()) < 3:
        return {"code": DEFAULT_LANGUAGE, "name": LANGUAGE_MAP.get(DEFAULT_LANGUAGE, "English"), "confidence": 1.0}

    try:
        from langdetect import detect_langs
        results = detect_langs(text)
        if results:
            top = results[0]
            code = top.lang
            # Normalize zh variants
            if code.startswith("zh"):
                code = "zh"
            name = LANGUAGE_MAP.get(code, code.upper())
            return {"code": code, "name": name, "confidence": round(top.prob, 2)}
    except Exception:
        pass

    return {"code": DEFAULT_LANGUAGE, "name": LANGUAGE_MAP.get(DEFAULT_LANGUAGE, "English"), "confidence": 0.0}


def get_language_instruction(lang_code: str) -> str:
    """
    Generate a strong language instruction for the LLM prompt.
    Returns empty string for English (default).
    """
    if lang_code == "en" or lang_code == DEFAULT_LANGUAGE:
        return "Respond in clear English."

    lang_name = LANGUAGE_MAP.get(lang_code, lang_code.upper())

    return (
        f"CRITICAL LANGUAGE REQUIREMENT: The user is writing in {lang_name}. "
        f"You MUST respond ENTIRELY in {lang_name}. "
        f"Every single word of your response MUST be in {lang_name}. "
        f"Do NOT use English words unless they are technical terms with no {lang_name} equivalent. "
        f"Do NOT include English translations in parentheses. "
        f"Write all explanations, labels, and conclusions in {lang_name}. "
        f"Chart titles and axis labels may remain in English for readability."
    )


def get_supported_languages() -> list[dict]:
    """Return list of supported language dicts for display."""
    return [{"code": code, "name": name} for code, name in sorted(LANGUAGE_MAP.items(), key=lambda x: x[1])]


def get_language_flag(lang_code: str) -> str:
    """Return a representative emoji for the language (best-effort)."""
    flags = {
        "en": "🇬🇧",
        "hi": "🇮🇳",
        "es": "🇪🇸",
        "fr": "🇫🇷",
        "de": "🇩🇪",
        "zh": "🇨🇳",
        "zh-cn": "🇨🇳",
        "zh-tw": "🇹🇼",
        "ja": "🇯🇵",
        "ko": "🇰🇷",
        "ar": "🇸🇦",
        "pt": "🇧🇷",
        "ru": "🇷🇺",
        "it": "🇮🇹",
        "nl": "🇳🇱",
        "tr": "🇹🇷",
        "th": "🇹🇭",
        "bn": "🇧🇩",
        "ta": "🇱🇰",
        "te": "🇮🇳",
        "mr": "🇮🇳",
        "gu": "🇮🇳",
        "ur": "🇵🇰",
        "pl": "🇵🇱",
        "uk": "🇺🇦",
        "vi": "🇻🇳",
        "id": "🇮🇩",
        "ms": "🇲🇾",
        "fa": "🇮🇷",
        "he": "🇮🇱",
        "sv": "🇸🇪",
        "da": "🇩🇰",
        "fi": "🇫🇮",
        "no": "🇳🇴",
    }
    return flags.get(lang_code, "🌐")
