"""
expose_fake_gpt.py
Expose the fake GPT-4o in LLM ensemble
"""

import os
import json
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_KEY)

test_text = "Breaking: Scientists discover water is wet."

prompt = f"""Analyze this article. Respond with JSON:
{{"verdict": "REAL/FAKE", "confidence": 0.0-1.0, "reasoning": "brief"}}

ARTICLE: {test_text}"""

print("="*70)
print("EXPOSING FAKE GPT-4o")
print("="*70)

# Test 1: Real LLaMA 3.3 70B
print("\n[TEST 1] Real LLaMA 3.3 70B:")
resp1 = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3,
    max_tokens=200
)
print(f"Model: llama-3.3-70b-versatile")
print(f"Response: {resp1.choices[0].message.content[:150]}")

# Test 2: Fake "GPT-4o" (actually LLaMA 3.1 8B)
print("\n[TEST 2] Fake 'GPT-4o' (actually LLaMA 3.1 8B):")
resp2 = client.chat.completions.create(
    model="llama-3.1-8b-instant",  # This is what app.py uses for "GPT-4o"
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3,
    max_tokens=200
)
print(f"Model: llama-3.1-8b-instant")
print(f"Response: {resp2.choices[0].message.content[:150]}")

# Test 3: Check available models
print("\n[TEST 3] Available Groq Models:")
models = client.models.list()
print("Models available on Groq:")
for m in models.data:
    print(f"  - {m.id}")

print("\n" + "="*70)
print("VERDICT")
print("="*70)
print("""
❌ GPT-4o is NOT available on Groq API
❌ app.py uses llama-3.1-8b-instant and calls it "GPT-4o"
❌ This is misleading - it's just another LLaMA model

ACTUAL LLM ENSEMBLE:
1. LLaMA 3.3 70B (real, working)
2. LLaMA 3.1 8B (fake name: "GPT-4o")
3. Gemini 2.5 Flash (real, but API issues)

RECOMMENDATION:
Either get real OpenAI API key for GPT-4o,
or rename "GPT-4o" to "LLaMA 3.1 8B" for honesty!
""")
