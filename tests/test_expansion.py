import re

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
            # Add primary terms
            expanded_terms.extend(keywords[:3])
    
    if expanded_terms:
        return f"{query} " + " ".join(set(expanded_terms))
    return query

print("Original: 'I feel tired'")
print("Expanded:", expand_query("I feel tired"))
print("\nOriginal: 'my stomach hurts and vomiting'")
print("Expanded:", expand_query("my stomach hurts and vomiting"))
print("\nOriginal: 'rare neurological disorder'")
print("Expanded:", expand_query("rare neurological disorder"))
