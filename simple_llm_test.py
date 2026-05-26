"""
simple_llm_test.py
Simple test for cleaned LLM (LLaMA only)
"""

import os
from dotenv import load_dotenv
from groq import Groq
import json
import re

load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY", "")

print("="*70)
print("SIMPLE LLM TEST - LLaMA 3.3 70B ONLY")
print("="*70)

if not GROQ_KEY:
    print("\nERROR: No API key!")
    exit(1)

print(f"\nAPI Key: {GROQ_KEY[:20]}...{GROQ_KEY[-10:]}")

client = Groq(api_key=GROQ_KEY)

test_text = "BREAKING: Government hiding alien technology! Secret documents leaked!"

prompt = f"""Analyze this article for fake news.
Respond with JSON:
{{"verdict": "REAL/FAKE", "confidence": 0.0-1.0, "reasoning": "brief"}}

ARTICLE: {test_text}"""

print(f"\nTest Article: {test_text}")
print("\nQuerying LLaMA 3.3 70B...")

resp = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3,
    max_tokens=200
)

raw = resp.choices[0].message.content
print(f"\nRaw Response:\n{raw}")

match = re.search(r'\{.*\}', raw, re.DOTALL)
if match:
    result = json.loads(match.group())
    print(f"\nParsed Result:")
    print(f"  Verdict: {result.get('verdict')}")
    print(f"  Confidence: {result.get('confidence')*100:.1f}%")
    print(f"  Reasoning: {result.get('reasoning')}")
    print("\nSUCCESS: LLaMA 3.3 70B is working!")
else:
    print("\nERROR: Could not parse JSON")

print("\n" + "="*70)
print("CLEANED APP.PY STATUS")
print("="*70)
print("""
REMOVED:
- Fake "GPT-4o" (was actually LLaMA 3.1 8B)
- Broken Gemini API

KEPT:
- LLaMA 3.3 70B (real, working, 70 billion parameters)

Tab 3 now shows:
- Single LLaMA model
- 4 detailed scores
- Clear reasoning
- No fake ensemble
""")
print("="*70)
