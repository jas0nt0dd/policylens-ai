"""
Semantic Analyzer — FAISS + sentence-transformers + spaCy
Embeds document clauses, runs NER, tags SDGs.
"""
import logging
from typing import List, Dict, Any

import numpy as np

logger = logging.getLogger("policylens.semantic")

# Demographic groups for equity analysis
DEMOGRAPHIC_GROUPS = [
    "women", "men", "children", "elderly", "disabled", "youth",
    "minority", "indigenous", "migrants", "refugees", "workers",
    "farmers", "poor", "rural", "urban", "scheduled caste", "scheduled tribe",
    "obc", "dalit", "adivasi",
]

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_embedding_model = None
_embedding_model_unavailable = False
_spacy_nlp = None
_spacy_unavailable = False


def analyze_semantics(parsed_doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Embed clauses, extract named entities, count demographic mentions.
    Returns enriched document with embeddings and NER results.
    """
    clauses = parsed_doc.get("clauses", [])
    full_text = parsed_doc.get("full_text", "")

    embeddings = _embed_clauses(clauses)
    ner_results = _run_ner(full_text)
    demographic_counts = _count_demographic_mentions(full_text)

    return {
        **parsed_doc,
        "embeddings": embeddings,
        "ner_results": ner_results,
        "demographic_mentions": demographic_counts,
    }


def _embed_clauses(clauses: List[Dict]) -> List[List[float]]:
    """Generate sentence embeddings for each clause."""
    model = _get_embedding_model()
    if model is None:
        return [[] for _ in clauses]

    try:
        texts = [c["text"] for c in clauses]
        if not texts:
            return []
        embeddings = model.encode(texts, batch_size=32, show_progress_bar=False)
        logger.info(f"Embedded {len(texts)} clauses")
        return embeddings.tolist()
    except Exception as e:
        logger.warning(f"Embedding failed: {e}. Returning empty embeddings.")
        return [[] for _ in clauses]


def _build_faiss_index(embeddings: List[List[float]]):
    """Build FAISS index for semantic similarity search."""
    try:
        import faiss
        if not embeddings or not embeddings[0]:
            return None
        matrix = np.array(embeddings, dtype=np.float32)
        dim = matrix.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(matrix)
        logger.info(f"FAISS index built with {len(embeddings)} vectors")
        return index
    except Exception as e:
        logger.warning(f"FAISS index build failed: {e}")
        return None


def _run_ner(text: str) -> Dict[str, List[str]]:
    """Named Entity Recognition using spaCy."""
    nlp = _get_spacy_model()
    if nlp is None:
        return {}

    try:
        # Process in chunks to avoid memory issues
        max_len = 100000
        text_chunk = text[:max_len]
        doc = nlp(text_chunk)
        entities: Dict[str, List[str]] = {}
        for ent in doc.ents:
            label = ent.label_
            if label not in entities:
                entities[label] = []
            if ent.text not in entities[label]:
                entities[label].append(ent.text)
        return entities
    except Exception as e:
        logger.warning(f"NER failed: {e}")
        return {}


def _get_embedding_model():
    """Load the embedding model once and prefer local cache over network fetches."""
    global _embedding_model, _embedding_model_unavailable

    if _embedding_model_unavailable:
        return None
    if _embedding_model is not None:
        return _embedding_model

    try:
        from huggingface_hub import snapshot_download
        from sentence_transformers import SentenceTransformer

        local_model_path = snapshot_download(
            repo_id=EMBEDDING_MODEL_NAME,
            local_files_only=True,
        )
        _embedding_model = SentenceTransformer(local_model_path)
        return _embedding_model
    except Exception as e:
        logger.warning(
            "Embedding model unavailable locally (%s). Falling back to empty embeddings.",
            e,
        )
        _embedding_model_unavailable = True
        return None


def _get_spacy_model():
    """Load and cache spaCy once to avoid repeated disk/model initialization."""
    global _spacy_nlp, _spacy_unavailable

    if _spacy_unavailable:
        return None
    if _spacy_nlp is not None:
        return _spacy_nlp

    try:
        import spacy

        _spacy_nlp = spacy.load("en_core_web_sm")
        return _spacy_nlp
    except OSError:
        logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
    except Exception as e:
        logger.warning(f"spaCy initialization failed: {e}")

    _spacy_unavailable = True
    return None


def _count_demographic_mentions(text: str) -> Dict[str, int]:
    """Count how many times each demographic group is mentioned."""
    text_lower = text.lower()
    counts = {}
    for group in DEMOGRAPHIC_GROUPS:
        count = text_lower.count(group.lower())
        if count > 0:
            counts[group] = count
    return counts


def find_similar_clauses(query_embedding: List[float], index, clauses: List[Dict], top_k: int = 5) -> List[Dict]:
    """Find semantically similar clauses using FAISS."""
    try:
        import faiss
        import numpy as np
        if index is None:
            return []
        query = np.array([query_embedding], dtype=np.float32)
        distances, indices = index.search(query, top_k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(clauses):
                results.append({**clauses[idx], "similarity_score": float(1 / (1 + dist))})
        return results
    except Exception as e:
        logger.warning(f"Similarity search failed: {e}")
        return []
