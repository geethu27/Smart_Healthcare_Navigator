import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.rag_engine import MedicalRAGEngine
from core.llm_provider import generate_symptom_response

rag = MedicalRAGEngine()

# Test 1: In-Corpus Symptom
q1 = "I have a cough and sore throat for 3 days"
res1 = rag.search(q1)
ans1 = generate_symptom_response(q1, res1, provider_type="local")
print("=== TEST 1: IN-CORPUS SYMPTOM ===")
print("Query:", q1)
print("Is Relevant:", res1["is_relevant"], "Score:", res1["best_score"])
print("Generated Response:\n", ans1)

# Test 2: Out-of-Corpus Rare Condition
q2 = "What are the symptoms of a rare neurological disorder?"
res2 = rag.search(q2)
ans2 = generate_symptom_response(q2, res2, provider_type="local")
print("\n=== TEST 2: OUT-OF-CORPUS RARE CONDITION ===")
print("Query:", q2)
print("Is Relevant:", res2["is_relevant"], "Score:", res2["best_score"])
print("Generated Response:\n", ans2)
