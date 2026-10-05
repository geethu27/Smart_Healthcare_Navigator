import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.rag_engine import MedicalRAGEngine
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

MEDICAL_SYNONYMS = {
    "fever": ["fever", "feverish", "high temperature", "chills", "pyrexia", "sweating", "shivering"],
    "cough": ["cough", "coughing", "dry cough", "productive cough", "phlegm", "mucus", "bronchitis", "chest cold"],
    "sore throat": ["sore throat", "throat pain", "scratchy throat", "pharyngitis", "swallowing pain", "throat hurts"],
    "stomach pain": ["stomach pain", "abdominal pain", "stomach ache", "belly pain", "cramps", "nausea", "nauseous", "vomit", "vomiting", "diarrhea", "indigestion", "heartburn", "acid reflux", "gerd", "gastritis"],
    "headache": ["headache", "head ache", "migraine", "temple pain", "throbbing head", "head hurts", "tension headache"],
    "skin rash": ["skin rash", "rash", "rashes", "itch", "itchy", "itching", "eczema", "hives", "dermatitis", "red spots", "bumps"],
    "fatigue": ["fatigue", "tired", "tiredness", "exhausted", "exhaustion", "weakness", "lethargy", "low iron", "iron deficiency", "anemia", "ferritin", "hemoglobin", "low energy", "sluggish"]
}

def expand_query(query: str) -> str:
    lower = query.lower()
    expanded_terms = []
    for concept, keywords in MEDICAL_SYNONYMS.items():
        if any(kw in lower for kw in keywords):
            expanded_terms.append(concept)
            expanded_terms.extend(keywords[:3])
    
    if expanded_terms:
        return f"{query} " + " ".join(set(expanded_terms))
    return query

rag = MedicalRAGEngine(similarity_threshold=0.18)

test_queries = [
    'fever',
    'I have fever',
    'headache',
    'cough',
    'I have a cough',
    'stomach pain',
    'stomach ache',
    'skin rash',
    'I feel tired and weak',
    'vomiting',
    'What should I do if I have fever?',
    'I have high temperature and body chills',
    'sore throat and runny nose',
    'What are the symptoms of a rare neurological disorder?',
    'Who is the Prime Minister of India?',
    'How to build a website?'
]

print("-" * 75)
for q in test_queries:
    exp = expand_query(q)
    query_vec = rag.vectorizer.transform([exp])
    sims = cosine_similarity(query_vec, rag.tfidf_matrix).flatten()
    best_idx = np.argmax(sims)
    best_score = float(sims[best_idx])
    is_rel = best_score >= 0.18
    print(f"{q:<45} | Score: {best_score:.4f} | Relevant: {is_rel}")
print("-" * 75)
