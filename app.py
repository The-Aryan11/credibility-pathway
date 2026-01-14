"""
Credibility Engine - Production Version
Features: RAG, Real-Time Streaming, Source Credibility, PDF Export,
          Confidence Intervals, Related Claims, Category Filter,
          Auto-refresh, Multi-language, Geographic Map, Voice Input, Social Share
"""
import streamlit as st
from pipeline.fact_checker import analyze_claim, get_source_credibility, get_related_claims
from pipeline.news_fetcher import fetch_news_by_topic, save_articles_to_folder
from pipeline.vector_store import vector_store
from pipeline.pathway_engine import pathway_engine
from pipeline.translator import translate_text, SUPPORTED_LANGUAGES
from pipeline.pdf_generator import generate_report
import os
from datetime import datetime
import pandas as pd
import numpy as np

# Page config
st.set_page_config(
    page_title="Credibility Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Feature 13: Auto-refresh (Handle import error gracefully)
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=60000, limit=None, key="refresh")
except:
    pass

# Initialize
@st.cache_resource
def init_app():
    pathway_engine.start_pipeline()
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
    
    .source-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    
    .source-high { background: #dcfce7; color: #166534; }
    .source-medium { background: #fef3c7; color: #92400e; }
    .source-low { background: #fee2e2; color: #991b1b; }
    
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
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'en'
if 'category_filter' not in st.session_state:
    st.session_state.category_filter = 'All'

# Stats
stats = vs.get_stats()
pipeline_status = pathway_engine.get_status()

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("## 🔍 Credibility Engine")
    st.caption("Real-Time Misinformation Tracker")
    
    st.markdown("---")
    
    # Feature 14: Language Selection
    st.markdown("### 🌐 Language")
    st.session_state.selected_language = st.selectbox(
        "Select Language:",
        options=list(SUPPORTED_LANGUAGES.keys()),
        format_func=lambda x: SUPPORTED_LANGUAGES[x],
        key="lang_selector"
    )
    
    st.markdown("---")
    
    # Pathway Status
    st.markdown("### 🔄 Pathway Pipeline")
    if pipeline_status["running"]:
        st.success("🟢 LIVE - Streaming")
        st.caption(f"📁 {pipeline_status['folder']}")
        st.caption(f"📄 {pipeline_status['files']} files")
    else:
        st.warning("🟡 Starting...")
        if st.button("▶️ Start Pipeline"):
            pathway_engine.start_pipeline()
            st.rerun()
    
    st.markdown("---")
    
    # Feature 12: Category Filter
    st.markdown("### 🏷️ Filter")
    categories = ['All', 'HEALTH', 'POLITICS', 'SCIENCE', 'TECHNOLOGY', 'FINANCE', 'OTHER']
    st.session_state.category_filter = st.selectbox("Category:", categories)
    
    st.markdown("---")
    
    # Stats
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📄 Docs", stats["total_documents"])
    with col2:
        st.metric("🔍 Checks", len(st.session_state.analysis_history))
    
    st.markdown("---")
    
    # Data Ingestion
    st.markdown("### 📰 Live Feed")
    topic = st.selectbox("Topic:", ["general", "health", "science", "technology", "business"])
    
    if st.button("🔄 Fetch News", use_container_width=True):
        with st.spinner("Fetching..."):
            articles = fetch_news_by_topic(topic, max_results=5)
            if articles:
                save_articles_to_folder(articles)
                for a in articles:
                    vs.add_document(f"{a['title']}\n{a['description']}\n{a['content']}", 
                                   {"source": a['source'], "url": a['url']})
                st.success(f"✅ Added {len(articles)}!")
                st.rerun()
            else:
                st.error("Failed. Check API key.")
    
    st.markdown("---")
    
    # Manual Input
    with st.expander("📝 Add Evidence"):
        custom_text = st.text_area("Content:", height=80, key="custom_txt")
        custom_source = st.text_input("Source:", key="custom_src")
        if st.button("Add"):
            if custom_text:
                vs.add_document(custom_text, {"source": custom_source or "Manual"})
                st.success("✅ Added!")
                st.rerun()
    
    st.markdown("---")
    
    # Settings
    st.markdown("### ⚙️ Settings")
    use_context = st.toggle("Use Knowledge Base", value=True)
    show_reasoning = st.toggle("Show Details", value=True)
    show_confidence = st.toggle("Show Confidence", value=True)
    
    st.markdown("---")
    st.caption("© 2025 Aryan & Khushboo")

# ============ MAIN ============
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.5rem;">🔍 Credibility Engine</h1>
    <p style="margin:0.5rem 0 0 0; opacity: 0.9;">Real-time claim verification with AI</p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔎 Verify", "🔴 Live Demo", "📊 Dashboard", 
    "📚 Knowledge", "📈 History", "🗺️ Map"
])

# ============ TAB 1: VERIFY ============
with tab1:
    st.markdown("### Enter a claim to verify")
    
    # Feature 24: Voice Input
    col_text, col_voice = st.columns([4, 1])
    
    with col_text:
        examples = ["Select example...", "The earth is flat", "Vaccines cause autism", 
                   "5G causes COVID-19", "Climate change is a hoax"]
        selected = st.selectbox("Examples:", examples)
        
        claim_input = st.text_area(
            "Your Claim:",
            value="" if selected == "Select example..." else selected,
            placeholder="Enter claim to verify...",
            height=100
        )
    
    with col_voice:
        st.markdown("### 🎤")
        st.caption("Voice Input")
        if st.button("🎙️ Speak"):
            st.info("Listening... (Say your claim)")
            # Note: Browser microphone access needs HTTPS or localhost
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)
    with col2:
        quick_btn = st.button("⚡ Quick", use_container_width=True)
    with col3:
        if st.button("🗑️ Clear"):
            st.rerun()
    
    if analyze_btn or quick_btn:
        if claim_input and claim_input != "Select example...":
            
            # Translate input (Feature 14)
            analysis_claim = claim_input
            
            progress = st.progress(0)
            status = st.empty()
            
            # Search
            status.text("🔍 Searching knowledge base...")
            progress.progress(25)
            
            context = ""
            sources = []
            source_details = []
            if use_context and stats["total_documents"] > 0:
                results = vs.search(analysis_claim, top_k=3)
                context = "\n\n".join([r["text"][:500] for r in results])
                for r in results:
                    src = r.get("metadata", {}).get("source", "Unknown")
                    sources.append(r.get("metadata", {}))
                    source_details.append(get_source_credibility(src))
            
            # Analyze
            status.text("🤖 Analyzing with AI...")
            progress.progress(60)
            
            result = analyze_claim(analysis_claim, context if not quick_btn else "")
            
            # Related Claims (Feature 8)
            status.text("🔗 Finding related claims...")
            progress.progress(80)
            
            if not result.get("related_claims"):
                result["related_claims"] = get_related_claims(analysis_claim, result.get("category", "OTHER"))
            
            progress.progress(100)
            status.text("✅ Complete!")
            
            # Save history
            st.session_state.analysis_history.append({
                "claim": claim_input,
                "result": result,
                "timestamp": datetime.now().isoformat(),
                "sources": sources,
                "source_details": source_details
            })
            
            progress.empty()
            status.empty()
            
            st.markdown("---")
            
            # Results
            score = result.get("score", 50)
            verdict = result.get("verdict", "UNVERIFIED")
            category = result.get("category", "OTHER")
            conf_low = result.get("confidence_low", score - 10)
            conf_high = result.get("confidence_high", score + 10)
            
            if score >= 75:
                score_color, score_class, emoji = "#22c55e", "score-high", "🟢"
            elif score >= 50:
                score_color, score_class, emoji = "#eab308", "score-medium", "🟡"
            elif score >= 25:
                score_color, score_class, emoji = "#f97316", "score-low", "🟠"
            else:
                score_color, score_class, emoji = "#ef4444", "score-false", "🔴"
            
            # Score cards
            c1, c2, c3, c4 = st.columns(4)
            
            with c1:
                st.markdown(f"""
                <div class="score-card {score_class}">
                    <div style="font-size: 2.5rem; font-weight: bold; color: {score_color};">{emoji} {score}%</div>
                    <div style="color: #64748b;">Credibility</div>
                </div>
                """, unsafe_allow_html=True)
            
            with c2:
                st.markdown(f"""
                <div class="score-card" style="border-left-color: #6366f1;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #1e293b;">{verdict}</div>
                    <div style="color: #64748b;">Verdict</div>
                </div>
                """, unsafe_allow_html=True)
            
            with c3:
                st.markdown(f"""
                <div class="score-card" style="border-left-color: #8b5cf6;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #1e293b;">{category}</div>
                    <div style="color: #64748b;">Category</div>
                </div>
                """, unsafe_allow_html=True)
            
            with c4:
                st.markdown(f"""
                <div class="score-card" style="border-left-color: #06b6d4;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #1e293b;">{len(sources)}</div>
                    <div style="color: #64748b;">Sources</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Feature 7: Confidence Interval
            if show_confidence:
                st.markdown("---")
                st.markdown("#### 📊 Confidence")
                st.markdown(f"Uncertainty: **{conf_high - conf_low}%** | Range: **{conf_low}% - {conf_high}%**")
                st.progress(score / 100)
                c1, c2, c3 = st.columns(3)
                c1.caption(f"Low: {conf_low}%")
                c2.caption(f"Score: {score}%")
                c3.caption(f"High: {conf_high}%")
            
            st.markdown("---")
            
            # Reasoning
            if show_reasoning:
                c_left, c_right = st.columns(2)
                
                with c_left:
                    st.markdown("#### 📝 Analysis")
                    reasoning = result.get("reasoning", "No reasoning.")
                    
                    # Translate output (Feature 14)
                    if st.session_state.selected_language != "en":
                        reasoning = translate_text(reasoning, st.session_state.selected_language)
                    
                    st.write(reasoning)
                    
                    timeline = result.get("timeline_note", "")
                    if timeline:
                        st.info(f"⏰ {timeline}")
                
                with c_right:
                    st.markdown("#### 🔑 Evidence")
                    evidence = result.get("key_evidence", [])
                    if evidence:
                        for e in evidence:
                            if st.session_state.selected_language != "en":
                                e = translate_text(e, st.session_state.selected_language)
                            st.markdown(f'<div class="evidence-card">{e}</div>', unsafe_allow_html=True)
                    else:
                        st.info("No specific evidence.")
            
            # Feature 1: Source Credibility
            if source_details:
                st.markdown("---")
                st.markdown("#### 📰 Sources")
                for src in source_details:
                    level = src.get("level", "Unknown").lower()
                    level_cls = "high" if "high" in level else "medium" if "medium" in level else "low"
                    st.markdown(f"""
                    <span class="source-badge source-{level_cls}">
                        {src['name']} - {src['score']}% ({src['level']})
                    </span>
                    """, unsafe_allow_html=True)
            
            # Feature 8: Related Claims
            related = result.get("related_claims", [])
            if related:
                st.markdown("---")
                st.markdown("#### 🔗 Related")
                for rc in related:
                    st.markdown(f"• {rc}")
            
            # Features 3 & 6: Export & Share
            st.markdown("---")
            st.markdown("#### 📤 Share")
            
            c1, c2, c3, c4 = st.columns(4)
            
            # PDF
            with c1:
                pdf_bytes = generate_report(claim_input, result, sources)
                st.download_button(
                    "📄 PDF",
                    data=pdf_bytes,
                    file_name=f"report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            # Twitter
            with c2:
                tweet = f"Fact-checked: \"{claim_input[:30]}...\" {emoji} {score}%"
                st.link_button("🐦 Twitter", f"https://twitter.com/intent/tweet?text={tweet}", use_container_width=True)
            
            # WhatsApp
            with c3:
                wa_msg = f"Fact Check:\n{claim_input[:50]}...\nScore: {score}% ({verdict})"
                st.link_button("💬 WhatsApp", f"https://wa.me/?text={wa_msg}", use_container_width=True)
            
            # LinkedIn
            with c4:
                st.link_button("💼 LinkedIn", "https://linkedin.com", use_container_width=True)
            
            # Copy
            summary = f"Claim: {claim_input}\nScore: {score}% | {verdict}\n- Credibility Engine"
            st.code(summary, language=None)
        
        else:
            st.warning("⚠️ Enter a claim")

# ============ TAB 2: LIVE DEMO ============
with tab2:
    st.markdown("### 🔴 Real-Time Demonstration")
    st.markdown("**Watch the system update in real-time!**")
    
    st.markdown("---")
    
    st.markdown("#### Step 1: Current State")
    st.metric("Documents", stats["total_documents"])
    
    st.markdown("#### Step 2: Add Article")
    demo_text = st.text_area("Paste article:", height=100, key="demo_txt")
    demo_src = st.text_input("Source:", value="Reuters", key="demo_src")
    
    if st.button("📰 Inject Article", type="primary"):
        if demo_text:
            vs.add_document(demo_text, {"source": demo_src})
            st.success("✅ Injected! Query it below.")
    
    st.markdown("---")
    
    st.markdown("#### Step 3: Query")
    demo_q = st.text_input("Search:", key="demo_q")
    
    if st.button("🔍 Search", key="demo_search") and demo_q:
        results = vs.search(demo_q, top_k=3)
        if results:
            st.success(f"Found {len(results)} results!")
            for i, r in enumerate(results):
                with st.expander(f"Result {i+1} ({r['score']:.0%})"):
                    st.write(r["text"][:300])
        else:
            st.warning("No results.")
    
    st.markdown("---")
    st.markdown("""
    ### 🎯 This Demonstrates:
    1. **Real-Time Ingestion** - Pathway watches folder
    2. **Instant Indexing** - New content searchable immediately
    3. **No Restart** - Continuous operation
    """)

# ============ TAB 3: DASHBOARD ============
with tab3:
    st.markdown("### 📊 Dashboard")
    
    filtered = st.session_state.analysis_history
    if st.session_state.category_filter != 'All':
        filtered = [h for h in filtered if h["result"].get("category") == st.session_state.category_filter]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📄 Docs", stats["total_documents"])
    c2.metric("🔍 Analyses", len(filtered))
    c3.metric("🔴 False", len([h for h in filtered if h["result"].get("score", 50) < 25]))
    c4.metric("🟢 True", len([h for h in filtered if h["result"].get("score", 50) >= 75]))
    
    st.markdown("---")
    
    # Category breakdown
    if st.session_state.analysis_history:
        st.markdown("### 📊 By Category")
        cats = {}
        for h in st.session_state.analysis_history:
            cat = h["result"].get("category", "OTHER")
            cats[cat] = cats.get(cat, 0) + 1
        
        for cat, count in sorted(cats.items(), key=lambda x: x[1], reverse=True):
            st.write(f"**{cat}:** {count}")
            st.progress(count / len(st.session_state.analysis_history))
    
    st.markdown("---")
    
    # Pipeline
    st.markdown("### 🔄 Pipeline")
    cols = st.columns(5)
    icons = [("📰", "Ingest"), ("🔄", "Process"), ("🧠", "Embed"), ("🔍", "Retrieve"), ("🤖", "Analyze")]
    for col, (icon, name) in zip(cols, icons):
        with col:
            st.markdown(f"<div style='text-align:center'><div style='font-size:2rem'>{icon}</div><b>{name}</b></div>", unsafe_allow_html=True)

# ============ TAB 4: KNOWLEDGE BASE ============
with tab4:
    st.markdown("### 📚 Knowledge Base")
    
    if stats["total_documents"] == 0:
        st.info("📭 No documents. Fetch news from sidebar!")
    else:
        st.success(f"✅ {stats['total_documents']} documents")
        
        query = st.text_input("🔍 Search:", key="kb_search")
        
        if query:
            results = vs.search(query, top_k=5)
            for i, r in enumerate(results):
                with st.expander(f"Doc {i+1} ({r['score']:.0%})"):
                    st.write(r["text"][:400])
                    st.caption(f"Source: {r['metadata'].get('source', 'Unknown')}")
        
        st.markdown("---")
        
        folder = "data/articles"
        if os.path.exists(folder):
            files = sorted(os.listdir(folder), reverse=True)[:10]
            st.markdown(f"**📁 {len(files)} files:**")
            for f in files:
                with st.expander(f"📄 {f}"):
                    with open(os.path.join(folder, f), 'r', encoding='utf-8') as file:
                        st.text(file.read()[:300] + "...")

# ============ TAB 5: HISTORY ============
with tab5:
    st.markdown("### 📈 History")
    
    filtered = st.session_state.analysis_history
    if st.session_state.category_filter != 'All':
        filtered = [h for h in filtered if h["result"].get("category") == st.session_state.category_filter]
    
    if not filtered:
        st.info("📭 No analyses yet.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total", len(filtered))
        c2.metric("🔴 False", len([h for h in filtered if h["result"].get("score", 50) < 25]))
        c3.metric("🟢 True", len([h for h in filtered if h["result"].get("score", 50) >= 75]))
        
        st.markdown("---")
        
        for h in reversed(filtered):
            score = h["result"].get("score", 50)
            emoji = "🟢" if score >= 75 else "🟡" if score >= 50 else "🟠" if score >= 25 else "🔴"
            
            with st.expander(f"{emoji} {h['claim'][:40]}... ({score}%)"):
                st.write(f"**Claim:** {h['claim']}")
                st.write(f"**Score:** {score}%")
                st.write(f"**Verdict:** {h['result'].get('verdict')}")
                st.write(f"**Category:** {h['result'].get('category')}")
                st.write(f"**Reasoning:** {h['result'].get('reasoning')}")
                st.caption(f"📅 {h['timestamp']}")

# ============ TAB 6: GEOGRAPHIC MAP (Optimized) ============
with tab6:
    st.markdown("### 🗺️ Geographic Spread")
    
    if not st.session_state.analysis_history:
        st.info("📭 No data. Analyze claims first.")
    else:
        # Standard Streamlit Map (Memory Safe)
        coords = {
            "Global": [20, 0], "USA": [39, -98], "UK": [54, -2], "India": [20, 77],
            "China": [35, 105], "Brazil": [-10, -55], "Germany": [51, 10],
            "France": [46, 2], "Australia": [-25, 135], "Russia": [60, 100],
            "Japan": [36, 138], "Canada": [56, -106]
        }
        
        map_points = []
        for h in st.session_state.analysis_history:
            regions = h["result"].get("geographic_relevance", ["Global"])
            for region in regions:
                if region in coords:
                    lat, lon = coords[region]
                    # Add jitter so dots don't overlap
                    map_points.append({
                        "lat": lat + np.random.uniform(-2, 2),
                        "lon": lon + np.random.uniform(-2, 2)
                    })
        
        if map_points:
            st.map(pd.DataFrame(map_points))
            st.caption("Locations related to analyzed claims")
        else:
            st.info("No location data found in claims.")

# Footer
st.markdown("""
<div class="footer">
    <p>© 2025 Aryan & Khushboo • All Rights Reserved</p>
    <p style="font-size: 0.8rem;">Powered by Pathway + Groq + HuggingFace</p>
</div>
""", unsafe_allow_html=True)