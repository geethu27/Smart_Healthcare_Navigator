import re

KNOWN_CORPUS_CONCEPTS = {
    "fever": ["fever", "feverish", "pyrexia", "temperature", "chills", "shivering"],
    "cough": ["cough", "coughing", "phlegm", "mucus", "bronchitis"],
    "sore throat": ["sore throat", "throat pain", "pharyngitis", "scratchy throat"],
    "stomach": ["stomach", "abdominal", "cramp", "nausea", "vomit", "vomiting", "diarrhea", "indigestion", "heartburn", "acid reflux"],
    "headache": ["headache", "migraine", "throbbing head", "temple pain"],
    "skin": ["rash", "rashes", "itch", "itchy", "eczema", "hives", "dermatitis"],
    "fatigue": ["fatigue", "tired", "tiredness", "exhausted", "exhaustion", "weakness", "lethargy", "low iron", "anemia"]
}

def compute_concept_boost(query: str) -> float:
    lower = query.lower()
    matches = 0
    for concept, keywords in KNOWN_CORPUS_CONCEPTS.items():
        if any(re.search(rf"\b{re.escape(kw)}\b", lower) for kw in keywords):
            matches += 1
    if matches > 0:
        return min(0.12 * matches, 0.25)
    return 0.0

queries = [
    ("fever", 0.2105),
    ("headache", 0.1669),
    ("cough", 0.1787),
    ("I have fever and headache", 0.22),
    ("I feel tired and weak", 0.1841),
    ("vomiting and stomach ache", 0.30),
    ("What are the symptoms of a rare neurological disorder?", 0.1168),
    ("Who is the Prime Minister of India?", 0.0000)
]

print("-" * 65)
for q, raw_score in queries:
    boost = compute_concept_boost(q)
    final_score = min(raw_score + boost, 1.0)
    is_rel = final_score >= 0.20
    print(f"{q:<45} | Raw: {raw_score:.3f} | +Boost: {boost:.2f} | Final: {final_score:.3f} | >=0.20: {is_rel}")
print("-" * 65)
