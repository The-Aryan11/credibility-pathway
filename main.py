# ... (Imports remain same)

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    # 1. Improved RAG Retrieval
    import requests
    try:
        # Retrieve documents
        rag_res = requests.post("http://0.0.0.0:8765/v1/retrieve", json={"query": req.claim, "k": 3}).json()
        
        # FIX: Extract meaningful text only
        docs = []
        sources = []
        for d in rag_res:
            text = d.get('text', '')
            # Filter out short/empty docs to prevent AI confusion
            if len(text) > 50: 
                docs.append(text)
                # Clean source name
                src = "Unknown"
                if "SOURCE:" in text[:100]:
                    src = text.split("\n")[0].replace("SOURCE:", "").strip()
                sources.append({"name": src, "credibility": rate_source(src)})
        
        context = "\n\n---\n\n".join(docs)
    except:
        context = ""
        sources = []

    # 2. Stronger AI Prompt (Prevent Hallucination)
    groq = Groq(api_key=GROQ_API_KEY)
    
    # If no context found, force AI to use internal knowledge
    if not context:
        instruction = "No external context found. Use your internal knowledge base to verify this claim accurately."
    else:
        instruction = f"Use the following Context to verify the claim. If context is irrelevant, ignore it and use internal knowledge.\n\nCONTEXT:\n{context}"

    prompt = f"""
    You are an expert fact-checker. Verify this claim: "{req.claim}"
    
    {instruction}
    
    Return JSON:
    {{
        "score": 0-100 (0=False, 100=True),
        "verdict": "TRUE|FALSE|MISLEADING|UNVERIFIED",
        "reasoning": "Clear explanation of why it is True/False",
        "category": "SCIENCE|HEALTH|POLITICS|OTHER",
        "key_evidence": ["Fact 1", "Fact 2"],
        "confidence_score": 0-100,
        "sentiment": "Positive|Negative|Neutral"
    }}
    """
    
    try:
        chat = groq.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        result = json.loads(chat.choices[0].message.content)
    except:
        result = {"score": 50, "verdict": "ERROR", "reasoning": "AI Processing Failed"}

    result['sources'] = sources
    return result