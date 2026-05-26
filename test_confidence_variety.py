"""
test_confidence_variety.py
Test LLaMA with different article types to see confidence variation
"""

import requests
import time

articles = [
    {
        "name": "OBVIOUS FAKE - Conspiracy",
        "text": "BREAKING: NASA Scientists Confirm Aliens Living Among Us! Secret government documents leaked. Mainstream media covering it up!",
        "expected_confidence": "90-95% (very high)"
    },
    {
        "name": "OBVIOUS REAL - Reuters",
        "text": "WASHINGTON (Reuters) - The Federal Reserve announced Wednesday it will maintain interest rates at current levels, citing stable inflation and employment data. Fed Chair Jerome Powell stated the central bank will continue monitoring economic indicators.",
        "expected_confidence": "60-70% (cautious on real news)"
    },
    {
        "name": "HEALTH SCAM - Clickbait",
        "text": "DOCTORS HATE HIM! This one weird trick melts belly fat overnight. No diet, no exercise needed. Big Pharma doesn't want you to know. Click now before government bans it!",
        "expected_confidence": "95-99% (extremely obvious fake)"
    },
    {
        "name": "AMBIGUOUS - Vague Opinion",
        "text": "Some experts believe the economy may face challenges in coming months. Various factors could influence market conditions. Analysts remain divided on potential outcomes.",
        "expected_confidence": "40-60% (uncertain)"
    },
    {
        "name": "NEUTRAL - Dry Fact",
        "text": "The meeting was held on Tuesday. Several participants attended. Topics were discussed. No decisions were announced.",
        "expected_confidence": "50-60% (very uncertain)"
    }
]

print("="*70)
print("TESTING CONFIDENCE VARIATION ACROSS DIFFERENT ARTICLE TYPES")
print("="*70)

results = []

for i, article in enumerate(articles, 1):
    print(f"\n[TEST {i}/5] {article['name']}")
    print(f"Expected: {article['expected_confidence']}")
    print(f"Text: {article['text'][:60]}...")
    print("Querying LLaMA 3.3 70B...")
    
    try:
        response = requests.post(
            "http://localhost:5000/api/predict/llm",
            json={"text": article['text']},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            verdict = data.get('verdict', 'N/A')
            confidence = data.get('confidence', 0) * 100
            reasoning = data.get('reasoning', 'N/A')[:80]
            
            print(f"\nResult:")
            print(f"  Verdict: {verdict}")
            print(f"  Confidence: {confidence:.1f}%")
            print(f"  Reasoning: {reasoning}...")
            
            results.append({
                'name': article['name'],
                'verdict': verdict,
                'confidence': confidence,
                'expected': article['expected_confidence']
            })
        else:
            print(f"  ERROR: HTTP {response.status_code}")
            results.append({
                'name': article['name'],
                'verdict': 'ERROR',
                'confidence': 0,
                'expected': article['expected_confidence']
            })
    
    except Exception as e:
        print(f"  ERROR: {str(e)[:50]}")
        results.append({
            'name': article['name'],
            'verdict': 'ERROR',
            'confidence': 0,
            'expected': article['expected_confidence']
        })
    
    time.sleep(1)  # Rate limiting

print("\n" + "="*70)
print("SUMMARY - CONFIDENCE VARIATION")
print("="*70)

for r in results:
    status = "OK" if r['confidence'] > 0 else "ERR"
    print(f"[{status}] {r['name'][:35]:35s} -> {r['verdict']:10s} ({r['confidence']:5.1f}%)")

print("\n" + "="*70)
print("ANALYSIS")
print("="*70)
print("""
WHY CONFIDENCE VARIES:

1. OBVIOUS FAKE (90-99%):
   - Clear red flags (BREAKING, clickbait, conspiracy)
   - LLaMA very confident it's fake
   
2. OBVIOUS REAL (60-70%):
   - Credible sources (Reuters, Fed)
   - But LLaMA is CAUTIOUS - doesn't want to say 100% real
   - Prefers saying "uncertain" over confidently saying "real"
   
3. HEALTH SCAM (95-99%):
   - MOST obvious fake (DOCTORS HATE HIM, weird trick)
   - Highest confidence
   
4. AMBIGUOUS (40-60%):
   - Vague, no clear signals
   - Low confidence = honest uncertainty
   
5. NEUTRAL (50-60%):
   - Dry facts, no emotion
   - LLaMA can't decide = low confidence

KEY INSIGHT:
LLaMA is BETTER at detecting FAKE than confirming REAL.
This is GOOD for fake news detection - better to be cautious!
""")
print("="*70)
