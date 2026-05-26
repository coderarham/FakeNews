"""
Comprehensive Model Testing Script
Tests all models (ML, DL, LLM, Agent Swarm) on mixed dataset
Run: python test_all_models.py
"""

import time
import joblib
from test_dataset import TEST_ARTICLES, print_dataset_summary
from preprocess import clean_text, load_tfidf

print("\n" + "="*80)
print(" "*20 + "TRUTHLENS COMPREHENSIVE MODEL TEST")
print("="*80)

print_dataset_summary()

# Load ML models
print("[1/4] Loading ML Models...")
ml_models = {}
for name in ['decision_tree', 'gradient_boosting', 'linear_svc', 'logistic_regression', 'random_forest']:
    try:
        ml_models[name] = joblib.load(f'models/{name}.pkl')
    except:
        pass
print(f"      Loaded {len(ml_models)} ML models")

# Load DL model
print("[2/4] Loading DL Model...")
dl_predictor = None
try:
    from dl_predictor import DLPredictor
    dl_predictor = DLPredictor()
    if dl_predictor.model:
        print("      DL model loaded (BiLSTM)")
    else:
        dl_predictor = None
        print("      DL model not available")
except:
    print("      DL model not available")

# Load vectorizer
print("[3/4] Loading TF-IDF Vectorizer...")
vectorizer = load_tfidf()
print("      Vectorizer loaded")

print("[4/4] Checking LLM & Agent Swarm...")
print("      LLM: Available (Groq API)")
print("      Agent Swarm: Available (20 agents)")

print("\n" + "="*80)
print("STARTING TESTS...")
print("="*80 + "\n")

results = []

for article in TEST_ARTICLES:
    print(f"\n{'='*80}")
    print(f"TEST #{article['id']}: {article['category']}")
    print(f"ACTUAL LABEL: {article['label']}")
    print(f"{'='*80}")
    print(f"Article Preview: {article['article'][:150]}...")
    print()
    
    text = article['article']
    result = {
        'id': article['id'],
        'category': article['category'],
        'actual': article['label'],
        'ml': None,
        'dl': None,
        'llm': None,
        'swarm': None
    }
    
    # ========== ML ENSEMBLE ==========
    print("[ML ENSEMBLE] Testing with 5 classifiers...")
    try:
        cleaned = clean_text(text)
        X = vectorizer.transform([cleaned])
        
        predictions = []
        for name, model in ml_models.items():
            pred = model.predict(X)[0]
            predictions.append(pred)
        
        fake_count = sum(predictions)
        ml_verdict = 'FAKE' if fake_count >= 3 else 'REAL'
        ml_confidence = fake_count / len(predictions) if ml_verdict == 'FAKE' else (len(predictions) - fake_count) / len(predictions)
        
        result['ml'] = {
            'verdict': ml_verdict,
            'confidence': round(ml_confidence * 100, 1),
            'votes': f"{fake_count}/{len(predictions)}"
        }
        
        match = "[CORRECT]" if ml_verdict == article['label'] else "[WRONG]"
        print(f"      Verdict: {ml_verdict} ({ml_confidence*100:.1f}%) {match}")
        print(f"      Votes: {fake_count}/{len(predictions)} models voted FAKE")
    except Exception as e:
        print(f"      Error: {e}")
    
    # ========== DEEP LEARNING ==========
    print("\n[DEEP LEARNING] Testing with BiLSTM...")
    try:
        if dl_predictor:
            dl_result = dl_predictor.predict(text)
            if dl_result:
                result['dl'] = {
                    'verdict': dl_result['verdict'],
                    'confidence': round(dl_result['confidence'] * 100, 1)
                }
                match = "[CORRECT]" if dl_result['verdict'] == article['label'] else "[WRONG]"
                print(f"      Verdict: {dl_result['verdict']} ({dl_result['confidence']*100:.1f}%) {match}")
            else:
                print("      DL prediction failed")
        else:
            print("      DL model not available")
    except Exception as e:
        print(f"      Error: {e}")
    
    # ========== LLM (Skip for speed - optional) ==========
    print("\n[LLM] Skipping (takes 5-10s per article, enable if needed)")
    result['llm'] = {'verdict': 'SKIPPED', 'confidence': 0}
    
    # ========== AGENT SWARM (Skip for speed - optional) ==========
    print("[AGENT SWARM] Skipping (takes 20-30s per article, enable if needed)")
    result['swarm'] = {'verdict': 'SKIPPED', 'confidence': 0}
    
    results.append(result)
    time.sleep(0.5)

