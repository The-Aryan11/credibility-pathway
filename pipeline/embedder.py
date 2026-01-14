import os
import requests
import numpy as np
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

headers = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}

print("✅ Hugging Face API embedder loaded!")

def get_embedding(text: str) -> list:
    """Get embedding from Hugging Face API (FREE, no local RAM)"""
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": text[:500], "options": {"wait_for_model": True}}
        )
        
        if response.status_code == 200:
            embedding = response.json()
            # Handle nested list response
            if isinstance(embedding, list) and len(embedding) > 0:
                if isinstance(embedding[0], list):
                    # Average pooling for sentence embedding
                    embedding = np.mean(embedding, axis=0).tolist()
                return embedding
        else:
            print(f"⚠️ API error: {response.status_code}")
            return [0.0] * 384
            
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return [0.0] * 384

def get_embeddings(texts: list) -> list:
    """Get embeddings for multiple texts"""
    embeddings = []
    for text in texts:
        emb = get_embedding(text)
        embeddings.append(emb)
    return embeddings

def compute_similarity(vec1: list, vec2: list) -> float:
    """Compute cosine similarity"""
    try:
        a = np.array(vec1)
        b = np.array(vec2)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    except:
        return 0.0