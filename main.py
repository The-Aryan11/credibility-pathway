"""
BACKEND API - Runs on Hugging Face (16GB RAM)
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

# --- 1. HEAVY EMBEDDING MODEL (Runs on HF GPU/CPU) ---
print("🚀 Loading Heavy Embedding Model...")
embedder = SentenceTransformerEmbedder(model="all-MiniLM-L6-v2")

# --- 2. PATHWAY STREAMING PIPELINE ---
print("🌊 Initializing Pathway Stream...")
documents = pw.io.fs.read(
    path=DATA_FOLDER,
    format="plaintext",
    mode="streaming",
    with_metadata=True
)

splitter = TokenCountSplitter(max_tokens=400)
vector_server = VectorStoreServer(documents, embedder=embedder, splitter=splitter)

# Run Pathway in background thread
def start_pathway():
    # Run internal vector server on port 8765
    vector_server.run_server(host="0.0.0.0", port=8765, threaded=False)

t = threading.Thread(target=start_pathway, daemon=True)
t.start()

# --- API ENDPOINTS ---

class IngestRequest(BaseModel):
    text: str
    source: str

class AnalyzeRequest(BaseModel):
    claim: str

@app.get("/")
def health():
    return {"status": "active", "platform": "Hugging Face"}

@app.post("/ingest")
def ingest(req: IngestRequest):
    import uuid
    filename = f"{DATA_FOLDER}/doc_{uuid.uuid4().hex}.txt"
    content = f"SOURCE: {req.source}\nDATE: {datetime.now()}\n\n{req.text}"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return {"status": "ingested", "file": filename}

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    # 1. Retrieve Context from Pathway (Real-time RAG)
    import requests
    try:
        # Query local Pathway server
        rag_response = requests.post(
            "http://0.0.0.0:8765/v1/retrieve",
            json={"query": req.claim, "k": 5},
            timeout=5
        ).json()
        docs = [d['text'] for d in rag_response]
        sources = list(set([d.get('metadata', {}).get('path', 'Unknown') for d in rag_response]))
        context = "\n\n".join(docs)
    except Exception as e:
        print(f"RAG Error: {e}")
        context = ""
        sources = []

    # 2. Advanced Analysis with Groq
    groq = Groq(api_key=GROQ_API_KEY)
    prompt = f"""
    Analyze this claim using the provided context.
    Return JSON:
    {{
        "score": 0-100,
        "verdict": "TRUE|FALSE|MISLEADING|UNVERIFIED",
        "reasoning": "Detailed explanation",
        "category": "HEALTH|POLITICS|SCIENCE|FINANCE|OTHER",
        "key_evidence": ["point 1", "point 2"],
        "confidence_score": 0-100,
        "sentiment": "positive|negative|neutral"
    }}
    
    CLAIM: {req.claim}
    CONTEXT: {context}
    """
    
    try:
        chat = groq.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": "You are an expert fact-checker. Return JSON only."}, 
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        result = json.loads(chat.choices[0].message.content)
        result['sources'] = sources
        return result
    except Exception as e:
        return {"error": str(e), "score": 50, "verdict": "ERROR"}

if __name__ == "__main__":
    # Hugging Face Spaces expects port 7860
    uvicorn.run(app, host="0.0.0.0", port=7860)