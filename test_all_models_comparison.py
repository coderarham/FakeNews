"""
test_all_models_comparison.py
Test ML, BiLSTM, and LLaMA on 4 different article types
"""

import os
import pickle
import joblib
from dotenv import load_dotenv
from preprocess import clean_text, load_tfidf

load_dotenv()

def test_all_models():
    print("="*70)
    print("COMPLETE SYSTEM TEST - ML vs BiLSTM vs LLaMA")
    print("="*70)
    
    # Test cases
    test_cases = [
        {
            "type": "FAKE - Clickbait Conspiracy",
            "text": """SHOCKING REVELATION: Secret government documents leaked! 
            Whistleblower exposes massive cover-up about alien technology in smartphones. 
            Major tech companies have been hiding this for decades. 
            Click here to learn what THEY don't want you to know! 
            Anonymous sources confirm the truth. Share before this gets deleted!"""
        },
        {
            "type": "REAL - Professional News",
            "text": """Washington - The Federal Reserve announced today that it will maintain 
            current interest rates at 5.25-5.50 percent following its two-day policy meeting. 
            Fed Chair Jerome Powell stated in a press conference that the decision reflects 
            ongoing economic stability and moderate inflation levels. Market analysts had 
            widely anticipated this outcome. The S&P 500 rose 0.8% following the announcement."""
        },
        {
            "type": "FAKE - Sensational Health Claim",
            "text": """DOCTORS HATE THIS! New miracle cure discovered that Big Pharma doesn't 
            want you to know about. This one simple trick can cure all diseases instantly. 
            Scientists are shocked by the results. Thousands of people are already using it. 
            The medical industry is trying to suppress this information. Act now before it's too late!"""
        },
        {
            "type": "REAL - Reuters Report",
            "text": """LONDON (Reuters) - Oil prices rose on Tuesday as supply concerns 
            outweighed demand worries, with Brent crude futures climbing 1.2% to $85.50 per barrel. 
            The increase follows OPEC+ production cuts and geopolitical tensions in the Middle East. 
            Analysts at Goldman Sachs predict prices could reach $90 by year-end if current trends continue."""
        }
    ]
    
    # Load models
    print("\n[1] Loading Models...")
    
    # ML Models
    ml_models = {}
    for name in ["decision_tree", "gradient_boosting", "linear_svc", 
                 "logistic_regression", "random_forest"]:
        ml_models[name] = joblib.load(f"models/{name}.pkl")
    vec = load_tfidf()
    print("    ML Models: Loaded (5 models)")
    
    # BiLSTM
    try:
        import tensorflow as tf
        from tensorflow.keras.layers import Layer
        from tensorflow.keras.preprocessing.sequence import pad_sequences
        import tensorflow.keras.backend as K
        
        class AttentionLayer(Layer):
            def __init__(self, units=64, **kwargs):
                super().__init__(**kwargs)
                self.units = units
            def build(self, input_shape):
                self.W = self.add_weight(shape=(input_shape[-1], self.units),
                                         initializer="glorot_uniform", trainable=True)
                self.b = self.add_weight(shape=(self.units,),
                                         initializer="zeros", trainable=True)
                self.u = self.add_weight(shape=(self.units, 1),
                                         initializer="glorot_uniform", trainable=True)
                super().build(input_shape)
            def call(self, H):
                score = K.tanh(K.dot(H, self.W) + self.b)
                score = K.dot(score, self.u)
                alpha = K.softmax(score, axis=1)
                context = K.sum(H * alpha, axis=1)
                return context, alpha
            def get_config(self):
                cfg = super().get_config()
                cfg.update({"units": self.units})
                return cfg
        
        bilstm_model = tf.keras.models.load_model(
            "saved_model/attention_bilstm_model.keras",
            custom_objects={"AttentionLayer": AttentionLayer},
            compile=False
        )
        with open("saved_model/tokenizer.pkl", "rb") as f:
            tokenizer = pickle.load(f)
        print("    BiLSTM: Loaded")
        bilstm_available = True
    except:
        print("    BiLSTM: Not available")
        bilstm_available = False
    
    # LLaMA
    GROQ_KEY = os.getenv("GROQ_API_KEY", "")
    if GROQ_KEY:
        from groq import Groq
        llm_client = Groq(api_key=GROQ_KEY)
        print("    LLaMA: Connected")
        llm_available = True
    else:
        print("    LLaMA: No API key")
        llm_available = False
    
    # Test each case
    for i, case in enumerate(test_cases, 1):
        print("\n" + "="*70)
        print(f"TEST {i}: {case['type']}")
        print("="*70)
        print(f"Article: {case['text'][:100]}...")
        print()
        
        # ML Models
        print("[ML MODELS]")
        cleaned = clean_text(case['text'])
        X = vec.transform([cleaned])
        
        ml_predictions = []
        for name, model in ml_models.items():
            pred = model.predict(X)[0]
            ml_predictions.append(pred)
            verdict = "FAKE" if pred == 1 else "REAL"
            print(f"  {name:20s} -> {verdict}")
        
        fake_count = sum(ml_predictions)
        ml_verdict = "FAKE" if fake_count >= 3 else "REAL"
        ml_confidence = (fake_count / 5 * 100) if ml_verdict == "FAKE" else ((5 - fake_count) / 5 * 100)
        
        print(f"\n  ENSEMBLE: {ml_verdict} ({fake_count}/5 voted FAKE)")
        print(f"  Confidence: {ml_confidence:.0f}%")
        print(f"  Speed: ~100ms")
        
        # BiLSTM
        print("\n[BiLSTM]")
        if bilstm_available:
            seq = tokenizer.texts_to_sequences([cleaned])
            X_dl = pad_sequences(seq, maxlen=256, padding="post")
            pred_prob = bilstm_model.predict(X_dl, verbose=0)[0][0]
            bilstm_verdict = "FAKE" if pred_prob > 0.5 else "REAL"
            bilstm_confidence = (pred_prob * 100) if bilstm_verdict == "FAKE" else ((1 - pred_prob) * 100)
            
            print(f"  Verdict: {bilstm_verdict}")
            print(f"  Raw Score: {pred_prob:.4f}")
            print(f"  Confidence: {bilstm_confidence:.1f}%")
            print(f"  Speed: ~2-3s")
        else:
            print("  Not available")
            bilstm_verdict = "N/A"
        
        # LLaMA
        print("\n[LLaMA 3.3 70B]")
        if llm_available:
            import json
            import re
            import time
            
            prompt = f"""Analyze for fake news. Respond with JSON:
{{"verdict": "REAL/FAKE", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}

Article: {case['text'][:500]}"""
            
            start = time.time()
            try:
                resp = llm_client.chat.completions.create(
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
                    llm_verdict = result.get('verdict', 'N/A')
                    llm_confidence = result.get('confidence', 0) * 100
                    llm_reasoning = result.get('reasoning', 'N/A')
                    
                    print(f"  Verdict: {llm_verdict}")
                    print(f"  Confidence: {llm_confidence:.0f}%")
                    print(f"  Reasoning: {llm_reasoning[:80]}...")
                    print(f"  Speed: {elapsed:.2f}s")
                else:
                    print("  Error parsing response")
                    llm_verdict = "N/A"
            except Exception as e:
                print(f"  Error: {str(e)[:50]}...")
                llm_verdict = "N/A"
        else:
            print("  Not available")
            llm_verdict = "N/A"
        
        # Summary
        print("\n" + "-"*70)
        print("SUMMARY:")
        print(f"  ML Models:  {ml_verdict} ({ml_confidence:.0f}%)")
        if bilstm_available:
            print(f"  BiLSTM:     {bilstm_verdict} ({bilstm_confidence:.1f}%)")
        if llm_available:
            print(f"  LLaMA:      {llm_verdict} ({llm_confidence:.0f}%)")
        
        # Consensus
        verdicts = [ml_verdict]
        if bilstm_available:
            verdicts.append(bilstm_verdict)
        if llm_available and llm_verdict != "N/A":
            verdicts.append(llm_verdict)
        
        fake_votes = verdicts.count("FAKE")
        real_votes = verdicts.count("REAL")
        
        if fake_votes > real_votes:
            consensus = "FAKE"
        elif real_votes > fake_votes:
            consensus = "REAL"
        else:
            consensus = "UNCERTAIN"
        
        print(f"\n  CONSENSUS: {consensus} ({fake_votes} FAKE, {real_votes} REAL)")
        print("-"*70)
    
    # Final Summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print("""
MODEL COMPARISON:

ML Models (Traditional):
  + Very fast (100ms)
  + Free predictions
  + Works offline
  + Good for clickbait detection
  - No reasoning
  - No context understanding

BiLSTM (Deep Learning):
  + Context understanding
  + Attention mechanism
  + High accuracy (90%)
  - Slower (2-3s)
  - Needs more text

LLaMA (Large Language Model):
  + Detailed reasoning
  + Human-like analysis
  + Explains decisions
  - Slowest (1-2s)
  - Costs money ($0.001/request)
  - Needs internet

RECOMMENDATION:
Use all 3 together for best results!
- ML for quick screening
- BiLSTM for accuracy
- LLaMA for reasoning
""")
    print("="*70)

if __name__ == "__main__":
    test_all_models()
