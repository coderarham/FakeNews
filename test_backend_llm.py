"""
test_backend_llm.py
Test if backend is using REAL LLaMA API or FAKE mock responses
"""

import requests
import json

print("="*70)
print("TESTING BACKEND LLM ENDPOINT")
print("="*70)

url = "http://localhost:5000/api/predict/llm"
test_text = "BREAKING: NASA Scientists Confirm Aliens Living Among Us!"

print(f"\nSending request to: {url}")
print(f"Test text: {test_text}")

try:
    response = requests.post(
        url,
        json={"text": test_text},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n" + "="*70)
        print("RESPONSE RECEIVED")
        print("="*70)
        
        # Check if it's the OLD mock format (3 models)
        if 'llama' in data and 'gpt4' in data and 'gemini' in data:
            print("\n[X] BACKEND NOT UPDATED!")
            print("    Still using OLD mock responses with 3 fake LLMs")
            print("\n    Response structure:")
            print(f"    - llama: {data['llama']['verdict']} ({data['llama']['confidence']*100:.0f}%)")
            print(f"    - gpt4: {data['gpt4']['verdict']} ({data['gpt4']['confidence']*100:.0f}%)")
            print(f"    - gemini: {data['gemini']['verdict']} ({data['gemini']['confidence']*100:.0f}%)")
            print("\n    ACTION REQUIRED:")
            print("    1. Stop backend (Ctrl+C)")
            print("    2. Restart: python backend_api.py")
            print("    3. Run this test again")
        
        # Check if it's the NEW format (single LLaMA)
        elif 'verdict' in data and 'confidence' in data and 'model' in data:
            print("\n[OK] BACKEND UPDATED!")
            print("    Using NEW real LLaMA 3.3 70B API")
            print("\n    Response:")
            print(f"    Model: {data.get('model', 'N/A')}")
            print(f"    Verdict: {data['verdict']}")
            print(f"    Confidence: {data['confidence']*100:.1f}%")
            print(f"    Reasoning: {data['reasoning'][:80]}...")
            print(f"\n    Metrics:")
            print(f"    - Factual: {data['metrics']['factual']*100:.0f}%")
            print(f"    - Sensationalism: {data['metrics']['sensationalism']*100:.0f}%")
            print(f"    - Credibility: {data['metrics']['credibility']*100:.0f}%")
            print(f"    - Style: {data['metrics']['style']*100:.0f}%")
            print("\n    SUCCESS: Backend is using real LLaMA API!")
        
        else:
            print("\n[?] UNKNOWN RESPONSE FORMAT")
            print(json.dumps(data, indent=2))
    
    else:
        print(f"\n[ERROR] HTTP {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n[ERROR] Cannot connect to backend!")
    print("        Make sure backend is running on port 5000")
    print("        Run: python backend_api.py")

except Exception as e:
    print(f"\n[ERROR] {str(e)}")

print("\n" + "="*70)
