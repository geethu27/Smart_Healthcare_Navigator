import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.rag_engine import MedicalRAGEngine

rag = MedicalRAGEngine(similarity_threshold=0.15)
queries = [
    "What are common symptoms associated with fever?",
    "I have a persistent cough and sore throat for 3 days",
    "My stomach is cramping and feeling nauseous",
    "I have an itchy red skin rash on my arms",
    "What are the symptoms of a rare neurological disorder?",
    "Who is the Prime Minister of India?",
    "How to build a quantum computer?"
]

print("-" * 70)
for q in queries:
    res = rag.search(q)
    top_chunk = res['matches'][0]['title'] if res['matches'] else 'None'
    print(f"Query: '{q}'")
    print(f"  -> Grounded in KB: {res['is_relevant']} | Score: {res['best_score']} (Threshold: {res['threshold']}) | Top Doc: {top_chunk}")
print("-" * 70)
