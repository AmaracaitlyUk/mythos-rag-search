"""
RAG-Based AI Search System — interface.

Run with:
    streamlit run app.py
"""

import streamlit as st

from rag.ingest import load_documents, build_chunk_records
from rag.embed_store import VectorStore
from rag.generate import generate_answer, MIN_RELEVANCE_SCORE

DATA_FOLDER = "data/mythology_docs"

st.set_page_config(page_title="Mythos Search", page_icon="✦", layout="wide")

# One consistent label per status — no color coding, the words do the work.
STATUS_LABEL = {
    "llm": "Answer",
    "fallback": "Answer (fallback mode)",
    "off_topic": "Outside this collection",
    "no_results": "No matches found",
}

# --- Theme: soft, pastel, easy on the eyes. Carved-stone display type over
# warm cream and lilac mist, with a dusty plum accent. Only our own custom
# classes get font overrides — native Streamlit elements (icons, widgets)
# are left alone so their internal icon fonts don't break. ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap');

    :root {
        --bg-top: #f6f0fb;
        --bg-bottom: #fdf8f0;
        --card-bg: #fffdfa;
        --accent: #a67bb5;
        --accent-soft: rgba(166, 123, 181, 0.30);
        --text: #4a3b52;
        --text-muted: #8d7c93;
    }

    .stApp {
        background: linear-gradient(160deg, var(--bg-top) 0%, var(--bg-bottom) 100%);
    }

    section[data-testid="stSidebar"] {
        background: #fbf6ff;
        border-right: 1px solid var(--accent-soft);
    }

    .mythos-title {
        text-align: center;
        font-family: 'Cinzel', serif;
        font-size: 2.4em;
        font-weight: 600;
        color: var(--text);
        letter-spacing: 0.05em;
        margin-bottom: 0;
    }

    .mythos-subtitle {
        text-align: center;
        font-family: 'EB Garamond', serif;
        font-style: italic;
        color: var(--text-muted);
        font-size: 1.1em;
        margin-top: 4px;
    }

    .mythos-divider {
        text-align: center;
        color: var(--accent);
        font-size: 1.2em;
        letter-spacing: 0.5em;
        margin: 18px 0 22px 0;
        opacity: 0.85;
    }

    .mythos-card {
        background: var(--card-bg);
        border: 1px solid var(--accent-soft);
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 20px;
        box-shadow: 0 4px 18px rgba(166, 123, 181, 0.15);
    }

    .mythos-label {
        font-family: 'Cinzel', serif;
        font-size: 0.72em;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: 10px;
        display: block;
    }

    .mythos-answer {
        font-family: 'EB Garamond', serif;
        font-size: 1.15em;
        line-height: 1.6;
        color: var(--text);
        white-space: pre-wrap;
    }

    .mythos-sidebar-caption {
        font-family: 'EB Garamond', serif;
        color: var(--text-muted);
        font-size: 0.9em;
    }

    .stTextInput input {
        background: var(--card-bg) !important;
        color: var(--text) !important;
        border: 1px solid var(--accent-soft) !important;
        font-family: 'EB Garamond', serif !important;
        font-size: 1.05em !important;
    }

    .stButton button, .stFormSubmitButton button {
        background: var(--accent) !important;
        color: #fffdfa !important;
        font-family: 'Cinzel', serif !important;
        letter-spacing: 0.08em;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    .stButton button:hover, .stFormSubmitButton button:hover {
        background: #91679f !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Loading")
def load_store():
    docs = load_documents(DATA_FOLDER)
    chunks = build_chunk_records(docs)
    store = VectorStore()
    store.build(chunks)
    return store, docs, chunks


store, docs, chunks = load_store()

with st.sidebar:
    st.markdown("### ✦ Settings")
    top_k = st.slider("Passages to retrieve", min_value=1, max_value=10, value=3)
    st.markdown(
        f'<span class="mythos-sidebar-caption">Indexed <b>{len(docs)}</b> documents → <b>{len(chunks)}</b> chunks</span>',
        unsafe_allow_html=True,
    )
    with st.expander("Documents in this index"):
        for d in docs:
            st.write(f"- {d['title']}")

st.markdown('<div class="mythos-title">✦ Mythos Search ✦</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="mythos-subtitle">Curious about the mythology and folklore? Start here.</div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="mythos-divider">· · ✦ · · </div>', unsafe_allow_html=True)

with st.form(key="search_form"):
    query = st.text_input(
        "Your question",
        placeholder="e.g. Why does Loki betray the other gods in Norse mythology?",
        label_visibility="collapsed",
    )
    col_left, col_center, col_right = st.columns([1, 1, 1])
    with col_center:
        search_clicked = st.form_submit_button(
            "Search", type="primary", use_container_width=True
        )

if search_clicked and query.strip():
    retrieved = store.query(query, top_k=top_k)
    answer, status = generate_answer(query, retrieved)
    label = STATUS_LABEL.get(status, "Answer")

    st.markdown(
        f"""
        <div class="mythos-card">
            <span class="mythos-label">{label}</span>
            <div class="mythos-answer">{answer}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    best_score = max((score for _, score in retrieved), default=0.0)
    is_relevant = best_score >= MIN_RELEVANCE_SCORE

    st.markdown('<span class="mythos-label" style="margin-left:4px;">Sources</span>', unsafe_allow_html=True)
    if not retrieved or not is_relevant:
        st.caption("No relevant sources found in the indexed documents for this query.")
    else:
        for chunk, score in retrieved:
            with st.expander(f"{chunk.doc_title}  ·  similarity {score:.2f}"):
                st.write(chunk.text)
elif search_clicked:
    st.warning("Type a question first.")