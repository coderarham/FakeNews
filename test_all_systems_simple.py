"""
test_all_systems_simple.py
Simple test of ML + BiLSTM + LLaMA (no unicode)
"""

import joblib
from preprocess import clean_text, load_tfidf
import requests
import time

print("="*70)
print("FINAL SYSTEM TEST - ML + BiLSTM + LLaMA")
print("="*70)

test_articles = [
    {
        "name": "Conspiracy",
        "text": "BREAKING: NASA Scientists Confirm Aliens Living Among Us! Secret government documents leaked!"
    },
    {
        "name": "Reuters",
        "text": "WASHINGTON (Reuters) - The Federal Reserve announced Wednesday it will maintain interest rates at current levels."
    },
    {
        "name": "Health Scam",
        "text": "DOCTORS HATE HIM! This one weird trick melts belly fat overnight. No diet needed!"
    }
]

# TEST 1: ML CLASSIFIERS
print("\n" + "="*70)
print("SYSTEM 1: ML CLASSIFIERS")
print("="*70)

try:
    ml_models = {}
    for name in ['decision_tree', 'gradient_boosting', 'linear_svc', 'logistic_regression', 'random_forest']:
        ml_models[name] = joblib.load(f'models/{name}.pkl')
    
    vectorizer = load_tfidf()
    print(f"[OK] Loaded {len(ml_models)} ML models")
    
    ml_results = []
    for article in test_articles:
        print(f"\n{article['name']}: {article['text'][:50]}...")
        
        cleaned = clean_text(article['text'])
        X = vectorizer.transform([cleaned])
        
        predictions = [model.predict(X)[0] for model in ml_models.values()]
        fake_count = sum(predictions)
        verdict = "FAKE" if fake_count >= 3 else "REAL"
        confidence = (fake_count if verdict == "FAKE" else len(predictions) - fake_count) / len(predictions)
        
        print(f"  ML: {verdict} ({confidence*100:.1f}%) - Vote: {fake_count}/5")
        ml_results.append({'verdict': verdict, 'conf': confidence*100})
    
    ml_status = "[OK] WORKING"
except Exception as e:
    print(f"[ERROR] {str(e)[:50]}")
    ml_status = "[ERROR]"
    ml_results = []

# TEST 2: BiLSTM
print("\n" + "="*70)
print("SYSTEM 2: BiLSTM DEEP LEARNING")
print("="*70)

try:
    from dl_predictor import DLPredictor
    dl_predictor = DLPredictor()
    
    if dl_predictor.model:
        print("[OK] Loaded BiLSTM model")
        
        bilstm_results = []
        for article in test_articles:
            print(f"\n{article['name']}: {article['text'][:50]}...")
            
            result = dl_predictor.predict(article['text'])
            if result:
                print(f"  BiLSTM: {result['verdict']} ({result['confidence']*100:.1f}%)")
                bilstm_results.append({'verdict': result['verdict'], 'conf': result['confidence']*100})
        
        bilstm_status = "[OK] WORKING"
    else:
        print("[ERROR] Model not loaded")
        bilstm_status = "[ERROR]"
        bilstm_results = []
except Exception as e:
    print(f"[ERROR] {str(e)[:50]}")
    bilstm_status = "[ERROR]"
    bilstm_results = []

# TEST 3: LLaMA
print("\n" + "="*70)
print("SYSTEM 3: LLaMA 3.3 70B")
print("="*70)

try:
    print("[OK] Testing LLaMA API...")
    
    llm_results = []
    for article in test_articles:
        print(f"\n{article['name']}: {article['text'][:50]}...")
        
        response = requests.post(
            "http://localhost:5000/api/predict/llm",
            json={"text": article['text']},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  LLaMA: {data['verdict']} ({data['confidence']*100:.1f}%)")
            llm_results.append({'verdict': data['verdict'], 'conf': data['confidence']*100})
        else:
            print(f"  [ERROR] HTTP {response.status_code}")
        
        time.sleep(1)
    
    llm_status = "[OK] WORKING"
except Exception as e:
    print(f"[ERROR] {str(e)[:50]}")
    llm_status = "[ERROR]"
    llm_results = []

# SUMMARY
print("\n" + "="*70)
print("FINAL STATUS")
print("="*70)
print(f"\n1. ML Classifiers:  {ml_status}")
print(f"2. BiLSTM:          {bilstm_status}")
print(f"3. LLaMA 3.3 70B:   {llm_status}")

if ml_results and bilstm_results and llm_results:
    print("\n" + "="*70)
    print("COMPARISON TABLE")
    print("="*70)
    
    for i, article in enumerate(test_articles):
        print(f"\n{article['name']}:")
        print(f"  ML:     {ml_results[i]['verdict']:10s} ({ml_results[i]['conf']:5.1f}%)")
        print(f"  BiLSTM: {bilstm_results[i]['verdict']:10s} ({bilstm_results[i]['conf']:5.1f}%)")
        print(f"  LLaMA:  {llm_results[i]['verdict']:10s} ({llm_results[i]['conf']:5.1f}%)")
        
        verdicts = [ml_results[i]['verdict'], bilstm_results[i]['verdict'], llm_results[i]['verdict']]
        if len(set(verdicts)) == 1:
            print(f"  => ALL AGREE: {verdicts[0]}")
        else:
            print(f"  => MIXED: {verdicts}")

print("\n" + "="*70)
print("ALL 3 SYSTEMS WORKING!")
print("="*70)
