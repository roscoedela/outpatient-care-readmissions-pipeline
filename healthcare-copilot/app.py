"""
app.py — Outpatient Care Intelligence
Streamlit chat interface powered by LangChain + FAISS + OpenAI GPT-4o-mini
"""

import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

st.set_page_config(
    page_title="Outpatient Care Intelligence",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:      #0a0f1e;
    --surface: #111827;
    --surface2:#1a2236;
    --border:  #1f2d45;
    --accent:  #00d4aa;
    --accent2: #3b82f6;
    --text:    #e2e8f0;
    --muted:   #64748b;
    --serif:   'DM Serif Display', Georgia, serif;
    --sans:    'DM Sans', sans-serif;
    --mono:    'DM Mono', monospace;
}
html, body, [class*="css"] { background-color: var(--bg) !important; color: var(--text) !important; font-family: var(--sans) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2rem 4rem !important; max-width: 1200px; }
[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border); }
[data-testid="stSidebar"] * { color: var(--text) !important; }

.copilot-title { font-family: var(--serif); font-size: 2.4rem; color: var(--text); letter-spacing: -0.02em; }
.copilot-badge { font-family: var(--mono); font-size: 0.65rem; color: var(--accent); border: 1px solid var(--accent); padding: 2px 8px; border-radius: 2px; letter-spacing: 0.1em; }
.copilot-sub { font-size: 0.85rem; color: var(--muted); margin-bottom: 2rem; }

.msg-user { background: var(--surface2); border: 1px solid var(--border); border-left: 3px solid var(--accent2); border-radius: 0 8px 8px 0; padding: 1rem 1.25rem; margin: 1rem 0 0.5rem; }
.msg-assistant { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--accent); border-radius: 0 8px 8px 0; padding: 1rem 1.25rem; margin: 0.5rem 0 1rem; line-height: 1.7; }
.msg-label { font-family: var(--mono); font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem; font-weight: 500; }
.msg-label.user { color: var(--accent2); }
.msg-label.asst { color: var(--accent); }

.sources-header { font-family: var(--mono); font-size: 0.65rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; margin: 1rem 0 0.5rem; }
.source-chip { display: inline-block; background: var(--surface2); border: 1px solid var(--border); border-radius: 3px; padding: 2px 10px; font-family: var(--mono); font-size: 0.7rem; color: var(--muted); margin: 2px 4px 2px 0; }

