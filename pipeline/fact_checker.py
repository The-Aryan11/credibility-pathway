import os
from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY not found in .env file!")
else:
    print("✅ GROQ API Key loaded!")

groq = Groq(api_key=GROQ_API_KEY)

def analyze_claim(claim: str, context: str = "") -> dict:
    """Analyze a claim using Groq LLM"""
    try:
        print(f"🔍 Analyzing: {claim[:50]}...")
        
        messages = [
            {
                "role": "system",
                "content": """You are a fact-checker. Analyze the claim and return JSON:
{
    "score": 0-100,
    "category": "HEALTH|POLITICS|SCIENCE|FINANCE|OTHER",
    "verdict": "TRUE|FALSE|MISLEADING|UNVERIFIED",
    "reasoning": "Brief explanation",
    "key_evidence": ["point 1", "point 2"]
}

Score guide:
- 0-20: Definitely false
- 21-40: Likely false
- 41-60: Uncertain
- 61-80: Likely true
- 81-100: Definitely true"""
            },
            {
                "role": "user",
                "content": f"CLAIM: {claim}\n\nCONTEXT:\n{context}" if context else f"CLAIM: {claim}"
            }
        ]

        response = groq.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.3
        )

        result = json.loads(response.choices[0].message.content)
        print(f"✅ Analysis complete! Score: {result.get('score', 'N/A')}%")
        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "score": 50,
            "category": "OTHER",
            "verdict": "UNVERIFIED",
            "reasoning": f"Analysis failed: {str(e)}",
            "key_evidence": []
        }