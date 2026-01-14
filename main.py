"""
BACKEND API - Hugging Face (16GB RAM)
Implements PRD 3.1, 3.2, 3.3 (Tracking, Evidence, Scoring)
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

# --- PRD 3.2: EVIDENCE ENGINE ---
# Using High-Quality Embeddings (Allowed on HF 16GB RAM)
print("🚀 Loading Evidence Engine (SentenceTransformers)...")
embedder = SentenceTransformerEmbedder(model="all-MiniLM-L6-v2")

# --- PRD 3.1: REAL-TIME TRACKING ---
# Pathway Streaming Mode
print("🌊 Initializing Pathway Stream...")
documents = pw.io.fs.read(
    path=DATA_FOLDER,
    format="plaintext",
    mode="streaming",
    with_metadata=True
)

splitter = TokenCountSplitter(max_tokens=400)
vector_server = VectorStoreServer(documents, embedder=embedder, splitter=splitter)

def start_pathway():
    vector_server.run_server(host="0.0.0.0", port=8765, threaded=False)

t = threading.Thread(target=start_pathway, daemon=True)
t.start()

# --- PRD 3.3.2: WEIGHTING LOGIC ---
def rate_source_credibility(source_name):
    # Implements PRD 3.2.1 Source ranking
    high = ['reuters', 'ap', 'bbc', 'nature', 'science', 'gov', 'edu', 'who', 'cdc']
    low = ['blog', 'social', 'opinion', 'unknown', 'twitter', 'reddit']
    s = source_name.lower()
    if any(x in s for x in high): return "High (10x Weight)"
    if any(x in s for x in low): return "Low (0.1x Weight)"
    return "Medium (5x Weight)"

# --- ENDPOINTS ---
class IngestRequest(BaseModel):
    text: str
    source: str

class AnalyzeRequest(BaseModel):
    claim: str
    profile: str = "Strict Science" # PRD 3.4.1

@app.get("/")
def health():
    return {"status": "active", "system": "Credibility Engine Backend"}

@app.post("/ingest")
def ingest(req: IngestRequest):
    import uuid
    # Saves to folder, Pathway automatically picks it up (Streaming)
    filename = f"{DATA_FOLDER}/doc_{uuid.uuid4().hex}.txt"
    content = f"SOURCE: {req.source}\nDATE: {datetime.now()}\n\n{req.text}"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return {"status": "ingested", "file": filename}

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    # 1. Retrieve Evidence (RAG)
    import requests
    try:
        rag_res = requests.post("http://0.0.0.0:8765/v1/retrieve", json={"query": req.claim, "k": 5}).json()
        docs = [d['text'] for d in rag_res]
        
        # PRD 3.2.3: Context Tagging & Source Identification
        sources = []
        for d in rag_res:
            raw_text = d['text']
            src_name = "Unknown"
            if "SOURCE:" in raw_text[:50]:
                src_name = raw_text.split("\n")[0].replace("SOURCE:", "").strip()
            
            sources.append({
                "name": src_name, 
                "rating": rate_source_credibility(src_name),
                "excerpt": raw_text[:200]
            })
        
        context = "\n---\n".join(docs)
    except:
        context = "No specific evidence found in real-time index."
        sources = []

    # 2. PRD 3.3: Credibility Scoring via LLM
    groq = Groq(api_key=GROQ_API_KEY)
    
    # Prompt based on PRD 3.3.1 (Baselines) and 3.3.4 (Confidence)
    prompt = f"""
    Act as the Credibility Scorer defined in the PRD.
    User Profile: {req.profile}
    
    Analyze this claim against the context.
    
    PRD Rules:
    1. Medical claims start at 30% baseline.
    2. Conspiracy claims start at 10% baseline.
    3. Established science starts at 90% baseline.
    4. Weight evidence: High credibility sources (10x), Low (0.1x).
    
    Return JSON:
    {{
        "score": 0-100,
        "confidence_score": 0-100,
        "verdict": "TRUE|FALSE|MISLEADING|UNVERIFIED",
        "category": "HEALTH|POLITICS|SCIENCE|FINANCE|OTHER",
        "reasoning": "Plain language explanation (PRD 3.3.5)",
        "key_evidence": ["point 1", "point 2"],
        "context_tags": ["population", "timeframe"],
        "timeline_note": "When this became relevant",
        "related_claims": ["claim 1", "claim 2"]
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
        result['sources'] = sources
        return result
    except Exception as e:
        return {"score": 50, "verdict": "ERROR", "reasoning": str(e), "sources": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)