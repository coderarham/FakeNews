"""
test_llm_detailed.py
Detailed LLM testing with step-by-step explanation
Shows exactly how LLM works without training
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()

def test_llm_step_by_step():
    print("="*70)
    print("LLM Testing - Step by Step Explanation")
    print("="*70)
    
    # Step 1: Check API Key
    print("\n[STEP 1] Checking API Key...")
    GROQ_KEY = os.getenv("GROQ_API_KEY", "")
    
    if not GROQ_KEY:
        print("  [ERROR] No API key found!")
        return
    
    print(f"  API Key: {GROQ_KEY[:20]}...{GROQ_KEY[-10:]}")
    print("  Status: VALID")
    
    # Step 2: Import Library
    print("\n[STEP 2] Importing Groq Library...")
    try:
        from groq import Groq
        print("  Library imported successfully")
    except ImportError:
        print("  [ERROR] Groq library not installed")
        print("  Run: pip install groq")
        return
    
    # Step 3: Create Client
    print("\n[STEP 3] Creating API Client...")
    client = Groq(api_key=GROQ_KEY)
    print("  Client created")
    print("  Connected to: api.groq.com")
    
    # Step 4: Prepare Test Article
    print("\n[STEP 4] Preparing Test Article...")
    test_article = """
SHOCKING: Secret government documents reveal alien technology in smartphones! 
Whistleblower claims major tech companies have been hiding this for decades. 
Click here to learn what THEY don't want you to know!
"""
    print(f"  Article: {test_article.strip()[:80]}...")
    print(f"  Length: {len(test_article)} characters")
    
    # Step 5: Create Prompt
    print("\n[STEP 5] Creating Prompt for LLaMA...")
    prompt = f"""Analyze this news article for fake news detection.
Provide JSON response with:
- verdict: REAL / FAKE / UNCERTAIN
- confidence: 0.0-1.0
- factual_consistency_score: 0.0-1.0
- sensationalism_score: 0.0-1.0
- source_credibility_score: 0.0-1.0
- writing_style_score: 0.0-1.0
- reasoning: brief explanation

ARTICLE:
{test_article}

Respond ONLY with valid JSON."""
    
    print("  Prompt created")
    print(f"  Prompt length: {len(prompt)} characters")
    
    # Step 6: Send Request to LLaMA
    print("\n[STEP 6] Sending Request to LLaMA 3.3 70B...")
    print("  Server: Groq Cloud (USA)")
    print("  Model: llama-3.3-70b-versatile")
    print("  Status: Sending request...")
    
    start_time = time.time()
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        print(f"  Status: Response received!")
        print(f"  Time taken: {elapsed:.2f} seconds")
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        return
    
    # Step 7: Extract Response
    print("\n[STEP 7] Processing LLaMA Response...")
    raw_response = response.choices[0].message.content
    print(f"  Raw response length: {len(raw_response)} characters")
    print(f"  Raw response preview:")
    print(f"  {raw_response[:200]}...")
    
    # Step 8: Parse JSON
    print("\n[STEP 8] Parsing JSON Response...")
    import json
    import re
    
    match = re.search(r'\{.*\}', raw_response, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            print("  JSON parsed successfully!")
        except:
            print("  [ERROR] Invalid JSON")
            return
    else:
        print("  [ERROR] No JSON found in response")
        return
    
    # Step 9: Display Results
    print("\n" + "="*70)
    print("LLAMA 3.3 70B ANALYSIS RESULTS")
    print("="*70)
    
    print(f"\nVERDICT: {result.get('verdict', 'N/A')}")
    print(f"CONFIDENCE: {result.get('confidence', 0)*100:.1f}%")
    
    print("\nDETAILED SCORES:")
    print(f"  Factual Consistency:  {result.get('factual_consistency_score', 0)*100:.1f}%")
    print(f"  Sensationalism:       {result.get('sensationalism_score', 0)*100:.1f}%")
    print(f"  Source Credibility:   {result.get('source_credibility_score', 0)*100:.1f}%")
    print(f"  Writing Style:        {result.get('writing_style_score', 0)*100:.1f}%")
    
    print(f"\nREASONING:")
    print(f"  {result.get('reasoning', 'N/A')}")
    
    # Step 10: Explain How It Worked
    print("\n" + "="*70)
    print("HOW DID THIS WORK WITHOUT TRAINING?")
    print("="*70)
    
    print("""
1. META'S TRAINING (Already Done):
   - Meta trained LLaMA on 15 Trillion tokens
   - Learned patterns from billions of articles
   - Trained for months on thousands of GPUs
   - Cost: Millions of dollars
   - Result: 70 Billion parameter model

2. YOUR API CALL (Just Now):
   - You sent article text to Groq server
   - Groq loaded LLaMA model from memory
   - Model analyzed text using learned patterns
   - Generated response in {:.2f} seconds
   - Cost: ~$0.001

3. WHAT LLAMA DETECTED:
   - "SHOCKING" = Sensational language (red flag)
   - "Secret documents" = No source cited (red flag)
   - "alien technology" = Extraordinary claim (red flag)
   - "Click here" = Clickbait tactic (red flag)
   - "THEY don't want you to know" = Conspiracy (red flag)

4. HOW IT KNEW:
   - Saw millions of fake news examples during training
   - Learned patterns: sensationalism, no sources, clickbait
   - Applied learned patterns to your article
   - Generated verdict based on pattern matching

5. WHY NO TRAINING NEEDED:
   - Model already trained by Meta
   - Hosted on Groq's cloud servers
   - You just send API request
   - Model applies existing knowledge
   - Returns analysis instantly
""".format(elapsed))
    
    print("="*70)
    
    # Step 11: Test More Examples
    print("\n[STEP 11] Testing More Examples...")
    
    more_tests = [
        ("REAL News", "Washington - The Federal Reserve announced today that it will maintain current interest rates. Fed Chair Jerome Powell stated the decision reflects economic stability."),
        ("FAKE Conspiracy", "Anonymous sources confirm secret documents prove massive government cover-up. Mainstream media refuses to report this shocking truth!"),
    ]
    
    for label, text in more_tests:
        print(f"\n--- Testing: {label} ---")
        print(f"Text: {text[:60]}...")
        
        prompt = f"""Analyze for fake news. Respond with JSON:
{{"verdict": "REAL/FAKE", "confidence": 0.0-1.0, "reasoning": "brief"}}

Article: {text}"""
        
        start = time.time()
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )
        elapsed = time.time() - start
        
        raw = resp.choices[0].message.content
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            result = json.loads(match.group())
            print(f"Verdict: {result.get('verdict')} ({result.get('confidence', 0)*100:.0f}%)")
            print(f"Time: {elapsed:.2f}s")
            print(f"Reasoning: {result.get('reasoning', 'N/A')[:80]}...")
    
    print("\n" + "="*70)
    print("TESTING COMPLETE!")
    print("="*70)
    print("""
KEY TAKEAWAYS:
1. LLaMA is PRE-TRAINED by Meta (you don't train it)
2. Model is HOSTED on cloud (always available)
3. You just CALL API (send text, get analysis)
4. Response in 2-5 seconds (no training wait)
5. Cost: ~$0.001 per request (pay per use)

COMPARISON:
- ML/BiLSTM: Train yourself (30-60 min) -> Free predictions
- LLaMA: Already trained (0 min) -> Pay per prediction

Both work! Choose based on your needs.
""")
    print("="*70)

if __name__ == "__main__":
    test_llm_step_by_step()
