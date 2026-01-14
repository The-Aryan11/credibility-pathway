"""
Enhanced Fact Checker with Source Credibility, Confidence Intervals, Related Claims
"""
import os
from groq import Groq
from dotenv import load_dotenv
import json
import random

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY not found!")
else:
    print("✅ GROQ API Key loaded!")

groq = Groq(api_key=GROQ_API_KEY)

# ============ FEATURE 1: SOURCE CREDIBILITY ============
SOURCE_CREDIBILITY = {
    # Tier 1: Very High (90-100)
    "reuters": 95, "associated press": 95, "ap": 95, "bbc": 92,
    "nature": 98, "science": 98, "pubmed": 96, "who": 95, "cdc": 95,
    "new york times": 88, "washington post": 88, "the guardian": 87,
    
    # Tier 2: High (75-89)
    "npr": 85, "pbs": 85, "economist": 84, "financial times": 84,
    "wall street journal": 82, "time": 80, "newsweek": 78,
    
    # Tier 3: Medium (50-74)
    "cnn": 70, "fox news": 62, "msnbc": 68, "huffpost": 60,
    "buzzfeed news": 58, "daily mail": 52, "new york post": 55,
    
    # Tier 4: Low (25-49)
    "breitbart": 35, "infowars": 15, "naturalnews": 18,
    "social media": 30, "facebook": 35, "twitter": 35, "whatsapp": 25,
    "unknown": 40, "blog": 35, "reddit": 40
}

def get_source_credibility(source_name: str) -> dict:
    """Get credibility score for a source"""
    if not source_name:
        return {"score": 40, "level": "Unknown", "color": "gray", "name": "Unknown"}
    
    source_lower = source_name.lower()
    
    for key, score in SOURCE_CREDIBILITY.items():
        if key in source_lower:
            if score >= 85:
                level, color = "Very High", "green"
            elif score >= 70:
                level, color = "High", "lightgreen"
            elif score >= 50:
                level, color = "Medium", "orange"
            else:
                level, color = "Low", "red"
            
            return {"score": score, "level": level, "color": color, "name": source_name}
    
    return {"score": 45, "level": "Unknown", "color": "gray", "name": source_name}


# ============ MAIN ANALYSIS FUNCTION ============
def analyze_claim(claim: str, context: str = "", language: str = "en") -> dict:
    """
    Analyze a claim with:
    - Credibility score
    - Confidence intervals (Feature 7)
    - Related claims (Feature 8)
    - Geographic relevance (Feature 16)
    """
    try:
        print(f"🔍 Analyzing: {claim[:50]}...")
        
        messages = [
            {
                "role": "system",
                "content": """You are a fact-checker. Analyze the claim and return JSON:
{
    "score": 0-100,
    "confidence_low": number (lower bound, score minus 5-15),
    "confidence_high": number (upper bound, score plus 5-15),
    "category": "HEALTH|POLITICS|SCIENCE|TECHNOLOGY|FINANCE|SPORTS|ENTERTAINMENT|OTHER",
    "verdict": "TRUE|FALSE|MISLEADING|UNVERIFIED|PARTIALLY_TRUE",
    "reasoning": "2-3 sentence explanation",
    "key_evidence": ["evidence point 1", "evidence point 2", "evidence point 3"],
    "related_claims": ["related claim 1", "related claim 2", "related claim 3"],
    "geographic_relevance": ["country1", "country2"],
    "timeline_note": "When this claim emerged or became relevant"
}

Score guide:
- 0-20: Definitely false / Dangerous misinformation
- 21-40: Likely false / Misleading
- 41-60: Uncertain / Needs verification
- 61-80: Likely true
- 81-100: Verified true

For confidence_low and confidence_high:
- If very certain: range of 10 points (e.g., 75-85)
- If uncertain: range of 20-30 points (e.g., 40-70)"""
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
        
        # Ensure all fields exist
        score = result.get("score", 50)
        
        # Feature 7: Confidence Intervals
        if "confidence_low" not in result:
            uncertainty = random.randint(8, 15)
            result["confidence_low"] = max(0, score - uncertainty)
        if "confidence_high" not in result:
            uncertainty = random.randint(8, 15)
            result["confidence_high"] = min(100, score + uncertainty)
        
        # Feature 8: Related Claims
        result.setdefault("related_claims", [])
        
        # Feature 16: Geographic Relevance
        result.setdefault("geographic_relevance", ["Global"])
        
        # Other defaults
        result.setdefault("category", "OTHER")
        result.setdefault("verdict", "UNVERIFIED")
        result.setdefault("reasoning", "Analysis complete.")
        result.setdefault("key_evidence", [])
        result.setdefault("timeline_note", "Recent")
        
        print(f"✅ Score: {score}% (Confidence: {result['confidence_low']}-{result['confidence_high']}%)")
        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "score": 50,
            "confidence_low": 35,
            "confidence_high": 65,
            "category": "OTHER",
            "verdict": "UNVERIFIED",
            "reasoning": f"Analysis error: {str(e)}",
            "key_evidence": [],
            "related_claims": [],
            "geographic_relevance": ["Unknown"],
            "timeline_note": "Unknown"
        }


# ============ FEATURE 8: GET RELATED CLAIMS ============
def get_related_claims(claim: str, category: str) -> list:
    """Generate related claims people might want to check"""
    try:
        response = groq.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": 'Generate 3 related claims. Return JSON: {"claims": ["claim1", "claim2", "claim3"]}'
                },
                {
                    "role": "user",
                    "content": f"Original: {claim}\nCategory: {category}"
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("claims", result.get("related_claims", []))
    
    except Exception as e:
        print(f"❌ Related claims error: {e}")
        return []