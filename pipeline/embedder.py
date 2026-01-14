"""
Lightweight Embeddings using HuggingFace FREE API
Uses 0MB RAM - Pure Python Math
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY", "")
API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

headers = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}

def get_embedding(text: str) -> list:
    """Get embedding from HuggingFace API"""
    if not HF_API_KEY: return _fallback_embedding(text)
    
    try:
        response = requests.post(
            API_URL, headers=headers,
            json={"inputs": text[:500], "options": {"wait_for_model": True}}, timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            # Handle API list format
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], list): 
                    # Manual mean pooling without numpy
                    dim = len(data[0])
                    avg = [sum(x)/len(data) for x in zip(*data)]
                    return avg
                return data
        return _fallback_embedding(text)
    except:
        return _fallback_embedding(text)

def _fallback_embedding(text: str) -> list:
    """Zero-RAM fallback"""
    return [0.0] * 384

def compute_similarity(vec1: list, vec2: list) -> float:
    """Compute cosine similarity using Pure Python (No Numpy)"""
    try:
        # Manual dot product
        dot = sum(a * b for a, b in zip(vec1, vec2))
        # Manual magnitude
        norm_a = sum(a * a for a in vec1) ** 0.5
        norm_b = sum(b * b for b in vec2) ** 0.5
        
        if norm_a == 0 or norm_b == 0: return 0.0
        return dot / (norm_a * norm_b)
    except:
        return 0.0