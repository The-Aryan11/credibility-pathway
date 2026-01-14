"""
Credibility Engine - Ultra-Light Production Version
Optimized for 512MB RAM Limit
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

# Page config
st.set_page_config(
    page_title="Credibility Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh
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
    .main-header { background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); padding: 2rem; border-radius: 1rem; margin-bottom: 2rem; color: white; }
    .score-card { background: white; border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center; border-left: 4px solid; }
    .score-high { border-left-color: #22c55e; } .score-medium { border-left-color: #eab308; } .score-low { border-left-color: #f97316; } .score-false { border-left-color: #ef4444; }
    .evidence-card { background: #f8fafc; border-radius: 0.5rem; padding: 1rem; margin: 0.5rem 0; border-left: 3px solid #3b82f6; color: #1e293b; }
    .footer { text-align: center; padding: 2rem; color: #64748b; margin-top: 3rem; border-top: 1px solid #eee; }
    .pilot-badge { position: fixed; top: 1rem; right: 1rem; background: #f59e0b; color: black; padding: 0.25rem 0.75rem; border-radius: 999px; font-weight: bold; font-size: 0.75rem; z-index: 1000; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
<div class="pilot-badge">🧪 PILOT</div>
""", unsafe_allow_html=True)

# Session state
if 'analysis_history' not in st.session_state: st.session_state.analysis_history = []
if 'selected_language' not in st.session_state: st.session_state.selected_language = 'en'
if 'category_filter' not in st.session_state: st.session_state.category_filter = 'All'

stats = vs.get_stats()
pipeline_status = pathway_engine.get_status()

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("## 🔍 Credibility Engine")
    st.caption("Real-Time Misinformation Tracker")
    st.markdown("---")
    
    st.markdown("### 🌐 Language")
    st.session_state.selected_language = st.selectbox("Select:", list(SUPPORTED_LANGUAGES.keys()), format_func=lambda x: SUPPORTED_LANGUAGES[x])
    st.markdown("---")
    
    st.markdown("### 🔄 Pathway Pipeline")
    if pipeline_status["running"]:
        st.success("🟢 LIVE - Streaming")
        st.caption(f"📁 {pipeline_status['folder']} | 📄 {pipeline_status['files']} files")
    else:
        st.warning("🟡 Starting...")
        if st.button("▶️ Start"):
            pathway_engine.start_pipeline()
            st.rerun()
    st.markdown("---")
    
    st.markdown("### 🏷️ Filter")
    st.session_state.category_filter = st.selectbox("Category:", ['All', 'HEALTH', 'POLITICS', 'SCIENCE', 'TECHNOLOGY', 'FINANCE', 'OTHER'])
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    col1.metric("Docs", stats["total_documents"])
    col2.metric("Checks", len(st.session_state.analysis_history))
    st.markdown("---")
    
    st.markdown("### 📰 Live Feed")
    topic = st.selectbox("Topic:", ["general", "health", "science", "technology"])
    if st.button("🔄 Fetch News", use_container_width=True):
        with st.spinner("Fetching..."):
            articles = fetch_news_by_topic(topic, max_results=5)
            if articles:
                save_articles_to_folder(articles)
                for a in articles:
                    vs.add_document(f"{a['title']}\n{a['description']}", {"source": a['source']})
                st.success(f"✅ Added {len(articles)}!")
                st.rerun()
            else:
                st.error("Failed. Check API.")
    
    st.markdown("---")
    st.caption("© 2025 Aryan & Khushboo")

