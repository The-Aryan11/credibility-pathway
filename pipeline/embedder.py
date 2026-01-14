from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

print("✅ Lightweight TF-IDF embedder loaded!")

# Global vectorizer (lightweight, no GPU needed)
vectorizer = TfidfVectorizer(
    max_features=1000,
    stop_words='english',
    ngram_range=(1, 2)
)

# Store for fitted state
_is_fitted = False
_corpus = []

def fit_vectorizer(texts: list):
    """Fit the vectorizer on a corpus of texts"""
    global _is_fitted, _corpus
    if texts:
        _corpus = texts
        vectorizer.fit(texts)
        _is_fitted = True
        print(f"✅ Vectorizer fitted on {len(texts)} documents")

def get_embedding(text: str) -> list:
    """Convert text to TF-IDF vector"""
    global _is_fitted
    
    if not _is_fitted:
        # Fit on single document if not fitted
        vectorizer.fit([text])
        _is_fitted = True
    
    try:
        vector = vectorizer.transform([text]).toarray()[0]
        return vector.tolist()
    except:
        # Return zero vector if error
        return [0.0] * 1000

def get_embeddings(texts: list) -> list:
    """Convert multiple texts to TF-IDF vectors"""
    global _is_fitted
    
    if not _is_fitted:
        vectorizer.fit(texts)
        _is_fitted = True
    
    try:
        vectors = vectorizer.transform(texts).toarray()
        return vectors.tolist()
    except:
        return [[0.0] * 1000 for _ in texts]

def compute_similarity(text1: str, text2: str) -> float:
    """Compute cosine similarity between two texts"""
    try:
        vec1 = get_embedding(text1)
        vec2 = get_embedding(text2)
        
        # Cosine similarity
        dot = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot / (norm1 * norm2))
    except:
        return 0.0