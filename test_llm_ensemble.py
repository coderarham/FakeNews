"""
test_llm_ensemble.py
Test LLM Ensemble (LLaMA, GPT-4o, Gemini) for fake news detection
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_llm_ensemble():
    print("="*70)
    print("LLM Ensemble Testing")
    print("="*70)
    
    # Check API keys
    print("\n[1] Checking API Keys...")
    
    GROQ_KEY = os.getenv("GROQ_API_KEY", "")
    GEMINI_KEY = os.getenv("GOOGLE_GENAI_KEY", "")
    
    if GROQ_KEY:
        print(f"    Groq API: {GROQ_KEY[:20]}... [OK]")
    else:
        print("    Groq API: [MISSING]")
    
    if GEMINI_KEY:
        print(f"    Gemini API: {GEMINI_KEY[:20]}... [OK]")
    else:
        print("    Gemini API: [MISSING]")
    
    if not GROQ_KEY and not GEMINI_KEY:
        print("\n[ERROR] No API keys found!")
        print("Set keys in .env file")
        return
    
    # Test cases
    test_cases = [
        {
            "label": "FAKE - Clickbait",
            "text": "SHOCKING: Secret government documents reveal alien technology in smartphones! Whistleblower claims major tech companies have been hiding this for decades. Click here to learn what THEY don't want you to know!"
        },
        {
            "label": "REAL - News",
            "text": "Washington - The Federal Reserve announced today that it will maintain current interest rates following its monthly policy meeting. Fed Chair Jerome Powell stated that the decision reflects ongoing economic stability and moderate inflation levels. Market analysts had widely anticipated this outcome."
        },
        {
            "label": "FAKE - Conspiracy",
            "text": "Anonymous sources confirm that secret documents prove massive government cover-up. Insiders reveal shocking truth about what really happened. Mainstream media refuses to report this!"
        },
        {
            "label": "REAL - Report",
            "text": "According to Reuters, the stock market showed gains in morning trading today. The S&P 500 index rose 0.8 percent while the Dow Jones Industrial Average increased by 150 points. Technology stocks led the rally."
        }
    ]
    
    print("\n[2] Testing LLM Ensemble...")
    print("="*70)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n[Test {i}] {case['label']}")
        print(f"Text: {case['text'][:80]}...")
        print("\nQuerying LLMs (this may take 10-30 seconds)...")
        
        result = llm_ensemble_predict(case['text'])
        
        print(f"\n--- RESULTS ---")
        print(f"Final Verdict: {result['verdict']}")
        print(f"Confidence: {result['confidence']*100:.1f}%")
        
        print(f"\nIndividual LLM Results:")
        for model_name, res in result['individual_results'].items():
            if 'error' in res:
                print(f"  {model_name.upper()}: ERROR - {res['error'][:50]}...")
            else:
                print(f"  {model_name.upper()}: {res.get('verdict', 'N/A')} ({res.get('confidence', 0)*100:.0f}%)")
                if 'reasoning' in res:
                    print(f"    Reasoning: {res['reasoning'][:100]}...")
        
        print("-"*70)
    
    print("\n" + "="*70)
    print("LLM Ensemble Testing Complete!")
    print("="*70)


def llm_ensemble_predict(text: str) -> dict:
    """Call LLaMA 3.3 70B, GPT-4o, Gemini 2.5 Flash via APIs."""
    import json
    import re
    
    GROQ_KEY = os.getenv("GROQ_API_KEY", "")
    GEMINI_KEY = os.getenv("GOOGLE_GENAI_KEY", "")
    
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
{text[:2000]}

Respond ONLY with valid JSON."""

    results = {}
    
    # LLaMA 3.3 70B via Groq
    if GROQ_KEY:
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_KEY)
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            txt = resp.choices[0].message.content
            match = re.search(r'\{.*\}', txt, re.DOTALL)
            if match:
                results["llama"] = json.loads(match.group())
        except Exception as e:
            results["llama"] = {"error": str(e)}
    
    # Gemini Flash
    if GEMINI_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")  # Changed from gemini-2.0-flash-exp
            resp = model.generate_content(prompt)
            txt = resp.text
            match = re.search(r'\{.*\}', txt, re.DOTALL)
            if match:
                results["gemini"] = json.loads(match.group())
        except Exception as e:
            results["gemini"] = {"error": str(e)}
    
    # Majority vote
    verdicts = [r.get("verdict", "UNCERTAIN") for r in results.values() if "error" not in r]
    if verdicts:
        from collections import Counter
        final_verdict = Counter(verdicts).most_common(1)[0][0]
        avg_conf = sum([r.get("confidence", 0.5) for r in results.values() if "error" not in r]) / len([r for r in results.values() if "error" not in r])
    else:
        final_verdict = "UNCERTAIN"
        avg_conf = 0.0
    
    return {
        "verdict": final_verdict,
        "confidence": round(avg_conf, 3),
        "individual_results": results
    }


if __name__ == "__main__":
    test_llm_ensemble()