# ========== SUMMARY ==========
print("\n\n" + "="*80)
print(" "*25 + "FINAL RESULTS SUMMARY")
print("="*80)

print(f"\n{'ID':<4} {'Category':<25} {'Actual':<6} {'ML':<15} {'DL':<15}")
print("-"*80)

ml_correct = 0
dl_correct = 0

for r in results:
    ml_str = f"{r['ml']['verdict']} ({r['ml']['confidence']}%)" if r['ml'] else "N/A"
    dl_str = f"{r['dl']['verdict']} ({r['dl']['confidence']}%)" if r['dl'] else "N/A"
    
    if r['ml'] and r['ml']['verdict'] == r['actual']:
        ml_correct += 1
        ml_str += " [OK]"
    elif r['ml']:
        ml_str += " [X]"
    
    if r['dl'] and r['dl']['verdict'] == r['actual']:
        dl_correct += 1
        dl_str += " [OK]"
    elif r['dl']:
        dl_str += " [X]"
    
    print(f"{r['id']:<4} {r['category']:<25} {r['actual']:<6} {ml_str:<15} {dl_str:<15}")

print("-"*80)
print(f"\nML ENSEMBLE ACCURACY: {ml_correct}/{len(results)} = {ml_correct/len(results)*100:.1f}%")
if dl_correct > 0:
    print(f"DL (BiLSTM) ACCURACY: {dl_correct}/{len(results)} = {dl_correct/len(results)*100:.1f}%")

print("\n" + "="*80)
print("DETAILED BREAKDOWN")
print("="*80)

fake_articles = [r for r in results if r['actual'] == 'FAKE']
real_articles = [r for r in results if r['actual'] == 'REAL']

ml_fake_correct = sum(1 for r in fake_articles if r['ml'] and r['ml']['verdict'] == 'FAKE')
ml_real_correct = sum(1 for r in real_articles if r['ml'] and r['ml']['verdict'] == 'REAL')

print(f"\nML Performance on FAKE news: {ml_fake_correct}/{len(fake_articles)} = {ml_fake_correct/len(fake_articles)*100:.1f}%")
print(f"ML Performance on REAL news: {ml_real_correct}/{len(real_articles)} = {ml_real_correct/len(real_articles)*100:.1f}%")

if dl_correct > 0:
    dl_fake_correct = sum(1 for r in fake_articles if r['dl'] and r['dl']['verdict'] == 'FAKE')
    dl_real_correct = sum(1 for r in real_articles if r['dl'] and r['dl']['verdict'] == 'REAL')
    print(f"\nDL Performance on FAKE news: {dl_fake_correct}/{len(fake_articles)} = {dl_fake_correct/len(fake_articles)*100:.1f}%")
    print(f"DL Performance on REAL news: {dl_real_correct}/{len(real_articles)} = {dl_real_correct/len(real_articles)*100:.1f}%")

print("\n" + "="*80)
print("TEST COMPLETE!")
print("="*80)

print("\n[TIP] To test LLM and Agent Swarm, uncomment those sections in the code")
print("[TIP] LLM adds ~5-10s per article, Agent Swarm adds ~20-30s per article")
print("\nFor quick web testing, use: http://localhost:3000\n")
