"""
find_low_confidence.py
Find articles where BiLSTM has low confidence (uncertain predictions)
"""

import pandas as pd
import pickle
import numpy as np
from preprocess import clean_text

def find_uncertain_predictions():
    print("="*70)
    print("Finding Low Confidence Predictions")
    print("="*70)
    
    # Load model
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
        
        print("\n[1] Loading model...")
        model = tf.keras.models.load_model(
            "saved_model/attention_bilstm_model.keras",
            custom_objects={"AttentionLayer": AttentionLayer},
            compile=False
        )
        
        with open("saved_model/tokenizer.pkl", "rb") as f:
            tokenizer = pickle.load(f)
        
        print(f"    Model loaded")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return
    
    # Load dataset
    print("\n[2] Loading dataset...")
    fake_df = pd.read_csv("Fake.csv")
    true_df = pd.read_csv("True.csv")
    
    # Sample 100 from each
    fake_sample = fake_df.sample(100, random_state=42)
    true_sample = true_df.sample(100, random_state=42)
    
    print(f"    Testing 200 articles...")
    
    # Find uncertain predictions (close to 0.5)
    uncertain_cases = []
    
    print("\n[3] Searching for uncertain predictions...")
    
    for idx, row in fake_sample.iterrows():
        text = row['text']
        cleaned = clean_text(text)
        seq = tokenizer.texts_to_sequences([cleaned])
        X = pad_sequences(seq, maxlen=256, padding="post")
        
        pred = model.predict(X, verbose=0)[0][0]
        confidence = abs(pred - 0.5)  # Distance from 0.5
        
        if confidence < 0.3:  # Within 0.2-0.8 range
            uncertain_cases.append({
                'title': row['title'],
                'text': row['text'][:200],
                'actual': 'FAKE',
                'prediction': pred,
                'confidence': confidence,
                'verdict': 'FAKE' if pred > 0.5 else 'REAL'
            })
    
    for idx, row in true_sample.iterrows():
        text = row['text']
        cleaned = clean_text(text)
        seq = tokenizer.texts_to_sequences([cleaned])
        X = pad_sequences(seq, maxlen=256, padding="post")
        
        pred = model.predict(X, verbose=0)[0][0]
        confidence = abs(pred - 0.5)
        
        if confidence < 0.3:
            uncertain_cases.append({
                'title': row['title'],
                'text': row['text'][:200],
                'actual': 'REAL',
                'prediction': pred,
                'confidence': confidence,
                'verdict': 'FAKE' if pred > 0.5 else 'REAL'
            })
    
    # Sort by confidence (lowest first)
    uncertain_cases.sort(key=lambda x: x['confidence'])
    
    print(f"    Found {len(uncertain_cases)} uncertain predictions")
    
    # Display results
    print("\n" + "="*70)
    print("LOW CONFIDENCE PREDICTIONS (Most Uncertain)")
    print("="*70)
    
    if len(uncertain_cases) == 0:
        print("\nNo uncertain predictions found!")
        print("Model is very confident on all predictions.")
        print("\nLet's create some ambiguous test cases instead...")
        
        # Create ambiguous test cases
        ambiguous_tests = [
            "The government announced new policies today according to sources",
            "Reports suggest that economic changes may be coming soon",
            "Officials say they are considering various options for reform",
            "Analysts predict potential shifts in the political landscape",
            "Sources close to the matter indicate possible developments ahead",
            "The situation remains unclear as discussions continue behind closed doors",
            "Experts are divided on the implications of recent events",
            "Speculation grows about what the future may hold for the nation"
        ]
        
        print("\nTesting ambiguous sentences:")
        print("="*70)
        
        for text in ambiguous_tests:
            cleaned = clean_text(text)
            seq = tokenizer.texts_to_sequences([cleaned])
            X = pad_sequences(seq, maxlen=256, padding="post")
            
            pred = model.predict(X, verbose=0)[0][0]
            verdict = "FAKE" if pred > 0.5 else "REAL"
            confidence = abs(pred - 0.5) * 2 * 100  # Convert to percentage
            
            print(f"\nText: {text}")
            print(f"  Prediction: {pred:.4f}")
            print(f"  Verdict: {verdict}")
            print(f"  Confidence: {confidence:.1f}%")
            
            if confidence < 60:
                print(f"  [LOW CONFIDENCE - Model is uncertain]")
    
    else:
        for i, case in enumerate(uncertain_cases[:10], 1):
            print(f"\n[{i}] Title: {case['title'][:60]}...")
            print(f"    Actual: {case['actual']}")
            print(f"    Predicted: {case['verdict']} (score: {case['prediction']:.4f})")
            print(f"    Confidence: {case['confidence']*2*100:.1f}%")
            print(f"    Text: {case['text']}...")
            
            if case['actual'] == case['verdict']:
                print(f"    Result: CORRECT (but uncertain)")
            else:
                print(f"    Result: WRONG")
    
    print("\n" + "="*70)
    print("ANALYSIS")
    print("="*70)
    
    if len(uncertain_cases) == 0:
        print("""
Model is VERY CONFIDENT on all predictions (0.0 or 1.0).

This means:
1. Model has learned strong patterns from training data
2. Test samples are similar to training data
3. Model uses extreme sigmoid outputs

To get uncertain predictions, try:
- Neutral news (no strong opinion)
- Short snippets (less context)
- Mixed tone articles (both positive and negative)
- Ambiguous statements
""")
    else:
        print(f"""
Found {len(uncertain_cases)} uncertain predictions out of 200 samples.

These are cases where model is confused:
- Predictions between 0.2 and 0.8
- Model cannot clearly classify as FAKE or REAL
- May need human verification
""")
    
    print("="*70)

if __name__ == "__main__":
    find_uncertain_predictions()
