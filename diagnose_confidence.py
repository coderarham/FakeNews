"""
diagnose_confidence.py
Check WHY ML and BiLSTM always show 100%
"""

import joblib
import numpy as np
from preprocess import clean_text, load_tfidf
from dl_predictor import DLPredictor

print("="*70)
print("DIAGNOSING CONFIDENCE SCORES")
print("="*70)

test_articles = [
    "BREAKING: NASA confirms aliens!",
    "WASHINGTON (Reuters) - The Federal Reserve announced rates.",
    "You Won't Believe This Study! Harvard researchers found...",
    "The meeting was held on Tuesday. Topics were discussed."
]

# Load models
ml_models = {}
for name in ['decision_tree', 'gradient_boosting', 'linear_svc', 'logistic_regression', 'random_forest']:
    ml_models[name] = joblib.load(f'models/{name}.pkl')
vectorizer = load_tfidf()

dl_predictor = DLPredictor()

print("\n" + "="*70)
print("ML MODELS - RAW PROBABILITIES")
print("="*70)

for i, text in enumerate(test_articles, 1):
    print(f"\n[TEST {i}] {text[:50]}...")
    
    cleaned = clean_text(text)
    X = vectorizer.transform([cleaned])
    
    print("\nModel Predictions:")
    for name, model in ml_models.items():
        pred = model.predict(X)[0]
        
        # Check if model has predict_proba
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(X)[0]
            print(f"  {name:20s}: {pred} | Proba: [REAL={proba[0]:.4f}, FAKE={proba[1]:.4f}]")
        else:
            print(f"  {name:20s}: {pred} | No probability (SVM)")
    
    # Majority vote
    predictions = [model.predict(X)[0] for model in ml_models.values()]
    fake_count = sum(predictions)
    print(f"\n  Majority Vote: {fake_count}/5 say FAKE")
    
    # This is the problem - we're converting vote to 100%!
    confidence = fake_count / 5 if fake_count >= 3 else (5 - fake_count) / 5
    print(f"  Our Confidence Calculation: {confidence*100:.1f}%")
    print(f"  ^ THIS IS WRONG! We're just counting votes, not averaging probabilities!")

print("\n" + "="*70)
print("BiLSTM - RAW PROBABILITIES")
print("="*70)

for i, text in enumerate(test_articles, 1):
    print(f"\n[TEST {i}] {text[:50]}...")
    
    result = dl_predictor.predict(text)
    if result:
        print(f"  Raw Probability: {result['fake_probability']:.6f}")
        print(f"  Verdict: {result['verdict']}")
        print(f"  Our Confidence: {result['confidence']*100:.1f}%")
        
        # Check if it's exactly 0 or 1
        if result['fake_probability'] in [0.0, 1.0]:
            print(f"  ^ PROBLEM: Sigmoid output is EXACTLY {result['fake_probability']} (too extreme!)")
        elif result['fake_probability'] < 0.01 or result['fake_probability'] > 0.99:
            print(f"  ^ PROBLEM: Sigmoid output is VERY extreme (>99% or <1%)")

print("\n" + "="*70)
print("ROOT CAUSE ANALYSIS")
print("="*70)
print("""
PROBLEM 1: ML Confidence Calculation
-------------------------------------
Current code:
  fake_count = 5  # All 5 models say FAKE
  confidence = 5/5 = 100%

This is WRONG! We're just counting votes, not probabilities.

FIX: Average the actual probabilities from predict_proba()
  confidence = average([0.92, 0.88, 0.95, 0.91, 0.89]) = 91%


PROBLEM 2: BiLSTM Extreme Outputs
----------------------------------
BiLSTM sigmoid outputs are TOO extreme:
  - Either 0.0000001 (basically 0)
  - Or 0.9999999 (basically 1)

This happens because:
1. Model is VERY confident (trained well)
2. Sigmoid squashes to extremes
3. No calibration applied

FIX OPTIONS:
1. Temperature scaling (soften probabilities)
2. Platt scaling (calibrate outputs)
3. Accept it (model IS very confident on obvious cases)


RECOMMENDATION:
--------------
For ML: Use average of predict_proba() instead of vote count
For BiLSTM: This is actually NORMAL for well-trained models
For LLaMA: Already working correctly (varies 60-95%)
""")
print("="*70)
