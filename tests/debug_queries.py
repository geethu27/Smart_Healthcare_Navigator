import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.rag_engine import MedicalRAGEngine
rag = MedicalRAGEngine(similarity_threshold=0.15)
test_queries = [
    'fever',
    'I have fever',
    'headache',
    'cough',
    'I have a cough',
    'stomach pain',
    'skin rash',
    'I feel tired',
    'vomiting',
    'What should I do if I have fever?',
    'I have high temperature and body chills',
    'sore throat and runny nose',
    'I have fever and headache',
    'hi',
    'hello'
]
for q in test_queries:
    r = rag.search(q)
    print(f"{q:<45} -> relevant: {str(r['is_relevant']):<5} | score: {r['best_score']:.4f}")
