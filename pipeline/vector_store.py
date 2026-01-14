import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SimpleVectorStore:
    def __init__(self):
        self.documents = []  # List of {"text": ..., "metadata": ...}
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.vectors = None
        print("✅ Lightweight vector store initialized!")
    
    def add_document(self, text: str, metadata: dict = None):
        """Add a document to the store"""
        self.documents.append({
            "text": text[:2000],  # Limit text length to save memory
            "metadata": metadata or {}
        })
        self._rebuild_index()
        print(f"📄 Added document ({len(self.documents)} total)")
    
    def add_documents(self, texts: list, metadatas: list = None):
        """Add multiple documents"""
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas else {}
            self.documents.append({
                "text": text[:2000],
                "metadata": metadata
            })
        self._rebuild_index()
        print(f"📄 Added {len(texts)} documents ({len(self.documents)} total)")
    
    def _rebuild_index(self):
        """Rebuild the TF-IDF index"""
        if not self.documents:
            self.vectors = None
            return
        
        texts = [doc["text"] for doc in self.documents]
        try:
            self.vectors = self.vectorizer.fit_transform(texts)
        except:
            self.vectors = None
    
    def search(self, query: str, top_k: int = 5) -> list:
        """Search for similar documents"""
        if not self.documents or self.vectors is None:
            return []
        
        try:
            query_vec = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, self.vectors)[0]
            
            # Get top k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:
                    results.append({
                        "text": self.documents[idx]["text"],
                        "metadata": self.documents[idx]["metadata"],
                        "score": float(similarities[idx])
                    })
            
            return results
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
        
        texts = []
        metadatas = []
        
        for filename in files[:50]:  # Limit to 50 files to save memory
            filepath = os.path.join(folder, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()[:2000]  # Limit text length
                    texts.append(text)
                    metadatas.append({"filename": filename})
            except:
                pass
        
        if texts:
            self.add_documents(texts, metadatas)
    
    def get_stats(self) -> dict:
        """Get store statistics"""
        return {
            "total_documents": len(self.documents),
            "last_updated": "now"
        }
    
    def clear(self):
        """Clear all documents"""
        self.documents = []
        self.vectors = None
        print("🗑️ Vector store cleared")

# Global instance
vector_store = SimpleVectorStore()