import streamlit as st
from pipeline.fact_checker import analyze_claim
from pipeline.news_fetcher import fetch_latest_news, fetch_news_by_topic, save_articles_to_folder
from pipeline.vector_store import vector_store
from pipeline.pathway_engine import pathway_engine
import os
from datetime import datetime

# Page config (MUST be first Streamlit command)
st.set_page_config(
    page_title="Credibility Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize everything once
@st.cache_resource
def init_app():
    # Start Pathway pipeline
    pathway_engine.start_pipeline()
    # Load existing documents
    vector_store.load_from_folder("data/articles")
    return vector_store

vs = init_app()

# Custom CSS
st.markdown("""
<style>
    .main > div { padding-top: 2rem; }
    
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        color: white;
    }
    
    .score-card {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-left: 4px solid;
    }
    
    .score-high { border-left-color: #22c55e; }
    .score-medium { border-left-color: #eab308; }
    .score-low { border-left-color: #f97316; }
    .score-false { border-left-color: #ef4444; }
    
    .evidence-card {
        background: #f8fafc;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #3b82f6;
        color: #1e293b;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #64748b;
        border-top: 1px solid #e2e8f0;
        margin-top: 3rem;
    }
    
    .pilot-badge {
        position: fixed;
        top: 1rem;
        right: 1rem;
        background: #f59e0b;
        color: black;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-weight: bold;
        font-size: 0.75rem;
        z-index: 1000;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>

<div class="pilot-badge">🧪 PILOT</div>
""", unsafe_allow_html=True)

# Session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# Get stats
stats = vs.get_stats()
pipeline_status = pathway_engine.get_status()

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("## 🔍 Credibility Engine")
    st.caption("Real-Time Misinformation Tracker")
    
    st.markdown("---")
    
    # Pathway Status
    st.markdown("### 🔄 Pathway Pipeline")
    if pipeline_status["running"]:
        st.success("🟢 LIVE - Streaming Active")
        st.caption(f"📁 Watching: {pipeline_status['folder']}")
        st.caption(f"📄 Files: {pipeline_status['files']}")
    else:
        st.warning("🟡 Pipeline starting...")
        if st.button("▶️ Start Pipeline"):
            pathway_engine.start_pipeline()
            st.rerun()
    
    st.markdown("---")
    
    # Stats
    st.markdown("### 📊 Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📄 Articles", stats["total_documents"])
    with col2:
        st.metric("🔍 Analyses", len(st.session_state.analysis_history))
    
    st.markdown("---")
    
    # Data Ingestion
    st.markdown("### 📰 Live Data Feed")
    topic = st.selectbox(
        "Select Topic:",
        ["general", "health", "science", "technology", "business", "world"]
    )
    
    if st.button("🔄 Fetch Latest News", use_container_width=True):
        with st.spinner("Fetching live news..."):
            articles = fetch_news_by_topic(topic, max_results=5)
            if articles:
                save_articles_to_folder(articles)
                for article in articles:
                    content = f"{article['title']}\n{article['description']}\n{article['content']}"
                    vs.add_document(content, {"source": article['source'], "url": article['url']})
                st.success(f"✅ Added {len(articles)} articles!")
                st.rerun()
            else:
                st.error("Failed to fetch. Check API key.")
    
    st.markdown("---")
    
    # Manual input
    st.markdown("### 📝 Add Evidence")
    with st.expander("Paste Article/Evidence"):
        custom_text = st.text_area("Content:", height=100, key="custom_article")
        custom_source = st.text_input("Source (optional):", key="custom_source")
        if st.button("Add to Knowledge Base"):
            if custom_text:
                vs.add_document(custom_text, {"source": custom_source or "Manual Entry"})
                st.success("✅ Added!")
                st.rerun()
    
    st.markdown("---")
    
    # Settings
    st.markdown("### ⚙️ Settings")
    use_context = st.toggle("Use Knowledge Base", value=True)
    show_reasoning = st.toggle("Show Detailed Reasoning", value=True)
    
    st.markdown("---")
    st.caption("© 2025 Aryan & Khushboo")
    st.caption("All Rights Reserved")

# ============ MAIN CONTENT ============
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.5rem;">🔍 Credibility Engine</h1>
    <p style="margin:0.5rem 0 0 0; opacity: 0.9;">Real-time claim verification powered by AI & live evidence</p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔎 Verify Claim", 
    "🔴 Live Demo",
    "📊 Dashboard", 
    "📚 Knowledge Base", 
    "📈 History"
])

