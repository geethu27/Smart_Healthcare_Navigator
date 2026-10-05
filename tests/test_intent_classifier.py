import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.intent_classifier import IntentClassifier

classifier = IntentClassifier()

test_cases = [
    "What is diabetes?",
    "Find me a dermatologist.",
    "Book appointment tomorrow.",
    "Write a Python program.",
    "Who is the Prime Minister of India?",
    "Severe crushing chest pain and shortness of breath",
    "I have had a high fever and chills since yesterday",
    "Please explain my CBC blood test report with low iron"
]

print("=" * 80)
for text in test_cases:
    res = classifier.classify(text)
    print(f"Query: '{text}'")
    print(f"  -> Intent: {res['intent']} | Routed To: {res['routed_to']} | Reason: {res['reason']}")
    if res.get('direct_response'):
        print(f"     Direct Response: {res['direct_response'][:70]}...")
print("=" * 80)
