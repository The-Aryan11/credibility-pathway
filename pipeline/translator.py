import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SUPPORTED_LANGUAGES = {
    "en": "English", "es": "Spanish", "hi": "Hindi", 
    "fr": "French", "de": "German", "zh": "Chinese"
}

def translate_text(text: str, target_lang: str) -> str:
    """Translate using Groq LLM (High quality, 0 RAM)"""
    if not text or target_lang == "en":
        return text
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": f"Translate this text to {SUPPORTED_LANGUAGES.get(target_lang, 'English')}. Return ONLY the translation, nothing else."},
                {"role": "user", "content": text}
            ],
            temperature=0.1
        )
        return completion.choices[0].message.content.strip()
    except:
        return text