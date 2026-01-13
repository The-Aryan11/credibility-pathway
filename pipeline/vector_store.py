import os
import json
from pipeline.embedder import get_embedding, get_embeddings
import numpy as np

# Simple in-memory vector store
class SimpleVectorStore:
    def __init__(self):
        self.documents = []  # List of {"text": ..., "embedding": ..., "metadata": ...}
        print("✅ Vector store initialized!")
    
    def add_document(self, text: str, metadata: dict = None):
        """Add a document to the store"""
        embedding = get_embedding(text[:1000])  # Limit text length
        self.documents.append({
            "text": text,
            "embedding": embedding,
            "metadata": metadata or {}
        })
        print(f"📄 Added document ({len(self.documents)} total)")
    
    def add_documents(self, texts: list, metadatas: list = None):
        """Add multiple documents"""
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas else {}
            self.add_document(text, metadata)
    
    def search(self, query: str, top_k: int = 5) -> list:
        """Search for similar documents"""
        if not self.documents:
            return []
        
        query_embedding = get_embedding(query)
        
        # Calculate cosine similarity
        results = []
        for doc in self.documents:
            similarity = self._cosine_similarity(query_embedding, doc["embedding"])
            results.append({
                "text": doc["text"],
                "metadata": doc["metadata"],
                "score": similarity
            })
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def _cosine_similarity(self, a: list, b: list) -> float:
        """Calculate cosine similarity between two vectors"""
        a = np.array(a)
        b = np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    def load_from_folder(self, folder: str = "data/articles"):
        """Load all text files from a folder"""
        if not os.path.exists(folder):
            print(f"⚠️ Folder not found: {folder}")
            return
        
        files = [f for f in os.listdir(folder) if f.endswith('.txt')]
        print(f"📂 Found {len(files)} files in {folder}")
        
        for filename in files:
            filepath = os.path.join(folder, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                self.add_document(text, {"filename": filename})
    
    def get_stats(self) -> dict:
        """Get store statistics"""
        return {
            "total_documents": len(self.documents),
            "last_updated": "now"
        }

# Global instance
vector_store = SimpleVectorStore()