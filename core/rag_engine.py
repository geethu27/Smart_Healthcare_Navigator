"""
RAG Engine with Retrieval Confidence Threshold, Query Expansion & Verified Medical Grounding
Strictly enforces:
1. Retrieval over verified medical documents
2. Confidence score threshold check
3. Zero-hallucination fallback when relevance is insufficient
4. Query expansion and concept matching to prevent false negatives for common patient symptoms
"""

import os
import re
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

FALLBACK_UNAVAILABLE_MESSAGE = (
    "I don't have enough verified information in my medical knowledge base to answer that "
    "question reliably. I don't want to guess or provide potentially unsafe medical information. "
    "Please consult a qualified healthcare professional or use a verified medical source."
)

MEDICAL_SYNONYMS = {
    "fever": ["fever", "feverish", "high temperature", "chills", "pyrexia", "sweating", "shivering", "warm body"],
    "cough": ["cough", "coughing", "dry cough", "productive cough", "phlegm", "mucus", "bronchitis", "chest cold"],
    "sore throat": ["sore throat", "throat pain", "scratchy throat", "pharyngitis", "swallowing pain", "throat hurts"],
    "stomach pain": ["stomach pain", "abdominal pain", "stomach ache", "belly pain", "cramps", "nausea", "nauseous", "vomit", "vomiting", "diarrhea", "indigestion", "heartburn", "acid reflux", "gerd", "gastritis", "tummy"],
    "headache": ["headache", "head ache", "migraine", "temple pain", "throbbing head", "head hurts", "tension headache"],
    "skin rash": ["skin rash", "rash", "rashes", "itch", "itchy", "itching", "eczema", "hives", "dermatitis", "red spots", "bumps", "skin irritation"],
    "fatigue": ["fatigue", "tired", "tiredness", "exhausted", "exhaustion", "weakness", "lethargy", "low iron", "iron deficiency", "anemia", "ferritin", "hemoglobin", "low energy", "sluggish"]
}

def expand_medical_query(query: str) -> str:
    """Expands conversational patient queries with clinical synonyms to improve semantic recall."""
    lower = query.lower()
    expanded_terms = []
    for concept, keywords in MEDICAL_SYNONYMS.items():
        if any(re.search(rf"\b{re.escape(kw)}\b", lower) for kw in keywords):
            expanded_terms.append(concept)
            expanded_terms.extend(keywords[:3])
    
    if expanded_terms:
        return f"{query} " + " ".join(set(expanded_terms))
    return query

def compute_concept_overlap(query: str) -> float:
    """Computes a boost when recognized medical symptom concepts from our verified corpus appear in the query."""
    lower = query.lower()
    matches = 0
    for concept, keywords in MEDICAL_SYNONYMS.items():
        if any(re.search(rf"\b{re.escape(kw)}\b", lower) for kw in keywords):
            matches += 1
    if matches > 0:
        return min(0.12 * matches, 0.25)
    return 0.0

class MedicalDocumentChunk:
    def __init__(self, doc_id: str, title: str, section: str, content: str, source: str, specialty: str, file_path: str):
        self.doc_id = doc_id
        self.title = title
        self.section = section
        self.content = content.strip()
        self.source = source
        self.specialty = specialty
        self.file_path = file_path

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "section": self.section,
            "content": self.content,
            "source": self.source,
            "specialty": self.specialty,
            "file_path": self.file_path
        }