.stTextInput > div > div > input { background: var(--surface2) !important; border: 1px solid var(--border) !important; border-radius: 6px !important; color: var(--text) !important; font-family: var(--sans) !important; }
.stTextInput > div > div > input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 2px rgba(0,212,170,0.1) !important; }
.stButton > button { background: var(--accent) !important; color: #0a0f1e !important; border: none !important; border-radius: 6px !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    physician = pd.read_csv(os.path.join(base, "physician_state_metrics.csv"))
    analysis  = pd.read_csv(os.path.join(base, "state_healthcare_analysis.csv"))
    STATE_NAMES = {
        "AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California",
        "CO":"Colorado","CT":"Connecticut","DE":"Delaware","FL":"Florida","GA":"Georgia",
        "HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa",
        "KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland",
        "MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi",
        "MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada","NH":"New Hampshire",
        "NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina",
        "ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania",
        "RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota","TN":"Tennessee",
        "TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington",
        "WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming","DC":"Washington D.C.",
        "PR":"Puerto Rico","GU":"Guam","VI":"Virgin Islands",
    }
    valid = set(STATE_NAMES.keys())
    physician = physician[physician["STATE_CODE"].isin(valid)].copy()
    analysis  = analysis[analysis["STATE_CODE"].isin(valid)].copy()
    return physician, analysis, STATE_NAMES

physician_df, analysis_df, STATE_NAMES = load_data()

# ── Load FAISS + chain ───────────────────────────────────────────────────────
@st.cache_resource
def load_chain():
    faiss_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faiss_index")
    if not os.path.exists(faiss_dir):
        return None
    embeddings  = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.load_local(faiss_dir, embeddings, allow_dangerous_deserialization=True)
    retriever   = vectorstore.as_retriever(search_kwargs={"k": 6})

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""You are an outpatient care intelligence analyst with deep expertise in Medicare outpatient data, patient satisfaction, readmissions, and disease burden across US states.

Use the following retrieved context from real CMS and Medicare data to answer the question. Always cite specific states, numbers, and data points. Identify anomalies and outliers. Be analytical and specific.

Context:
{context}

Question: {question}

Provide a clear, insightful answer that:
1. Directly addresses the question with specific data points
2. Identifies anomalies or outliers worth noting
3. Explains what the data means for healthcare outcomes
4. Notes which data sources you are drawing from

Answer:"""
    )

    llm   = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    return chain

chain = load_chain()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style=\"font-family:'DM Serif Display',serif;font-size:1.1rem;margin-bottom:0.25rem\">Outpatient Care Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div style=\"font-size:0.75rem;color:#64748b;margin-bottom:1.5rem\">Powered by CMS Medicare Data</div>", unsafe_allow_html=True)
    st.markdown("**Data Sources**")
    st.markdown("<div style=\"font-size:0.78rem;color:#64748b;line-height:2\">📊 Physician State Metrics<br>🏥 State Healthcare Analysis<br>🔗 Correlation Findings<br>📍 50 US States + Territories</div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#1f2d45;margin:1.5rem 0'>", unsafe_allow_html=True)

    st.markdown("**Quick Stats**")
    avg_cancer = physician_df["CANCER_PCT"].mean()
    avg_stars  = analysis_df["AVG_PATIENT_SURVEY_STAR_RATING"].mean()
    n_states   = physician_df["STATE_CODE"].nunique()
    st.markdown(f"<div style=\"font-family:'DM Mono',monospace;font-size:0.78rem;line-height:2.2;color:#64748b\">States indexed: <span style='color:#00d4aa'>{n_states}</span><br>Avg cancer rate: <span style='color:#f59e0b'>{avg_cancer:.1f}%</span><br>Avg satisfaction: <span style='color:#00d4aa'>{avg_stars:.2f} ★</span></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#1f2d45;margin:1.5rem 0'>", unsafe_allow_html=True)

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("<span class='copilot-title'>Outpatient Care Intelligence</span> &nbsp;<span class='copilot-badge'>BETA</span>", unsafe_allow_html=True)
st.markdown("<div class='copilot-sub'>CMS Medicare outpatient intelligence · Disease burden · Satisfaction · Readmissions · Costs</div>", unsafe_allow_html=True)

st.markdown("<hr style='border:none;border-top:1px solid #1f2d45;margin:1.5rem 0'>", unsafe_allow_html=True)

# ── Chat ─────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

def run_query(query):
    st.session_state.messages.append({"role": "user", "content": query})
    if chain is None:
        answer  = "⚠️ FAISS index not found. Please run `python ingest.py` first, then restart the app."
        sources = []
    else:
        with st.spinner("Retrieving and analyzing..."):
            result   = chain.invoke({"query": query})
            answer   = result["result"]
            src_docs = result.get("source_documents", [])
            sources  = list({
                f"{d.metadata.get('state_name', d.metadata.get('state_code','?'))} · {d.metadata.get('source','').replace('_',' ').title()}"
                for d in src_docs
            })
    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
    st.rerun()

if not st.session_state.messages:
    st.markdown("<div style=\"font-size:0.8rem;color:#64748b;margin-bottom:0.75rem;font-family:'DM Mono',monospace;text-transform:uppercase;letter-spacing:0.08em\">Suggested Questions</div>", unsafe_allow_html=True)
    suggestions = [
        "Which states are anomalies for cancer rates?",
        "Which states have high cost but low satisfaction?",
        "What drives excess readmissions?",
        "Which states have the best overall outcomes?",
        "How does disease burden correlate with satisfaction?",
        "Which states have the worst patient out-of-pocket costs?",
    ]
    cols = st.columns(3)
    for i, s in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(s, key=f"s{i}"):
                run_query(s)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='msg-user'><div class='msg-label user'>You</div>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='msg-assistant'><div class='msg-label asst'>OCI</div>{msg['content']}</div>", unsafe_allow_html=True)
        if msg.get("sources"):
            st.markdown('<div class="sources-header">Retrieved Sources</div>', unsafe_allow_html=True)
            chips = "".join(f'<span class="source-chip">{s}</span>' for s in msg["sources"])
            st.markdown(f"<div>{chips}</div>", unsafe_allow_html=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    col_i, col_b = st.columns([5, 1])
    with col_i:
        user_input = st.text_input("Ask", placeholder="e.g. Which states are anomalies for cancer and heart disease?", label_visibility="collapsed")
    with col_b:
        submitted = st.form_submit_button("Ask →")

if submitted and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})
    if chain is None:
        answer  = "⚠️ FAISS index not found. Please run `python ingest.py` first, then restart the app."
        sources = []
    else:
        with st.spinner("Retrieving and analyzing..."):
            result   = chain.invoke({"query": user_input})
            answer   = result["result"]
            src_docs = result.get("source_documents", [])
            sources  = list({
                f"{d.metadata.get('state_name', d.metadata.get('state_code','?'))} · {d.metadata.get('source','').replace('_',' ').title()}"
                for d in src_docs
            })
    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
    st.rerun()
