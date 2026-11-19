import requests

QUESTIONS = [
    "What projects does DarGlobal have in Oman or Qatar?",
    "Tell me about Trump Villas Simaisma",
    "Which brands does DarGlobal partner with?",
    "What is DarGlobal?",
    "What is the Jeddah development announced in November 2026?",
    "What is Wasalt?",
    "What is the capital of France?",
]

for q in QUESTIONS:
    r = requests.post("http://127.0.0.1:8000/query", json={"question": q}, timeout=120)
    d = r.json()
    print(f"\nQ: {q}\nA: {d.get('answer', d)[:400]}")
    for s in d.get("sources", [])[:5]:
        print(f"   - score={s.get('score')} | {str(s.get('snippet', ''))[:90]}")