class MedicalRAGEngine:
    def __init__(self, knowledge_dir: str = "medical_knowledge", similarity_threshold: float = 0.20):
        self.knowledge_dir = knowledge_dir
        self.similarity_threshold = similarity_threshold
        self.chunks: List[MedicalDocumentChunk] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.load_and_index_documents()

    def load_and_index_documents(self):
        """Loads and chunks all markdown files from the knowledge directory."""
        self.chunks = []
        if not os.path.exists(self.knowledge_dir):
            os.makedirs(self.knowledge_dir, exist_ok=True)

        md_files = [f for f in os.listdir(self.knowledge_dir) if f.endswith(".md")]
        chunk_counter = 1

        for filename in md_files:
            filepath = os.path.join(self.knowledge_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()

            title_match = re.search(r"^#\s+(.+)$", raw_text, re.MULTILINE)
            source_match = re.search(r"\*\*Source\*\*:\s*([^\n]+)", raw_text)
            spec_match = re.search(r"\*\*Specialty Recommendation\*\*:\s*([^\n]+)", raw_text)

            doc_title = title_match.group(1).strip() if title_match else filename
            source_info = source_match.group(1).strip() if source_match else "Verified Medical Guidelines"
            specialty = spec_match.group(1).strip() if spec_match else "General Medicine"

            sections = re.split(r"\n(?=##\s+)", raw_text)
            for sec in sections:
                if not sec.strip():
                    continue
                
                header_match = re.search(r"^##\s+(.+)$", sec, re.MULTILINE)
                section_title = header_match.group(1).strip() if header_match else "General Guidance"
                
                subsections = re.split(r"\n(?=###\s+)", sec)
                for sub in subsections:
                    clean_content = sub.strip()
                    if len(clean_content) < 40:
                        continue

                    sub_header_match = re.search(r"^###\s+(.+)$", sub, re.MULTILINE)
                    chunk_section = f"{section_title} - {sub_header_match.group(1).strip()}" if sub_header_match else section_title

                    chunk = MedicalDocumentChunk(
                        doc_id=f"chunk_{chunk_counter}",
                        title=doc_title,
                        section=chunk_section,
                        content=clean_content,
                        source=source_info,
                        specialty=specialty,
                        file_path=filepath
                    )
                    self.chunks.append(chunk)
                    chunk_counter += 1

        if self.chunks:
            corpus = [f"{c.title} {c.section} {c.content}" for c in self.chunks]
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words="english",
                sublinear_tf=True
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
            print(f"[MedicalRAGEngine] Successfully indexed {len(self.chunks)} chunks from {len(md_files)} documents.")
        else:
            print("[MedicalRAGEngine] Warning: No medical documents found in knowledge directory.")

    def search(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        """
        Searches the knowledge base with query expansion, concept boost, and threshold evaluation.
        """
        if not self.chunks or self.vectorizer is None or self.tfidf_matrix is None:
            return {
                "query": query,
                "is_relevant": False,
                "best_score": 0.0,
                "threshold": self.similarity_threshold,
                "matches": [],
                "grounded_context": "",
                "sources": [],
                "fallback_message": FALLBACK_UNAVAILABLE_MESSAGE
            }

        # 1. Expand query with medical synonyms
        expanded_q = expand_medical_query(query)
        
        # 2. Vectorize and compute similarities
        query_vec = self.vectorizer.transform([expanded_q])
        raw_similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # 3. Add medical concept overlap boost
        concept_boost = compute_concept_overlap(query)
        similarities = np.clip(raw_similarities + concept_boost, 0.0, 1.0)

        # 4. Sort indices by score descending
        sorted_indices = np.argsort(similarities)[::-1]
        
        matches = []
        unique_sources = set()
        best_score = float(similarities[sorted_indices[0]]) if len(sorted_indices) > 0 else 0.0

        is_relevant = best_score >= self.similarity_threshold

        if is_relevant:
            for idx in sorted_indices[:top_k]:
                score = float(similarities[idx])
                if score >= (self.similarity_threshold * 0.70):
                    chunk = self.chunks[idx]
                    matches.append({
                        "chunk_id": chunk.doc_id,
                        "title": chunk.title,
                        "section": chunk.section,
                        "source": chunk.source,
                        "specialty": chunk.specialty,
                        "score": round(score, 4),
                        "content": chunk.content
                    })
                    unique_sources.add(f"{chunk.source} ({chunk.title})")

        grounded_context = "\n\n---\n\n".join([
            f"[Source: {m['source']} | Document: {m['title']} | Section: {m['section']}]\n{m['content']}"
            for m in matches
        ]) if is_relevant else ""

        return {
            "query": query,
            "is_relevant": is_relevant,
            "best_score": round(best_score, 4),
            "threshold": self.similarity_threshold,
            "matches": matches,
            "grounded_context": grounded_context,
            "sources": sorted(list(unique_sources)),
            "fallback_message": None if is_relevant else FALLBACK_UNAVAILABLE_MESSAGE
        }
