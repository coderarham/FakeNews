"""
test_bilstm_low_confidence.py
Find articles where BiLSTM gives LOW confidence (not 100%)
"""

from dl_predictor import DLPredictor

print("="*70)
print("TESTING BiLSTM FOR LOW CONFIDENCE")
print("="*70)

# Articles designed to confuse BiLSTM
test_articles = [
    {
        "name": "Ultra Neutral - No emotion",
        "text": "The event occurred on Monday. People attended. Information was shared. The session ended at 5 PM."
    },
    {
        "name": "Dry Government Statement",
        "text": "The committee met to discuss budget allocations for the fiscal year. Various proposals were reviewed. Further meetings are scheduled."
    },
    {
        "name": "Academic Abstract",
        "text": "This study examines the relationship between variables A and B. Data was collected from 200 participants. Results indicate a correlation coefficient of 0.45."
    },
    {
        "name": "Weather Report",
        "text": "Temperatures will range from 15 to 20 degrees Celsius. Partly cloudy conditions expected. Wind speed approximately 10 km/h from the northwest."
    },
    {
        "name": "Stock Market Update",
        "text": "The index closed at 15,234 points, up 0.3% from yesterday. Trading volume was moderate. Analysts expect continued stability."
    },
    {
        "name": "Recipe Instructions",
        "text": "Preheat oven to 180 degrees. Mix flour, sugar, and eggs. Bake for 25 minutes. Allow to cool before serving."
    },
    {
        "name": "Sports Score",
        "text": "The match ended with a score of 2-1. First half was goalless. Both teams played defensively. Attendance was approximately 30,000."
    },
    {
        "name": "Meeting Minutes",
        "text": "Attendees: John, Mary, Steve. Agenda items discussed. Action points assigned. Next meeting scheduled for next Tuesday."
    },
    {
        "name": "Product Description",
        "text": "This device measures 15cm x 10cm x 5cm. Weight is 200 grams. Available in black and white. Battery life approximately 8 hours."
    },
    {
        "name": "Train Schedule",
        "text": "Train departs at 9:15 AM from Platform 3. Stops at Central Station at 9:45 AM. Arrives at destination at 10:30 AM."
    }
]

dl_predictor = DLPredictor()

if not dl_predictor.model:
    print("ERROR: BiLSTM model not loaded!")
    exit(1)

print("\nTesting BiLSTM with neutral/ambiguous articles...\n")

results = []

for article in test_articles:
    print("="*70)
    print(f"TEST: {article['name']}")
    print("="*70)
    print(f"Text: {article['text']}")
    print()
    
    result = dl_predictor.predict(article['text'])
    
    if result:
        confidence = result['confidence']
        verdict = result['verdict']
        
        print(f"Verdict: {verdict}")
        print(f"Confidence: {confidence*100:.2f}%")
        
        # Analyze confidence level
        if confidence >= 0.95:
            level = "VERY HIGH (>95%)"
        elif confidence >= 0.80:
            level = "HIGH (80-95%)"
        elif confidence >= 0.60:
            level = "MEDIUM (60-80%)"
        else:
            level = "LOW (<60%)"
        
        print(f"Confidence Level: {level}")
        
        results.append({
            'name': article['name'],
            'verdict': verdict,
            'confidence': confidence * 100
        })
    else:
        print("ERROR: Prediction failed")
    
    print()

# Summary
print("="*70)
print("SUMMARY - SORTED BY CONFIDENCE (LOWEST FIRST)")
print("="*70)

results_sorted = sorted(results, key=lambda x: x['confidence'])

for r in results_sorted:
    print(f"{r['confidence']:6.2f}% | {r['verdict']:10s} | {r['name']}")

print("\n" + "="*70)
print("ANALYSIS")
print("="*70)

low_conf = [r for r in results if r['confidence'] < 80]
medium_conf = [r for r in results if 80 <= r['confidence'] < 95]
high_conf = [r for r in results if r['confidence'] >= 95]

print(f"\nLow Confidence (<80%):    {len(low_conf)}")
print(f"Medium Confidence (80-95%): {len(medium_conf)}")
print(f"High Confidence (>95%):   {len(high_conf)}")

if low_conf:
    print("\nArticles with LOW confidence:")
    for r in low_conf:
        print(f"  - {r['name']} ({r['confidence']:.1f}%)")
else:
    print("\nNO LOW CONFIDENCE FOUND!")
    print("BiLSTM is VERY confident even on neutral text.")
    print("This means the model is well-trained but may be overconfident.")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print("""
BiLSTM gives 100% confidence because:

1. WELL-TRAINED MODEL
   - Trained on 40K+ articles
   - Learned strong patterns
   - Very decisive

2. SIGMOID ACTIVATION
   - Outputs get squashed to extremes
   - 0.9999 becomes "100%"
   - 0.0001 becomes "0%"

3. CLEAR PATTERNS
   - Even neutral text has patterns
   - Model picks up subtle cues
   - Makes strong predictions

TO GET LOW CONFIDENCE:
- Need truly ambiguous text
- Mixed signals (some fake, some real indicators)
- Very short text (not enough info)
- Completely random/nonsense text
""")
print("="*70)