# ============ MAIN ============
st.markdown("""<div class="main-header"><h1 style="margin:0;">🔍 Credibility Engine</h1><p style="margin:0;">Real-time verification</p></div>""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🔎 Verify", "🔴 Live Demo", "📊 Dashboard", "📚 Knowledge", "📈 History", "🗺️ Map"])

# ============ TAB 1: VERIFY ============
with tab1:
    st.markdown("### Enter a claim")
    
    c_txt, c_mic = st.columns([4, 1])
    with c_txt:
        ex = ["Select...", "Earth is flat", "Vaccines cause autism", "5G causes COVID"]
        sel = st.selectbox("Examples:", ex)
        claim_input = st.text_area("Claim:", value="" if sel=="Select..." else sel, height=100)
    with c_mic:
        st.markdown("### 🎤")
        if st.button("Speak"): st.info("Listening...")

    c1, c2, c3 = st.columns([2, 1, 1])
    do_analyze = c1.button("🔍 Analyze", type="primary", use_container_width=True)
    do_quick = c2.button("⚡ Quick", use_container_width=True)
    if c3.button("🗑️ Clear"): st.rerun()

    if do_analyze or do_quick:
        if claim_input and claim_input != "Select...":
            
            # Translate input
            proc_claim = claim_input
            if st.session_state.selected_language != "en":
                from pipeline.translator import translate_to_english
                proc_claim = translate_to_english(claim_input)

            # Analysis
            with st.spinner("Analyzing..."):
                context = ""
                sources = []
                if stats["total_documents"] > 0:
                    results = vs.search(proc_claim, top_k=3)
                    context = "\n".join([r["text"][:300] for r in results])
                    sources = [r.get("metadata", {}) for r in results]
                
                result = analyze_claim(proc_claim, context if not do_quick else "")
                
                # Related
                if not result.get("related_claims"):
                    result["related_claims"] = get_related_claims(proc_claim, result.get("category", "OTHER"))

            # Save history
            st.session_state.analysis_history.append({
                "claim": claim_input, "result": result, "timestamp": datetime.now().isoformat(),
                "sources": sources
            })
            
            st.markdown("---")
            
            # Display
            score = result.get("score", 50)
            verdict = result.get("verdict", "UNVERIFIED")
            cat = result.get("category", "OTHER")
            
            color, cls, emoji = ("#22c55e", "score-high", "🟢") if score >= 75 else \
                                ("#eab308", "score-medium", "🟡") if score >= 50 else \
                                ("#f97316", "score-low", "🟠") if score >= 25 else \
                                ("#ef4444", "score-false", "🔴")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f'<div class="score-card {cls}"><div style="font-size:2em;font-weight:bold;color:{color}">{emoji} {score}%</div><div>Score</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="score-card"><div style="font-size:1.5em;font-weight:bold;">{verdict}</div><div>Verdict</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="score-card"><div style="font-size:1.5em;font-weight:bold;">{cat}</div><div>Category</div></div>', unsafe_allow_html=True)
            c4.markdown(f'<div class="score-card"><div style="font-size:1.5em;font-weight:bold;">{len(sources)}</div><div>Sources</div></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Reasoning
            c_l, c_r = st.columns(2)
            with c_l:
                st.markdown("#### 📝 Analysis")
                reason = result.get("reasoning", "No details.")
                if st.session_state.selected_language != "en":
                    reason = translate_text(reason, st.session_state.selected_language)
                st.write(reason)
            
            with c_r:
                st.markdown("#### 🔑 Evidence")
                ev = result.get("key_evidence", [])
                if ev:
                    for e in ev:
                        if st.session_state.selected_language != "en":
                            e = translate_text(e, st.session_state.selected_language)
                        st.markdown(f'<div class="evidence-card">{e}</div>', unsafe_allow_html=True)
                else:
                    st.info("No specific evidence.")

            # Actions
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                # PDF Download (Now HTML to save RAM)
                report_html = generate_report(claim_input, result, sources)
                st.download_button("📄 Print Report (PDF)", report_html, "report.html", "text/html", use_container_width=True)
            with c2:
                tweet = f"Fact-checked: '{claim_input[:30]}...' {score}%"
                st.link_button("🐦 Share on Twitter", f"https://twitter.com/intent/tweet?text={tweet}", use_container_width=True)

# ============ TAB 2: LIVE DEMO ============
with tab2:
    st.markdown("### 🔴 Real-Time Demo")
    st.metric("Indexed Docs", stats["total_documents"])
    
    txt = st.text_area("Paste Article:", height=100)
    if st.button("📰 Inject", type="primary"):
        if txt:
            vs.add_document(txt, {"source": "Demo"})
            st.success("✅ Injected! Pipeline processing...")
    
    q = st.text_input("Query new data:")
    if st.button("Search") and q:
        res = vs.search(q, top_k=3)
        if res:
            for r in res: st.info(r["text"][:300])
        else:
            st.warning("No results yet.")

# ============ TAB 3: DASHBOARD ============
with tab3:
    st.markdown("### 📊 Dashboard")
    hist = st.session_state.analysis_history
    if st.session_state.category_filter != 'All':
        hist = [h for h in hist if h["result"].get("category") == st.session_state.category_filter]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total", len(hist))
    c2.metric("False", len([h for h in hist if h["result"].get("score", 50) < 25]))
    c3.metric("True", len([h for h in hist if h["result"].get("score", 50) >= 75]))

# ============ TAB 4: KNOWLEDGE ============
with tab4:
    st.markdown("### 📚 Knowledge Base")
    st.write(f"Total: {stats['total_documents']}")
    q = st.text_input("Search KB:")
    if q:
        res = vs.search(q, top_k=5)
        for r in res: st.caption(r["text"][:200])

# ============ TAB 5: HISTORY ============
with tab5:
    st.markdown("### 📈 History")
    for h in reversed(hist):
        s = h["result"].get("score", 50)
        em = "🟢" if s>=75 else "🔴" if s<25 else "🟡"
        with st.expander(f"{em} {h['claim'][:40]}... ({s}%)"):
            st.write(f"**Verdict:** {h['result'].get('verdict')}")
            st.caption(h['timestamp'])

# ============ TAB 6: MAP (Low RAM) ============
with tab6:
    st.markdown("### 🗺️ Geographic Spread")
    if not hist:
        st.info("No data.")
    else:
        # Simple Iframe Map (0 RAM)
        st.markdown("""
        <iframe width="100%" height="400" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" 
        src="https://www.openstreetmap.org/export/embed.html?bbox=-180,-90,180,90&layer=mapnik"></iframe>
        """, unsafe_allow_html=True)
        
        # Location list
        locs = []
        for h in hist:
            locs.extend(h["result"].get("geographic_relevance", []))
        
        if locs:
            st.write("**Locations Mentioned:** " + ", ".join(set([l for l in locs if l not in ["Global", "Unknown"]])))

st.markdown("<div class='footer'>© 2025 Aryan & Khushboo • Powered by Pathway + Groq</div>", unsafe_allow_html=True)