# ============ TAB 1: VERIFY CLAIM ============
with tab1:
    st.markdown("### Enter a claim to verify")
    
    example_claims = [
        "Select an example...",
        "The earth is flat",
        "Vaccines cause autism",
        "Drinking 8 glasses of water daily is necessary",
        "5G causes COVID-19",
        "Climate change is a hoax"
    ]
    
    selected_example = st.selectbox("Or try an example:", example_claims)
    
    claim_input = st.text_area(
        "Your Claim:",
        value="" if selected_example == "Select an example..." else selected_example,
        placeholder="Enter a claim you want to verify...",
        height=100
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        analyze_button = st.button("🔍 Analyze Claim", type="primary", use_container_width=True)
    with col2:
        quick_check = st.button("⚡ Quick Check", use_container_width=True)
    with col3:
        if st.button("🗑️ Clear", use_container_width=True):
            st.rerun()
    
    if analyze_button or quick_check:
        if claim_input and claim_input != "Select an example...":
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Search knowledge base
            status_text.text("🔍 Searching knowledge base...")
            progress_bar.progress(25)
            
            context = ""
            sources = []
            if use_context and stats["total_documents"] > 0:
                results = vs.search(claim_input, top_k=3)
                context = "\n\n---\n\n".join([r["text"][:500] for r in results])
                sources = [r.get("metadata", {}) for r in results]
            
            # Step 2: AI Analysis
            status_text.text("🤖 Analyzing with AI...")
            progress_bar.progress(60)
            
            result = analyze_claim(claim_input, context if not quick_check else "")
            
            # Step 3: Complete
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Save to history
            st.session_state.analysis_history.append({
                "claim": claim_input,
                "result": result,
                "timestamp": datetime.now().isoformat(),
                "sources_used": len(sources)
            })
            
            progress_bar.empty()
            status_text.empty()
            
            st.markdown("---")
            
            # Results
            score = result.get("score", 50)
            verdict = result.get("verdict", "UNVERIFIED")
            category = result.get("category", "OTHER")
            
            if score >= 75:
                score_color, score_class, score_emoji = "#22c55e", "score-high", "🟢"
            elif score >= 50:
                score_color, score_class, score_emoji = "#eab308", "score-medium", "🟡"
            elif score >= 25:
                score_color, score_class, score_emoji = "#f97316", "score-low", "🟠"
            else:
                score_color, score_class, score_emoji = "#ef4444", "score-false", "🔴"
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="score-card {score_class}">
                    <div style="font-size: 2.5rem; font-weight: bold; color: {score_color};">{score_emoji} {score}%</div>
                    <div style="color: #64748b; margin-top: 0.5rem;">Credibility Score</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="score-card" style="border-left-color: #6366f1;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #1e293b;">{verdict}</div>
                    <div style="color: #64748b; margin-top: 0.5rem;">Verdict</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="score-card" style="border-left-color: #8b5cf6;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #1e293b;">{category}</div>
                    <div style="color: #64748b; margin-top: 0.5rem;">Category</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="score-card" style="border-left-color: #06b6d4;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #1e293b;">{len(sources)}</div>
                    <div style="color: #64748b; margin-top: 0.5rem;">Sources Used</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            if show_reasoning:
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.markdown("#### 📝 Analysis")
                    st.write(result.get("reasoning", "No detailed reasoning available."))
                
                with col_right:
                    st.markdown("#### 🔑 Key Evidence Points")
                    evidence = result.get("key_evidence", [])
                    if evidence:
                        for e in evidence:
                            st.markdown(f'<div class="evidence-card">{e}</div>', unsafe_allow_html=True)
                    else:
                        st.info("No specific evidence points identified.")
            
            if sources and use_context:
                st.markdown("---")
                st.markdown("#### 📰 Sources Referenced")
                for s in sources:
                    st.caption(f"• {s.get('source', 'Unknown Source')}")
        else:
            st.warning("⚠️ Please enter a claim to analyze")

# ============ TAB 2: LIVE DEMO ============
with tab2:
    st.markdown("### 🔴 Real-Time Demonstration")
    st.markdown("""
    **This demonstrates the LIVE capability required by the hackathon.**
    
    Watch how the system updates in real-time when new data arrives!
    """)
    
    st.markdown("---")
    
    # Current state
    st.markdown("#### Step 1: Current Knowledge Base")
    current_stats = vs.get_stats()
    st.metric("Documents Indexed", current_stats["total_documents"])
    
    # Add new document
    st.markdown("#### Step 2: Add New Evidence (Simulates Live News)")
    demo_text = st.text_area(
        "Paste breaking news article:",
        placeholder="Example: Scientists at MIT announced today that...",
        height=100,
        key="demo_article_input"
    )
    demo_source = st.text_input("Source:", value="Reuters", key="demo_source_input")
    
    if st.button("📰 Inject Live Article", type="primary"):
        if demo_text:
            vs.add_document(demo_text, {"source": demo_source})
            st.success("✅ Article injected!")
            st.info("⏳ Pathway pipeline is now processing...")
            st.markdown("#### Step 3: Verify Real-Time Update")
            st.write("The document is now indexed. Query it below!")
    
    st.markdown("---")
    
    # Query
    st.markdown("#### Step 3: Query the New Information")
    demo_query = st.text_input(
        "Ask about the article you just added:",
        placeholder="What did scientists announce?",
        key="demo_query_input"
    )
    
    if st.button("🔍 Search", key="demo_search") and demo_query:
        results = vs.search(demo_query, top_k=3)
        
        if results:
            st.success(f"✅ Found {len(results)} results!")
            for i, r in enumerate(results):
                with st.expander(f"Result {i+1} (Score: {r['score']:.2%})"):
                    st.write(r["text"][:500])
        else:
            st.warning("No results yet.")
    
    st.markdown("---")
    st.markdown("""
    ### 🎯 What This Demonstrates
    
    1. **Real-Time Ingestion** - Articles are added to Pathway's watched folder
    2. **Streaming Processing** - Pathway detects new files automatically
    3. **Instant Retrieval** - New content is immediately searchable
    4. **No Restart Needed** - The pipeline runs continuously
    """)

# ============ TAB 3: DASHBOARD ============
with tab3:
    st.markdown("### 📊 System Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Articles Indexed", stats["total_documents"])
    with col2:
        st.metric("🔍 Total Analyses", len(st.session_state.analysis_history))
    with col3:
        false_count = len([h for h in st.session_state.analysis_history if h["result"].get("score", 50) < 25])
        st.metric("🔴 False Claims", false_count)
    with col4:
        true_count = len([h for h in st.session_state.analysis_history if h["result"].get("score", 50) >= 75])
        st.metric("🟢 Verified True", true_count)
    
    st.markdown("---")
    st.markdown("### 🔄 Real-Time Pipeline")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    icons = [("📰", "Ingest", "Live feeds"), ("🔄", "Process", "Pathway"), 
             ("🧠", "Embed", "Vectors"), ("🔍", "Retrieve", "Search"), ("🤖", "Analyze", "AI")]
    
    for col, (icon, title, desc) in zip([col1, col2, col3, col4, col5], icons):
        with col:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 2rem;">{icon}</div>
                <div style="font-weight: bold;">{title}</div>
                <div style="font-size: 0.8rem; color: #64748b;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# ============ TAB 4: KNOWLEDGE BASE ============
with tab4:
    st.markdown("### 📚 Indexed Knowledge Base")
    
    if stats["total_documents"] == 0:
        st.info("📭 No articles indexed yet. Click '🔄 Fetch Latest News' in the sidebar!")
    else:
        st.success(f"✅ {stats['total_documents']} documents indexed")
        
        search_query = st.text_input("🔍 Search:", placeholder="Enter keywords...")
        
        if search_query:
            results = vs.search(search_query, top_k=5)
            st.markdown(f"**Found {len(results)} results:**")
            for i, r in enumerate(results):
                with st.expander(f"Document {i+1} (Score: {r['score']:.2%})"):
                    st.write(r["text"][:500])
                    st.caption(f"Source: {r['metadata'].get('source', 'Unknown')}")
        
        st.markdown("---")
        
        articles_folder = "data/articles"
        if os.path.exists(articles_folder):
            files = sorted(os.listdir(articles_folder), reverse=True)
            st.markdown(f"**📁 {len(files)} files:**")
            for f in files[:10]:
                with st.expander(f"📄 {f}"):
                    with open(os.path.join(articles_folder, f), 'r', encoding='utf-8') as file:
                        st.text(file.read()[:500] + "...")

# ============ TAB 5: HISTORY ============
with tab5:
    st.markdown("### 📈 Analysis History")
    
    if not st.session_state.analysis_history:
        st.info("📭 No analyses yet. Go to 'Verify Claim' to get started!")
    else:
        total = len(st.session_state.analysis_history)
        false_claims = len([h for h in st.session_state.analysis_history if h["result"].get("score", 50) < 25])
        true_claims = len([h for h in st.session_state.analysis_history if h["result"].get("score", 50) >= 75])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total", total)
        col2.metric("🔴 False", false_claims)
        col3.metric("🟢 True", true_claims)
        
        st.markdown("---")
        
        for h in reversed(st.session_state.analysis_history):
            score = h["result"].get("score", 50)
            emoji = "🟢" if score >= 75 else "🟡" if score >= 50 else "🟠" if score >= 25 else "🔴"
            
            with st.expander(f"{emoji} {h['claim'][:50]}... ({score}%)"):
                st.write(f"**Claim:** {h['claim']}")
                st.write(f"**Score:** {score}%")
                st.write(f"**Verdict:** {h['result'].get('verdict', 'N/A')}")
                st.write(f"**Reasoning:** {h['result'].get('reasoning', 'N/A')}")
                st.caption(f"Analyzed: {h['timestamp']}")

# Footer
st.markdown("""
<div class="footer">
    <p>© 2025 Aryan & Khushboo • All Rights Reserved</p>
    <p style="font-size: 0.8rem;">Powered by Pathway + Groq + HuggingFace</p>
</div>
""", unsafe_allow_html=True)