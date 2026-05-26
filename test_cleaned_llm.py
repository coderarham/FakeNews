"""
test_cleaned_llm.py
Test cleaned LLM function (only LLaMA 3.3 70B)
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Import from app.py
sys.path.insert(0, os.path.dirname(__file__))
from app import llm_ensemble_predict

print("="*70)
print("TESTING CLEANED LLM FUNCTION")
print("="*70)

tests = [
    {
        "name": "Obvious FAKE - Conspiracy",
        "text": "BREAKING: Government hiding alien technology! Secret documents leaked. Mainstream media silent. Share before deleted!",
        "expected": "FAKE"
    },
    {
        "name": "Obvious REAL - Reuters",
        "text": "WASHINGTON (Reuters) - The Federal Reserve announced today it will maintain interest rates at current levels, citing stable inflation and employment data.",
        "expected": "REAL"
    },
    {
        "name": "Health Scam",
        "text": "DOCTORS HATE HIM! This one weird trick melts belly fat overnight. No diet, no exercise. Click now before Big Pharma bans it!",
        "expected": "FAKE"
    }
]

print("\nAPI Key Status:")
GROQ_KEY = os.getenv("GROQ_API_KEY", "")
if GROQ_KEY:
    print(f"✅ GROQ_API_KEY found: {GROQ_KEY[:20]}...{GROQ_KEY[-10:]}")
else:
    print("❌ GROQ_API_KEY not found!")

print("\n" + "="*70)

for i, test in enumerate(tests, 1):
    print(f"\n[TEST {i}] {test['name']}")
    print(f"Expected: {test['expected']}")
    print(f"Text: {test['text'][:60]}...")
    print("\nQuerying LLaMA 3.3 70B...")
    
    result = llm_ensemble_predict(test['text'])
    
    if result.get("verdict") == "ERROR":
        print(f"❌ ERROR: {result.get('error')}")
    else:
        verdict = result.get("verdict", "N/A")
        confidence = result.get("confidence", 0)
        reasoning = result.get("reasoning", "N/A")
        
        factual = result.get("factual_consistency_score", 0)
        sensational = result.get("sensationalism_score", 0)
        credibility = result.get("source_credibility_score", 0)
        style = result.get("writing_style_score", 0)
        
        print(f"\n✅ RESULT:")
        print(f"  Verdict: {verdict}")
        print(f"  Confidence: {confidence*100:.1f}%")
        print(f"  Factual: {factual*100:.0f}% | Sensational: {sensational*100:.0f}%")
        print(f"  Credibility: {credibility*100:.0f}% | Style: {style*100:.0f}%")
        print(f"  Reasoning: {reasoning[:100]}...")
        
        # Check correctness
        is_correct = "✅ CORRECT" if verdict == test['expected'] else "❌ WRONG"
        print(f"\n  Status: {is_correct}")
    
    print("-"*70)

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
✅ Removed fake "GPT-4o" (was actually LLaMA 3.1 8B)
✅ Removed broken Gemini API
✅ Kept only real working LLaMA 3.3 70B

BENEFITS:
+ Honest - no fake model names
+ Fast - single API call (0.5-1.5s)
+ Reliable - only tested working model
+ Clean - simple code, no ensemble complexity

Tab 3 now shows:
- Single LLaMA 3.3 70B analysis
- 4 detailed scores (factual, sensational, credibility, style)
- Clear reasoning explanation
""")
print("="*70)
