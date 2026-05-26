"""
test_ml_vs_bilstm.py
Compare ML and BiLSTM on clickbait fake news
"""

import joblib
from preprocess import clean_text, load_tfidf

# Your clickbait example
clickbait_fake = """
BREAKING: Secret government documents reveal shocking truth about alien 
technology being used in smartphones! Whistleblower claims major tech 
companies have been hiding this for decades. Click here to learn what 
THEY don't want you to know!
"""

print("="*70)
print("ML Models vs BiLSTM - Clickbait Detection Test")
print("="*70)
print("\nTest Article:")
print(clickbait_fake)
print("\n" + "="*70)

# Test ML Models
print("\n[1] ML MODELS (TF-IDF + Classifiers)")
print("="*70)

try:
    vec = load_tfidf()
    cleaned = clean_text(clickbait_fake)
    X = vec.transform([cleaned])
    
    model_names = ['decision_tree', 'gradient_boosting', 'linear_svc', 
                   'logistic_regression', 'random_forest']
    
    predictions = []
    for name in model_names:
        model = joblib.load(f'models/{name}.pkl')
        pred = model.predict(X)[0]
        verdict = "FAKE" if pred == 1 else "REAL"
        predictions.append(pred)
        print(f"  {name:20s} -> {verdict}")
    
    fake_count = sum(predictions)
    ensemble = "FAKE" if fake_count >= 3 else "REAL"
    
    print(f"\n  ENSEMBLE VERDICT: {ensemble} ({fake_count}/5 voted FAKE)")
    
except Exception as e:
    print(f"[ERROR] {e}")

# Test BiLSTM
print("\n" + "="*70)
print("[2] BiLSTM (Deep Learning)")
print("="*70)

try:
    from dl_predictor import DLPredictor
    predictor = DLPredictor()
    
    if predictor.model:
        result = predictor.predict(clickbait_fake)
        print(f"  VERDICT: {result['verdict']}")
        print(f"  Confidence: {result['confidence']*100:.2f}%")
    else:
        print("  [ERROR] Model not loaded")
        
except Exception as e:
    print(f"[ERROR] {e}")

# Analysis
print("\n" + "="*70)
print("ANALYSIS")
print("="*70)
print("""
WHY ML WORKS BETTER FOR CLICKBAIT:

ML Models (TF-IDF):
- Detect keywords: "BREAKING", "shocking", "secret", "reveal"
- High TF-IDF scores for sensational words
- Pattern matching on word frequency
- Works well on short text

BiLSTM:
- Needs context and sentence structure
- Trained on 2015-2017 political articles
- Modern clickbait style not in training data
- Short text = insufficient context

RECOMMENDATION:
For clickbait/conspiracy detection -> Use ML Models
For nuanced fake news detection -> Use BiLSTM
For best results -> Use BOTH + LLM Ensemble
""")
print("="*70)
