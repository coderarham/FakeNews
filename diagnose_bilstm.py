"""
diagnose_bilstm.py
Deep diagnosis of BiLSTM model to find why it predicts everything as REAL
"""

import os
import pickle
import numpy as np
from preprocess import clean_text

def diagnose_model():
    print("="*70)
    print("BiLSTM Model Diagnosis")
    print("="*70)
    
    try:
        import tensorflow as tf
        from tensorflow.keras.layers import Layer
        from tensorflow.keras.preprocessing.sequence import pad_sequences
        import tensorflow.keras.backend as K
        
        # Define custom AttentionLayer
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
        
        # Load model
        model_path = "saved_model/attention_bilstm_model.keras"
        print(f"\n[1] Loading model from: {model_path}")
        model = tf.keras.models.load_model(
            model_path,
            custom_objects={"AttentionLayer": AttentionLayer},
            compile=False
        )
        
        print(f"    Parameters: {model.count_params():,}")
        print(f"    Input shape: {model.input_shape}")
        print(f"    Output shape: {model.output_shape}")
        
        # Load tokenizer
        with open("saved_model/tokenizer.pkl", "rb") as f:
            tokenizer = pickle.load(f)
        print(f"\n[2] Tokenizer loaded: {len(tokenizer.word_index)} words")
        
        # Test cases
        test_cases = [
            ("FAKE - Clickbait", "SHOCKING SECRET REVEALED! Government hiding alien truth! Click now!"),
            ("FAKE - Conspiracy", "Anonymous sources confirm secret documents prove massive cover-up"),
            ("REAL - News", "The president announced new economic policies during press conference today"),
            ("REAL - Report", "According to Reuters, the stock market showed gains in morning trading"),
        ]
        
        print("\n" + "="*70)
        print("[3] Testing Predictions")
        print("="*70)
        
        raw_outputs = []
        
        for label, text in test_cases:
            # Preprocess
            cleaned = clean_text(text)
            seq = tokenizer.texts_to_sequences([cleaned])
            X = pad_sequences(seq, maxlen=512, padding="post")
            
            # Get raw prediction
            raw_pred = model.predict(X, verbose=0)[0][0]
            raw_outputs.append(raw_pred)
            
            verdict = "FAKE" if raw_pred > 0.5 else "REAL"
            
            print(f"\n{label}")
            print(f"  Text: {text[:60]}...")
            print(f"  Raw output: {raw_pred:.6f}")
            print(f"  Verdict: {verdict}")
        
        # Analyze outputs
        print("\n" + "="*70)
        print("[4] Analysis")
        print("="*70)
        
        print(f"\nRaw outputs: {[f'{x:.6f}' for x in raw_outputs]}")
        print(f"Min: {min(raw_outputs):.6f}")
        print(f"Max: {max(raw_outputs):.6f}")
        print(f"Mean: {np.mean(raw_outputs):.6f}")
        print(f"Std: {np.std(raw_outputs):.6f}")
        
        if max(raw_outputs) < 0.5:
            print("\n[PROBLEM FOUND] All outputs < 0.5 (always predicts REAL)")
            print("This means model is biased towards class 0 (REAL)")
        elif min(raw_outputs) > 0.5:
            print("\n[PROBLEM FOUND] All outputs > 0.5 (always predicts FAKE)")
            print("This means model is biased towards class 1 (FAKE)")
        elif max(raw_outputs) - min(raw_outputs) < 0.1:
            print("\n[PROBLEM FOUND] Very low variance in predictions")
            print("Model is not discriminating between REAL and FAKE")
        else:
            print("\n[OK] Model shows reasonable variance")
        
        # Check model weights
        print("\n" + "="*70)
        print("[5] Model Architecture Check")
        print("="*70)
        
        print("\nLayers:")
        for i, layer in enumerate(model.layers):
            print(f"  {i}: {layer.name} - {layer.__class__.__name__}")
        
        # Check final layer
        final_layer = model.layers[-1]
        print(f"\nFinal layer: {final_layer.name}")
        print(f"  Activation: {final_layer.activation.__name__ if hasattr(final_layer.activation, '__name__') else 'unknown'}")
        print(f"  Output shape: {final_layer.output_shape}")
        
        # Get weights of final layer
        weights = final_layer.get_weights()
        if len(weights) > 0:
            print(f"  Weight shape: {weights[0].shape}")
            print(f"  Weight mean: {np.mean(weights[0]):.6f}")
            print(f"  Weight std: {np.std(weights[0]):.6f}")
            if len(weights) > 1:
                print(f"  Bias: {weights[1]}")
        
        # Test with actual training data samples
        print("\n" + "="*70)
        print("[6] Testing with Training Data Samples")
        print("="*70)
        
        import pandas as pd
        
        # Load some real samples from dataset
        try:
            fake_df = pd.read_csv("Fake.csv")
            true_df = pd.read_csv("True.csv")
            
            print("\nTesting FAKE news from dataset:")
            fake_sample = fake_df.iloc[0]['text']
            cleaned = clean_text(fake_sample)
            seq = tokenizer.texts_to_sequences([cleaned])
            X = pad_sequences(seq, maxlen=512, padding="post")
            pred = model.predict(X, verbose=0)[0][0]
            print(f"  Sample: {fake_sample[:80]}...")
            print(f"  Raw output: {pred:.6f}")
            print(f"  Verdict: {'FAKE' if pred > 0.5 else 'REAL'}")
            
            print("\nTesting REAL news from dataset:")
            true_sample = true_df.iloc[0]['text']
            cleaned = clean_text(true_sample)
            seq = tokenizer.texts_to_sequences([cleaned])
            X = pad_sequences(seq, maxlen=512, padding="post")
            pred = model.predict(X, verbose=0)[0][0]
            print(f"  Sample: {true_sample[:80]}...")
            print(f"  Raw output: {pred:.6f}")
            print(f"  Verdict: {'FAKE' if pred > 0.5 else 'REAL'}")
            
        except Exception as e:
            print(f"  Could not load dataset: {e}")
        
        print("\n" + "="*70)
        print("[7] Conclusion")
        print("="*70)
        
        if max(raw_outputs) < 0.5:
            print("""
ISSUE: Model always predicts REAL (output < 0.5)

POSSIBLE CAUSES:
1. Model not properly trained (stopped too early)
2. Class imbalance during training
3. Wrong label encoding (0=REAL, 1=FAKE might be flipped)
4. Model converged to always predicting majority class

SOLUTIONS:
1. Re-train model with proper class weights
2. Check label encoding in train_dl.py
3. Use more epochs with early stopping
4. Balance the dataset before training
""")
        else:
            print("\nModel architecture looks OK. Check training process.")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_model()
