# Mythos Search - RAG-Based AI Search System

Mythos Search is a retrieval-augmented generation (RAG) search system that answers questions about world mythology and folklore using a collection of 23 documents. The collection includes Greek, Norse, Egyptian, Japanese, Chinese, Hindu, Celtic, Aztec, Native American, Slavic, West African, Polynesian, and Mesopotamian mythology, as well as documents covering shared themes such as flood myths, creation myths, trickster figures, and the hero's journey.

This project was developed for the **CS382 Final Project**.

---

# Setup

### 1. Install Python 3.11 or 3.12

This project was developed and tested using Python 3.11 and 3.12. Python 3.14 may cause compatibility issues with Streamlit (see **Known Limitations**).

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install the required packages

```powershell
pip install -r requirements.txt
```

### 4. Get a free Groq API key

The language model used in this project runs through the Groq API.

* Sign up at https://console.groq.com
* Create a new API key under **API Keys**

### 5. Set the API key

```powershell
$env:GROQ_API_KEY = "your-key-here"
```

### 6. Run the application

```powershell
python -m streamlit run app.py
```

**Note:** The first time the application is started, the sentence-transformer embedding model (approximately 90 MB) will be downloaded automatically. This only happens once.

---

# System Architecture

```
Raw Documents
      ↓
Document Loading & Chunking
      ↓
Embedding & Vector Store
      ↓
Similarity Retrieval
      ↓
LLM Response Generation
      ↓
Streamlit User Interface
```

| Stage                       | File                                       | Description                                                                                                                                       |
| --------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Document Loading & Chunking | `rag/ingest.py`                            | Loads all `.txt` files from `data/mythology_docs/` and splits them into overlapping chunks (80 words with a 20-word overlap).                     |
| Embedding & Storage         | `rag/embed_store.py`                       | Converts each chunk into dense vector embeddings using `sentence-transformers` (`all-MiniLM-L6-v2`) and stores them for cosine similarity search. |
| Retrieval                   | `rag/embed_store.py` (`VectorStore.query`) | Embeds the user's query, compares it with all document chunks, and returns the most relevant results.                                             |
| Response Generation         | `rag/generate.py`                          | Creates a grounded prompt using the retrieved chunks and generates an answer with Llama 3.3 70B through the Groq API.                             |
| User Interface              | `app.py`                                   | Streamlit application containing the search interface, answer display, Sources panel, and adjustable `top_k` value.                               |

---

# Key Design Decisions

### Embeddings instead of TF-IDF

The system uses sentence-transformer embeddings instead of TF-IDF for retrieval. This allows queries to be matched based on their meaning rather than only exact keywords. As a result, the system can often retrieve relevant information even when the query shares few or no words with the documents.

### Relevance Threshold

A relevance threshold (`MIN_RELEVANCE_SCORE = 0.32`) is used before generating an answer. If the highest similarity score falls below this threshold, the system rejects the query as being outside the document collection instead of sending it to the language model. This reduces unnecessary API calls and helps keep responses focused on the available documents.

### Basic Prompt Injection Protection

The generation prompt instructs the language model to ignore instructions contained within retrieved documents or user queries that attempt to override its behaviour or reveal internal information. Together with the relevance threshold, this helps reduce the impact of prompt injection attempts by limiting responses to the indexed mythology collection.

### Graceful Failure Handling

If the Groq API is unavailable, the API key is missing, or the request fails for another reason, the application automatically falls back to displaying the retrieved document chunks instead of a generated answer. This allows the application to continue functioning instead of crashing.

### Sources Panel

Instead of placing citations directly inside the generated response, the application displays the retrieved document names and similarity scores in a Sources panel. This keeps the generated answer easier to read while still allowing users to see where the information came from.

---

# Known Limitations

### Typo Sensitivity

The embedding model handles some spelling mistakes better than others. Missing-letter typos such as **"japnese"** are usually retrieved correctly, while substitution typos such as **"chanese"** may retrieve the wrong document because of how the embedding model represents words. This limitation was documented rather than addressed because implementing typo correction was outside the scope of this project.

### Dataset Coverage

The collection contains only 23 documents, so some questions cannot be answered perfectly. For example, asking about a sea deity retrieves the closest related document because the collection does not contain a document specifically about sea gods. This is a limitation of the dataset rather than the retrieval system.

### Groq API Limits

Answer generation depends on the Groq API, which has free-tier rate limits. If requests fail because of network issues or rate limits, the application automatically falls back to extractive retrieval mode.

### Small Embedding Model

The project uses `all-MiniLM-L6-v2` because it runs locally, is free to use, and works well on CPU-only systems. However, larger embedding models generally provide more accurate retrieval.

### Python Compatibility

The project was developed and tested using Python 3.11 and 3.12. Python 3.14 may produce asyncio-related shutdown errors with Streamlit, so Python 3.11 or 3.12 is recommended.

---

# Project Structure

```
final_project_starter/
├── app.py
├── requirements.txt
├── README.md
├── evaluation.md
├── .streamlit/
│   └── config.toml
├── data/
│   └── mythology_docs/
└── rag/
    ├── ingest.py
    ├── embed_store.py
    └── generate.py
```

---

# Conclusion

Mythos Search demonstrates the core ideas behind a retrieval-augmented generation (RAG) system by combining semantic search, document retrieval, grounded answer generation, and graceful error handling. While the project has some limitations, such as a relatively small document collection and the use of a lightweight embedding model, it successfully meets the project requirements and provides accurate, collection-based responses to mythology-related questions.
