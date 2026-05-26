"""
test_tricky_articles.py
Test with TRICKY articles where models will DISAGREE
"""

import joblib
from preprocess import clean_text, load_tfidf
import requests
import time

print("="*70)
print("TESTING TRICKY ARTICLES - Where Models DISAGREE")
print("="*70)

# TRICKY articles - not obvious fake/real
tricky_articles = [
    {
        "name": "Satire (The Onion style)",
        "text": "Scientists at the Institute of Obvious Conclusions announced today that drinking coffee at 11 PM may interfere with sleep. Lead researcher Dr. No Kidding stated they were shocked by these findings. The study took 10 years and concluded that water is also wet."
    },
    {
        "name": "Opinion Piece (Vague)",
        "text": "Political analysts suggest that upcoming policy changes could impact various sectors. Some experts believe reforms are necessary, while others argue the current system works. The debate continues as stakeholders await further developments."
    },
    {
        "name": "Clickbait (But Real)",
        "text": "You Won't Believe What This Study Found About Sleep! Researchers discovered that people who sleep 7-8 hours perform better at work. The findings were published in the Journal of Sleep Research by Harvard Medical School scientists."
    },
    {
        "name": "Dry Facts (Neutral)",
        "text": "The meeting was held on Tuesday at 3 PM. Several participants attended via video conference. Various topics were discussed including budget allocation and timeline adjustments. No final decisions were announced."
    },
    {
        "name": "Conspiracy-like (But Real)",
        "text": "Declassified CIA documents reveal that the agency conducted mind control experiments in the 1950s under Project MKUltra. The program involved testing LSD on unwitting subjects. These facts were confirmed by the Church Committee in 1975."
    }
]

# Load models
print("\nLoading models...")
ml_models = {}
for name in ['decision_tree', 'gradient_boosting', 'linear_svc', 'logistic_regression', 'random_forest']:
    ml_models[name] = joblib.load(f'models/{name}.pkl')
vectorizer = load_tfidf()

from dl_predictor import DLPredictor
dl_predictor = DLPredictor()

print("Models loaded!\n")

# Test each article
all_results = []

for article in tricky_articles:
    print("="*70)
    print(f"ARTICLE: {article['name']}")
    print("="*70)
    print(f"Text: {article['text'][:80]}...")
    print()
    
    results = {'name': article['name']}
    
    # ML Test
    try:
        cleaned = clean_text(article['text'])
        X = vectorizer.transform([cleaned])
        predictions = [model.predict(X)[0] for model in ml_models.values()]
        fake_count = sum(predictions)
        ml_verdict = "FAKE" if fake_count >= 3 else "REAL"
        ml_conf = (fake_count if ml_verdict == "FAKE" else 5 - fake_count) / 5
        
        print(f"ML:     {ml_verdict:10s} ({ml_conf*100:5.1f}%) - Vote: {fake_count}/5")
        results['ml'] = ml_verdict
        results['ml_conf'] = ml_conf * 100
    except:
        print("ML:     ERROR")
        results['ml'] = "ERROR"
    
    # BiLSTM Test
    try:
        result = dl_predictor.predict(article['text'])
        if result:
            print(f"BiLSTM: {result['verdict']:10s} ({result['confidence']*100:5.1f}%)")
            results['bilstm'] = result['verdict']
            results['bilstm_conf'] = result['confidence'] * 100
        else:
            print("BiLSTM: ERROR")
            results['bilstm'] = "ERROR"
    except:
        print("BiLSTM: ERROR")
        results['bilstm'] = "ERROR"
    
    # LLaMA Test
    try:
        response = requests.post(
            "http://localhost:5000/api/predict/llm",
            json={"text": article['text']},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            print(f"LLaMA:  {data['verdict']:10s} ({data['confidence']*100:5.1f}%)")
            results['llama'] = data['verdict']
            results['llama_conf'] = data['confidence'] * 100
        else:
            print("LLaMA:  ERROR")
            results['llama'] = "ERROR"
    except:
        print("LLaMA:  ERROR")
        results['llama'] = "ERROR"
    
    # Check agreement
    verdicts = [results.get('ml'), results.get('bilstm'), results.get('llama')]
    verdicts = [v for v in verdicts if v and v != "ERROR"]
    
    if len(set(verdicts)) == 1:
        print(f"\n=> ALL AGREE: {verdicts[0]}")
    elif len(set(verdicts)) == 2:
        print(f"\n=> SPLIT DECISION: {verdicts}")
    else:
        print(f"\n=> TOTAL DISAGREEMENT: {verdicts}")
    
    all_results.append(results)
    print()
    time.sleep(1)

# Summary
print("="*70)
print("SUMMARY - DISAGREEMENT ANALYSIS")
print("="*70)

disagreements = 0
for r in all_results:
    verdicts = [r.get('ml'), r.get('bilstm'), r.get('llama')]
    verdicts = [v for v in verdicts if v and v != "ERROR"]
    
    if len(set(verdicts)) > 1:
        disagreements += 1
        print(f"\n[DISAGREE] {r['name']}")
        print(f"  ML: {r.get('ml', 'N/A')}, BiLSTM: {r.get('bilstm', 'N/A')}, LLaMA: {r.get('llama', 'N/A')}")

print(f"\n\nTotal Disagreements: {disagreements}/{len(all_results)}")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print("""
OBVIOUS articles (aliens, health scams):
  => All 3 models AGREE (easy to detect)

TRICKY articles (satire, opinion, vague):
  => Models DISAGREE (harder to classify)

This is NORMAL and EXPECTED!
Different models have different strengths.
""")
print("="*70)
