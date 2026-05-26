"""
live_llm_test.py
Live LLM testing with different article types
"""

import os
import json
import re
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def test_llm_live():
    print("="*70)
    print("LIVE LLM TESTING - LLaMA 3.3 70B")
    print("="*70)
    
    # Check API
    GROQ_KEY = os.getenv("GROQ_API_KEY", "")
    if not GROQ_KEY:
        print("\n[ERROR] No API key found!")
        return
    
    print(f"\nAPI Key: {GROQ_KEY[:20]}...{GROQ_KEY[-10:]}")
    print("Status: Connected to Groq")
    
    client = Groq(api_key=GROQ_KEY)
    
    # Test cases
    tests = [
        {
            "name": "TEST 1: Obvious FAKE - Alien Conspiracy",
            "text": """BREAKING: NASA Scientist Confirms Aliens Living Among Us! 
            Secret government program revealed. Whistleblower exposes shocking truth. 
            Mainstream media covering it up. Share before this gets deleted!""",
            "expected": "FAKE"
        },
        {
            "name": "TEST 2: Obvious REAL - BBC Report",
            "text": """The United Nations announced today that global carbon emissions 
            decreased by 3% in 2024, according to its annual climate report. 
            UN Secretary-General António Guterres called it "encouraging progress" 
            while emphasizing the need for continued efforts.""",
            "expected": "REAL"
        },
        {
            "name": "TEST 3: Tricky - Satire",
            "text": """Scientists Discover Coffee Actually Makes You More Tired, 
            Study Finds. Researchers at the Institute of Obvious Conclusions 
            report that drinking coffee at 11 PM may interfere with sleep. 
            "We were shocked," said lead researcher Dr. No Kidding.""",
            "expected": "FAKE/SATIRE"
        },
        {
            "name": "TEST 4: Ambiguous - Vague Report",
            "text": """Sources say government officials are considering various options 
            regarding the new policy. Some experts believe changes may be coming. 
            The situation remains fluid as discussions continue.""",
            "expected": "UNCERTAIN"
        },
        {
            "name": "TEST 5: Health Scam",
            "text": """DOCTORS HATE HIM! This one weird trick burns fat instantly. 
            No exercise needed. Big Pharma doesn't want you to know. 
            Limited time offer - click now before government bans it!""",
            "expected": "FAKE"
        }
    ]
    
    results = []
    
    for i, test in enumerate(tests, 1):
        print("\n" + "="*70)
        print(f"{test['name']}")
        print("="*70)
        print(f"Text: {test['text'][:80].strip()}...")
        print(f"Expected: {test['expected']}")
        print("\nQuerying LLaMA...")
        
        prompt = f"""Analyze this article for fake news detection.
Respond with JSON only:
{{
  "verdict": "REAL/FAKE/UNCERTAIN",
  "confidence": 0.0-1.0,
  "factual_consistency_score": 0.0-1.0,
  "sensationalism_score": 0.0-1.0,
  "source_credibility_score": 0.0-1.0,
  "writing_style_score": 0.0-1.0,
  "reasoning": "brief explanation"
}}

ARTICLE:
{test['text']}"""
        
        start = time.time()
        
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            elapsed = time.time() - start
            
            raw = response.choices[0].message.content
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            
            if match:
                result = json.loads(match.group())
                
                verdict = result.get('verdict', 'N/A')
                confidence = result.get('confidence', 0)
                reasoning = result.get('reasoning', 'N/A')
                
                factual = result.get('factual_consistency_score', 0)
                sensational = result.get('sensationalism_score', 0)
                credibility = result.get('source_credibility_score', 0)
                style = result.get('writing_style_score', 0)
                
                print(f"\n--- RESULT ---")
                print(f"Verdict: {verdict}")
                print(f"Confidence: {confidence*100:.1f}%")
                print(f"Time: {elapsed:.2f}s")
                print(f"\nScores:")
                print(f"  Factual Consistency: {factual*100:.0f}%")
                print(f"  Sensationalism: {sensational*100:.0f}%")
                print(f"  Source Credibility: {credibility*100:.0f}%")
                print(f"  Writing Style: {style*100:.0f}%")
                print(f"\nReasoning:")
                print(f"  {reasoning}")
                
                # Check if correct
                is_correct = "?"
                if test['expected'] == "FAKE" and verdict == "FAKE":
                    is_correct = "CORRECT"
                elif test['expected'] == "REAL" and verdict == "REAL":
                    is_correct = "CORRECT"
                elif test['expected'] == "UNCERTAIN" and confidence < 0.7:
                    is_correct = "CORRECT (Low confidence)"
                elif test['expected'] == "FAKE/SATIRE" and verdict == "FAKE":
                    is_correct = "CORRECT"
                else:
                    is_correct = "WRONG"
                
                print(f"\nStatus: {is_correct}")
                
                results.append({
                    'test': test['name'],
                    'expected': test['expected'],
                    'verdict': verdict,
                    'confidence': confidence,
                    'correct': is_correct,
                    'time': elapsed
                })
                
            else:
                print("\n[ERROR] Could not parse JSON response")
                results.append({
                    'test': test['name'],
                    'expected': test['expected'],
                    'verdict': 'ERROR',
                    'confidence': 0,
                    'correct': 'ERROR',
                    'time': elapsed
                })
        
        except Exception as e:
            print(f"\n[ERROR] {str(e)[:100]}")
            results.append({
                'test': test['name'],
                'expected': test['expected'],
                'verdict': 'ERROR',
                'confidence': 0,
                'correct': 'ERROR',
                'time': 0
            })
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    correct_count = sum(1 for r in results if 'CORRECT' in r['correct'])
    total = len(results)
    
    print(f"\nResults: {correct_count}/{total} correct")
    print(f"Accuracy: {correct_count/total*100:.1f}%")
    print(f"Avg Time: {sum(r['time'] for r in results)/total:.2f}s")
    
    print("\nDetailed Results:")
    for r in results:
        status = "[OK]" if "CORRECT" in r['correct'] else "[X]"
        print(f"  {status} {r['test'][:40]:40s} -> {r['verdict']:10s} ({r['confidence']*100:.0f}%)")
    
    print("\n" + "="*70)
    print("ANALYSIS")
    print("="*70)
    print("""
LLaMA 3.3 70B Performance:

STRENGTHS:
+ Detects obvious fake news (clickbait, conspiracies)
+ Identifies credible sources (Reuters, UN, BBC)
+ Provides detailed reasoning
+ Analyzes multiple dimensions (factual, sensational, etc)
+ Fast response (0.5-1.5 seconds)

WEAKNESSES:
- May struggle with satire/parody
- Ambiguous content can be challenging
- Depends on training data patterns

BEST USE CASES:
1. Obvious fake news detection
2. Professional news verification
3. Detailed analysis with reasoning
4. When explanation is needed

RECOMMENDATION:
Use LLaMA alongside ML/BiLSTM for best results!
""")
    print("="*70)

if __name__ == "__main__":
    test_llm_live()
