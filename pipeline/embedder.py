import os
import requests
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# HuggingFace API (Free & High Quality)
HF_API_KEY = os.getenv("HF_API_KEY")
API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

def get_embedding(text: str) -> list:
    """Get embedding from API (Uses 0MB RAM)"""
    if not HF_API_KEY:
        print("⚠️ HF_API_KEY missing!")
        return [0.0] * 384
        
    try:
        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={"inputs": text[:500], "options": {"wait_for_model": True}},
            timeout=5
        )
        data = response.json()
        
        # Handle API response formats
        if isinstance(data, list):
            if isinstance(data[0], list): 
                # Mean pooling if it returns token embeddings
                return np.mean(data, axis=0).tolist()
            return data
        return [0.0] * 384
    except:
        return [0.0] * 384

def get_embeddings(texts: list) -> list:
    return [get_embedding(t) for t in texts]