import urllib.request
import json

def send_chat(msg):
    data = json.dumps({'message': msg, 'provider': 'local', 'threshold': 0.20}).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:8000/api/chat', data=data, headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode('utf-8'))

queries = [
    'hi',
    'fever',
    'cough and sore throat',
    'I feel tired and weak',
    'What are the symptoms of a rare neurological disorder?',
    'Who is the Prime Minister of India?'
]

print("=" * 70)
for query in queries:
    resp = send_chat(query)
    print(f"Query: '{query}'")
    print(f"  -> Intent: {resp['intent']} | Grounded: {resp['is_grounded']} | Score: {resp.get('rag_score', 0)}")
    print(f"  -> Response preview: {resp['response'][:90]}...")
print("=" * 70)
