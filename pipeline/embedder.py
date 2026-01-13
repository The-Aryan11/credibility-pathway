from sentence_transformers import SentenceTransformer

# Load free embedding model (runs locally, no API key needed)
print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Embedding model loaded!")

def get_embeddings(texts: list) -> list:
    """Convert list of texts to vector embeddings"""
    embeddings = model.encode(texts)
    return embeddings.tolist()

def get_embedding(text: str) -> list:
    """Convert single text to vector embedding"""
    embedding = model.encode([text])[0]
    return embedding.tolist()