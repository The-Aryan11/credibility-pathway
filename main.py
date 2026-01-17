from fastapi import FastAPI
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

# --- CONFIG ---
DATA_FOLDER = "./data/articles"
os.makedirs(DATA_FOLDER, exist_ok=True)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- PATHWAY SETUP ---
embedder = SentenceTransformerEmbedder(model="all-MiniLM-L6-v2")
documents = pw.io.fs.read(path=DATA_FOLDER, format="plaintext", mode="streaming", with_metadata=True)
vector_server = VectorStoreServer(documents, embedder=embedder, splitter=TokenCountSplitter(max_tokens=400))

def start_pathway():
    vector_server.run_server(host="0.0.0.0", port=8765, threaded=False)

t = threading.Thread(target=start_pathway, daemon=True)
t.start()

# --- ENDPOINTS ---
class Payload(BaseModel):
    text: str = ""
    source: str = ""
    claim: str = ""

@app.get("/")
def health(): return {"status": "active", "files": len(os.listdir(DATA_FOLDER))}

@app.post("/ingest")
def ingest(req: Payload):
    import uuid
    filename = f"{DATA_FOLDER}/{uuid.uuid4().hex}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"SOURCE: {req.source}\n\n{req.text}")
    return {"status": "indexed"}

@app.post("/analyze")
def analyze(req: Payload):
    # 1. Retrieve
    try:
        import requests
        resp = requests.post("http://0.0.0.0:8765/v1/retrieve", json={"query": req.claim, "k": 4}).json()
        context = "\n".join([d['text'] for d in resp])
        sources = [d['metadata'].get('path', 'Unknown') for d in resp]
    except:
        context = ""
        sources = []

    # 2. Analyze
    groq = Groq(api_key=GROQ_API_KEY)
    prompt = f"""
    Analyze this claim based on the context. Return JSON:
    {{
        "score": 0-100,
        "verdict": "TRUE|FALSE|MISLEADING|UNVERIFIED",
        "reasoning": "Explanation",
        "category": "HEALTH|POLITICS|SCIENCE|FINANCE|OTHER",
        "key_evidence": ["point 1", "point 2"]
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
        res = json.loads(chat.choices[0].message.content)
        res['sources'] = sources
        return res
    except Exception as e:
        return {"score": 50, "verdict": "ERROR", "reasoning": str(e), "category": "ERROR"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)