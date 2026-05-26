"""
quick_test_samples.py
Quick test of 4 sample articles on all models
Usage: python quick_test_samples.py
"""

import os
import pickle
import joblib
from dotenv import load_dotenv
from preprocess import clean_text, load_tfidf

load_dotenv()

# Test articles
articles = [
    {
        "name": "TEST 1: Obvious FAKE - Conspiracy",
        "text": """SHOCKING: Government Hiding Alien Technology in 5G Towers! 
        Whistleblower reveals secret documents proving massive cover-up. 
        Major telecom companies have been working with extraterrestrials for decades. 
        Anonymous sources confirm the truth that mainstream media refuses to report. 
        Click here before this gets deleted! Share immediately! 
        THEY don't want you to know this information!""",
        "expected": "FAKE"
    },
    {
        "name": "TEST 2: Obvious REAL - Reuters",
        "text": """LONDON (Reuters) - The Bank of England raised interest rates by 0.25 percentage 
        points to 5.25% on Thursday, marking the 14th consecutive increase as it continues 
        efforts to combat inflation. Governor Andrew Bailey stated that the decision was 
        necessary despite signs of economic slowdown. The FTSE 100 index fell 0.6% following 
        the announcement. Economists at Barclays predict one more rate hike before year-end.""",
        "expected": "REAL"
    },
    {
        "name": "TEST 3: Tricky - Satire",
        "text": """Breaking: Local Man Discovers Internet Still Works Without Checking Social Media 
        Every 5 Minutes. In a groundbreaking experiment, 32-year-old Dave Thompson went 
        an entire hour without scrolling through his phone. "I didn't know what to do 
        with my hands," Thompson reported. Scientists are baffled by this unprecedented 
        achievement. His friends have started a support group.""",
        "expected": "FAKE/SATIRE"
    },
    {
        "name": "TEST 4: Ambiguous - Opinion",
        "text": """The government's new economic policy has sparked debate among experts. 
        While some analysts praise the approach, others express concerns about 
        long-term implications. Officials say they are monitoring the situation closely. 
        Sources indicate that discussions are ongoing. The outcome remains uncertain 
        as stakeholders continue to evaluate various options. Time will tell whether 
        this strategy proves effective.""",
        "expected": "UNCERTAIN"
    }
]

def test_samples():
    print("="*70)
    print("QUICK TEST - 4 Sample Articles")
    print("="*70)
    
    # Load models
    print("\nLoading models...")
    
    # ML
    ml_models = {}
    for name in ["decision_tree", "gradient_boosting", "linear_svc", 
                 "logistic_regression", "random_forest"]:
        ml_models[name] = joblib.load(f"models/{name}.pkl")
    vec = load_tfidf()
    
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
        
        bilstm = tf.keras.models.load_model(
            "saved_model/attention_bilstm_model.keras",
            custom_objects={"AttentionLayer": AttentionLayer},
            compile=False
        )
        with open("saved_model/tokenizer.pkl", "rb") as f:
            tokenizer = pickle.load(f)
        bilstm_ok = True
    except:
        bilstm_ok = False
    
    # LLaMA
    GROQ_KEY = os.getenv("GROQ_API_KEY", "")
    if GROQ_KEY:
        from groq import Groq
        llm = Groq(api_key=GROQ_KEY)
        llm_ok = True
    else:
        llm_ok = False
    
    print(f"ML: OK | BiLSTM: {'OK' if bilstm_ok else 'NO'} | LLaMA: {'OK' if llm_ok else 'NO'}")
    
    # Test each article
    for i, article in enumerate(articles, 1):
        print("\n" + "="*70)
        print(f"{article['name']}")
        print("="*70)
        print(f"Text: {article['text'][:80].strip()}...")
        print(f"Expected: {article['expected']}")
        print()
        
        cleaned = clean_text(article['text'])
        
        # ML
        X = vec.transform([cleaned])
        preds = [m.predict(X)[0] for m in ml_models.values()]
        fake_count = sum(preds)
        ml_verdict = "FAKE" if fake_count >= 3 else "REAL"
        print(f"ML:     {ml_verdict} ({fake_count}/5 voted FAKE)")
        
        # BiLSTM
        if bilstm_ok:
            seq = tokenizer.texts_to_sequences([cleaned])
            X_dl = pad_sequences(seq, maxlen=256, padding="post")
            pred = bilstm.predict(X_dl, verbose=0)[0][0]
            bilstm_verdict = "FAKE" if pred > 0.5 else "REAL"
            print(f"BiLSTM: {bilstm_verdict} (score: {pred:.4f})")
        
        # LLaMA
        if llm_ok:
            import json, re, time
            prompt = f"""Analyze: {article['text'][:300]}
Respond JSON: {{"verdict": "REAL/FAKE", "confidence": 0.0-1.0}}"""
            
            try:
                resp = llm.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=100
                )
                raw = resp.choices[0].message.content
                match = re.search(r'\{.*\}', raw, re.DOTALL)
                if match:
                    result = json.loads(match.group())
                    llm_verdict = result.get('verdict', 'N/A')
                    llm_conf = result.get('confidence', 0)
                    print(f"LLaMA:  {llm_verdict} ({llm_conf*100:.0f}%)")
            except:
                print("LLaMA:  Error")
        
        print("-"*70)
    
    print("\n" + "="*70)
    print("TEST COMPLETE!")
    print("="*70)
    print("""
HOW TO USE THESE TESTS:

1. Copy any article from test_articles.txt
2. Test with quick_test.py:
   python quick_test.py "Your article text"

3. Or test all models:
   python test_all_models_comparison.py

4. Or use Streamlit UI:
   streamlit run app.py

EXPECTED RESULTS:
- Test 1 (Conspiracy): All should say FAKE
- Test 2 (Reuters): All should say REAL
- Test 3 (Satire): Mixed results (tricky!)
- Test 4 (Opinion): Low confidence (ambiguous)
""")

if __name__ == "__main__":
    test_samples()
