"""
test_bilstm_dataset.py
Test BiLSTM with actual ISOT dataset samples
"""

import pandas as pd
import pickle
from preprocess import clean_text

def test_with_dataset():
    print("="*70)
    print("BiLSTM Testing with ISOT Dataset Samples")
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
        
        print(f"    Model: {model.count_params():,} parameters")
        print(f"    Tokenizer: {len(tokenizer.word_index)} words")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return
    
    # Load dataset samples
    print("\n[2] Loading dataset samples...")
    fake_df = pd.read_csv("Fake.csv")
    true_df = pd.read_csv("True.csv")
    
    print(f"    Fake articles: {len(fake_df)}")
    print(f"    Real articles: {len(true_df)}")
    
    # Test on 10 random samples from each
    print("\n" + "="*70)
    print("TESTING ON FAKE NEWS SAMPLES")
    print("="*70)
    
    fake_samples = fake_df.sample(10, random_state=42)
    fake_correct = 0
    fake_predictions = []
    
    for idx, row in fake_samples.iterrows():
        text = row['text']
        cleaned = clean_text(text)
        seq = tokenizer.texts_to_sequences([cleaned])
        X = pad_sequences(seq, maxlen=256, padding="post")
        
        pred = model.predict(X, verbose=0)[0][0]
        verdict = "FAKE" if pred > 0.5 else "REAL"
        is_correct = verdict == "FAKE"
        fake_correct += is_correct
        fake_predictions.append(pred)
        
        emoji = "[OK]" if is_correct else "[X]"
        print(f"{emoji} Pred: {pred:.4f} -> {verdict} | Title: {row['title'][:50]}...")
    
    print(f"\nFake News Accuracy: {fake_correct}/10 ({fake_correct*10}%)")
    print(f"Prediction range: {min(fake_predictions):.4f} to {max(fake_predictions):.4f}")
    
    # Test on REAL news
    print("\n" + "="*70)
    print("TESTING ON REAL NEWS SAMPLES")
    print("="*70)
    
    real_samples = true_df.sample(10, random_state=42)
    real_correct = 0
    real_predictions = []
    
    for idx, row in real_samples.iterrows():
        text = row['text']
        cleaned = clean_text(text)
        seq = tokenizer.texts_to_sequences([cleaned])
        X = pad_sequences(seq, maxlen=256, padding="post")
        
        pred = model.predict(X, verbose=0)[0][0]
        verdict = "FAKE" if pred > 0.5 else "REAL"
        is_correct = verdict == "REAL"
        real_correct += is_correct
        real_predictions.append(pred)
        
        emoji = "[OK]" if is_correct else "[X]"
        print(f"{emoji} Pred: {pred:.4f} -> {verdict} | Title: {row['title'][:50]}...")
    
    print(f"\nReal News Accuracy: {real_correct}/10 ({real_correct*10}%)")
    print(f"Prediction range: {min(real_predictions):.4f} to {max(real_predictions):.4f}")
    
    # Overall statistics
    print("\n" + "="*70)
    print("OVERALL STATISTICS")
    print("="*70)
    
    all_predictions = fake_predictions + real_predictions
    
    print(f"Total Accuracy: {(fake_correct + real_correct)}/20 ({(fake_correct + real_correct)*5}%)")
    print(f"\nPrediction Statistics:")
    print(f"  Min:  {min(all_predictions):.6f}")
    print(f"  Max:  {max(all_predictions):.6f}")
    print(f"  Mean: {sum(all_predictions)/len(all_predictions):.6f}")
    
    import numpy as np
    std = np.std(all_predictions)
    print(f"  Std:  {std:.6f}")
    
    # Analysis
    print("\n" + "="*70)
    print("ANALYSIS")
    print("="*70)
    
    if std < 0.01:
        print("[X] PROBLEM: Very low variance in predictions")
        print("   Model is not discriminating properly")
        print("   All predictions are too similar")
    elif max(all_predictions) < 0.1:
        print("[X] PROBLEM: All predictions near 0")
        print("   Model always predicts REAL")
    elif min(all_predictions) > 0.9:
        print("[X] PROBLEM: All predictions near 1")
        print("   Model always predicts FAKE")
    else:
        print("[OK] Model shows reasonable variance")
        print(f"   Fake news predictions: {min(fake_predictions):.4f} - {max(fake_predictions):.4f}")
        print(f"   Real news predictions: {min(real_predictions):.4f} - {max(real_predictions):.4f}")
    
    # Check if model is just memorizing
    if fake_correct == 10 and real_correct == 10:
        print("\n⚠️  WARNING: 100% accuracy might indicate:")
        print("   1. Model is working perfectly (unlikely)")
        print("   2. Model is overfitting to training data")
        print("   3. Test samples are too similar to training data")
    
    print("\n" + "="*70)
    print("RECOMMENDATION")
    print("="*70)
    
    if (fake_correct + real_correct) >= 16:
        print("[OK] Model is working reasonably well")
        print("   Use it for detection, but verify important cases")
    else:
        print("[X] Model needs retraining")
        print("   Current accuracy too low for production use")
        print("   Upload TruthLens_BiLSTM_Training.ipynb to Colab")
    
    print("="*70)

if __name__ == "__main__":
    test_with_dataset()
