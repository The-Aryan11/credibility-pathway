import numpy as np
from pipeline.embedder import get_embedding

class SimpleVectorStore:
    def __init__(self):
        self.documents = []  # Stores text and embedding
        print("✅ Vector Store Initialized")

    def add_document(self, text, metadata=None):
        vector = get_embedding(text)
        self.documents.append({
            "text": text,
            "vector": vector,
            "metadata": metadata or {}
        })

    def search(self, query, top_k=3):
        if not self.documents: return []
        
        query_vec = get_embedding(query)
        
        # Calculate Cosine Similarity manually (Lightweight)
        results = []
        for doc in self.documents:
            vec = doc["vector"]
            # Dot product
            dot = sum(a*b for a,b in zip(query_vec, vec))
            # Magnitude (Norm)
            norm_q = sum(a*a for a in query_vec) ** 0.5
            norm_d = sum(b*b for b in vec) ** 0.5
            
            score = 0
            if norm_q * norm_d > 0:
                score = dot / (norm_q * norm_d)
                
            results.append({**doc, "score": score})
            
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def load_from_folder(self, folder="data/articles"):
        import os
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.endswith(".txt"):
                    try:
                        with open(f"{folder}/{f}", "r", encoding="utf-8") as file:
                            self.add_document(file.read(), {"source": "File"})
                    except: pass

    def get_stats(self):
        return {"total_documents": len(self.documents), "folder": "data/articles"}

vector_store = SimpleVectorStore()