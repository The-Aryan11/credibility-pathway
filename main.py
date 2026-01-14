"""
BACKEND API - Hugging Face (16GB RAM)
Implements Pathway Streaming + RAG + LLM Analysis
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pathway as pw
from pathway.xpacks.llm.vector_store import VectorStoreServer
from pathway.xpacks.llm.embedders import SentenceTransformerEmbedder
from pathway.xpacks.llm.splitters import TokenCountSplitter
import uvicorn
import threading
import os
import json
from groq import Groq
from datetime import datetime

app = FastAPI()

# --- CONFIGURATION ---
DATA_FOLDER = "./data/articles"
os.makedirs(DATA_FOLDER, exist_ok=True)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- PATHWAY SETUP ---
print("🚀 Loading Embeddings...")
embedder = SentenceTransformerEmbedder(model="all-MiniLM-L6-v2")

print("🌊 Starting Pathway Stream...")
documents = pw.io.fs.read(
    path=DATA_FOLDER, format="plaintext", mode="streaming", with_metadata=True
)
splitter = TokenCountSplitter(max_tokens=400)
vector_server = VectorStoreServer(documents, embedder=embedder, splitter=splitter)

def start_pathway():
    vector_server.run_server(host="0.0.0.0", port=8765, threaded=False)

t = threading.Thread(target=start_pathway, daemon=True)
t.start()

# --- HELPERS ---
def rate_source(source_name):
    high = ['reuters', 'ap', 'bbc', 'nature', 'science', 'gov', 'edu', 'who', 'cdc']
    low = ['blog', 'social', 'opinion', 'unknown', 'twitter', 'reddit']
    s = source_name.lower()
    if any(x in s for x in high): return "High"
    if any(x in s for x in low): return "Low"
    return "Medium"

# --- ENDPOINTS ---
class IngestRequest(BaseModel):
    text: str
    source: str

class AnalyzeRequest(BaseModel):
    claim: str

@app.get("/")
def health(): return {"status": "active", "backend": "Pathway+HF"}

@app.post("/ingest")
def ingest(req: IngestRequest):
    import uuid
    filename = f"{DATA_FOLDER}/doc_{uuid.uuid4().hex}.txt"
    content = f"SOURCE: {req.source}\nDATE: {datetime.now()}\n\n{req.text}"
    with open(filename, "w", encoding="utf-8") as f: f.write(content)
    return {"status": "ingested", "file": filename}

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    # 1. RAG Retrieval
    import requests
    try:
        rag_res = requests.post("http://0.0.0.0:8765/v1/retrieve", json={"query": req.claim, "k": 4}).json()
        docs = [d['text'] for d in rag_res]
        sources = []
        for d in rag_res:
            raw = d.get('text', '')
            src = "Unknown"
            if "SOURCE:" in raw[:50]:
                src = raw.split("\n")[0].replace("SOURCE:", "").strip()
            sources.append({"name": src, "credibility": rate_source(src)})
        context = "\n---\n".join(docs)
    except:
        context = ""
        sources = []

    # 2. LLM Analysis
    groq = Groq(api_key=GROQ_API_KEY)
    prompt = f"""
    Analyze this claim. Return JSON:
    {{
        "score": 0-100,
        "verdict": "TRUE|FALSE|MISLEADING|UNVERIFIED",
        "reasoning": "Explanation",
        "category": "HEALTH|POLITICS|SCIENCE|FINANCE|OTHER",
        "key_evidence": ["point 1", "point 2"],
        "confidence_score": 0-100,
        "related_claims": ["claim 1", "claim 2"],
        "sentiment": "Positive|Negative|Neutral"
    }}
    
    CLAIM: {req.claim}
    CONTEXT: {context}
    """
    
    try:
        chat = groq.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        result = json.loads(chat.choices[0].message.content)
    except:
        result = {"score": 50, "verdict": "ERROR", "reasoning": "AI Error"}

    result['sources'] = sources
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)