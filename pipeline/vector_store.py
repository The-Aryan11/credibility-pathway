import os
import numpy as np
from pipeline.embedder import get_embedding, compute_similarity

class SimpleVectorStore:
    def __init__(self):
        self.documents = []  # List of {"text": ..., "embedding": ..., "metadata": ...}
        print("✅ Vector store initialized (using HuggingFace API)!")
    
    def add_document(self, text: str, metadata: dict = None):
        """Add a document to the store"""
        # Get embedding from HuggingFace API (no local RAM used)
        embedding = get_embedding(text[:1000])
        
        self.documents.append({
            "text": text[:2000],
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
        """Search for similar documents using semantic similarity"""
        if not self.documents:
            return []
        
        try:
            # Get query embedding from API
            query_embedding = get_embedding(query)
            
            # Calculate similarities
            results = []
            for doc in self.documents:
                similarity = compute_similarity(query_embedding, doc["embedding"])
                results.append({
                    "text": doc["text"],
                    "metadata": doc["metadata"],
                    "score": similarity
                })
            
            # Sort by similarity
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def load_from_folder(self, folder: str = "data/articles"):
        """Load all text files from a folder"""
        if not os.path.exists(folder):
            print(f"⚠️ Folder not found: {folder}")
            return
        
        files = [f for f in os.listdir(folder) if f.endswith('.txt')]
        print(f"📂 Found {len(files)} files in {folder}")
        
        # Limit to prevent API rate limits
        for filename in files[:20]:
            filepath = os.path.join(folder, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
                    self.add_document(text, {"filename": filename})
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    def get_stats(self) -> dict:
        """Get store statistics"""
        return {
            "total_documents": len(self.documents),
            "last_updated": "now"
        }
    
    def clear(self):
        """Clear all documents"""
        self.documents = []
        print("🗑️ Vector store cleared")

# Global instance
vector_store = SimpleVectorStore()