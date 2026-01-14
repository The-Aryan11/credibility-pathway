"""
Multi-language Support using FREE Google Translate
"""
from deep_translator import GoogleTranslator

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
    "ar": "Arabic",
    "zh-CN": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ru": "Russian",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali"
}

def translate_text(text: str, target_lang: str) -> str:
    """Translate text to target language (FREE)"""
    if not text or target_lang == "en":
        return text
    
    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def translate_to_english(text: str) -> str:
    """Translate any language to English"""
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return text