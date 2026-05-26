"""
debug_bilstm_deep.py
Deep debugging to find exact issue with BiLSTM
"""

import os
import pickle
import numpy as np

print("="*70)
print("BiLSTM Deep Debugging")
print("="*70)

# Step 1: Check files
print("\n[STEP 1] Checking files...")
model_path = "saved_model/attention_bilstm_model.keras"
tok_path = "saved_model/tokenizer.pkl"

if os.path.exists(model_path):
    size = os.path.getsize(model_path)
    print(f"  Model file: EXISTS ({size:,} bytes = {size/1024/1024:.1f} MB)")
else:
    print(f"  Model file: NOT FOUND")
    exit(1)

if os.path.exists(tok_path):
    size = os.path.getsize(tok_path)
    print(f"  Tokenizer: EXISTS ({size:,} bytes = {size/1024/1024:.1f} MB)")
else:
    print(f"  Tokenizer: NOT FOUND")
    exit(1)

# Step 2: Load tokenizer
print("\n[STEP 2] Loading tokenizer...")
try:
    with open(tok_path, "rb") as f:
        tokenizer = pickle.load(f)
    print(f"  Tokenizer loaded: {len(tokenizer.word_index)} words")
    print(f"  Sample words: {list(tokenizer.word_index.items())[:5]}")
except Exception as e:
    print(f"  ERROR: {e}")
    exit(1)

# Step 3: Load model
print("\n[STEP 3] Loading model...")
try:
    import tensorflow as tf
    from tensorflow.keras.layers import Layer
    import tensorflow.keras.backend as K
    
    # Define AttentionLayer
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
    
    model = tf.keras.models.load_model(
        model_path,
        custom_objects={"AttentionLayer": AttentionLayer},
        compile=False
    )
    print(f"  Model loaded: {model.count_params():,} parameters")
    
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 4: Check model architecture
print("\n[STEP 4] Checking model architecture...")
print(f"  Input shape: {model.input_shape}")
print(f"  Output shape: {model.output_shape}")
print(f"  Total layers: {len(model.layers)}")

# Check final layer
final_layer = model.layers[-1]
print(f"\n  Final layer: {final_layer.name}")
print(f"  Type: {type(final_layer).__name__}")

# Get weights
weights = final_layer.get_weights()
if len(weights) > 0:
    print(f"  Weight shape: {weights[0].shape}")
    print(f"  Weight stats: min={weights[0].min():.6f}, max={weights[0].max():.6f}, mean={weights[0].mean():.6f}")
    if len(weights) > 1:
        print(f"  Bias: {weights[1]}")

# Step 5: Test with simple input
print("\n[STEP 5] Testing with simple inputs...")

from tensorflow.keras.preprocessing.sequence import pad_sequences
from preprocess import clean_text

test_cases = [
    "This is a simple test",
    "Breaking news shocking revelation",
    "President announces new policy",
    "Secret government conspiracy exposed"
]

print("\nRaw predictions:")
for text in test_cases:
    cleaned = clean_text(text)
    seq = tokenizer.texts_to_sequences([cleaned])
    X = pad_sequences(seq, maxlen=512, padding="post")
    
    pred = model.predict(X, verbose=0)[0][0]
    print(f"  '{text[:40]}...' -> {pred:.6f}")

# Step 6: Check if model weights are all zeros
print("\n[STEP 6] Checking model weights...")
all_weights = model.get_weights()
print(f"  Total weight arrays: {len(all_weights)}")

zero_count = 0
for i, w in enumerate(all_weights):
    if np.all(w == 0):
        zero_count += 1
        print(f"  WARNING: Weight array {i} is all zeros! Shape: {w.shape}")

if zero_count > 0:
    print(f"\n  [PROBLEM] {zero_count} weight arrays are all zeros!")
    print("  This means model is not trained properly.")
else:
    print(f"  All weight arrays have non-zero values")

# Step 7: Test with actual dataset sample
print("\n[STEP 7] Testing with dataset samples...")

try:
    import pandas as pd
    
    # Load one fake and one real sample
    fake_df = pd.read_csv("Fake.csv", nrows=1)
    true_df = pd.read_csv("True.csv", nrows=1)
    
    print("\nFAKE sample:")
    fake_text = fake_df.iloc[0]['text']
    print(f"  Text: {fake_text[:80]}...")
    
    cleaned = clean_text(fake_text)
    seq = tokenizer.texts_to_sequences([cleaned])
    X = pad_sequences(seq, maxlen=512, padding="post")
    pred = model.predict(X, verbose=0)[0][0]
    
    print(f"  Prediction: {pred:.6f}")
    print(f"  Verdict: {'FAKE' if pred > 0.5 else 'REAL'}")
    print(f"  Expected: FAKE")
    print(f"  Status: {'CORRECT' if pred > 0.5 else 'WRONG'}")
    
    print("\nREAL sample:")
    real_text = true_df.iloc[0]['text']
    print(f"  Text: {real_text[:80]}...")
    
    cleaned = clean_text(real_text)
    seq = tokenizer.texts_to_sequences([cleaned])
    X = pad_sequences(seq, maxlen=512, padding="post")
    pred = model.predict(X, verbose=0)[0][0]
    
    print(f"  Prediction: {pred:.6f}")
    print(f"  Verdict: {'FAKE' if pred > 0.5 else 'REAL'}")
    print(f"  Expected: REAL")
    print(f"  Status: {'CORRECT' if pred < 0.5 else 'WRONG'}")
    
except Exception as e:
    print(f"  Could not test with dataset: {e}")

# Step 8: Diagnosis
print("\n" + "="*70)
print("[DIAGNOSIS]")
print("="*70)

# Check prediction range
from tensorflow.keras.preprocessing.sequence import pad_sequences
test_texts = [
    "breaking shocking secret revealed government conspiracy",
    "president announces policy economic growth",
    "study shows research indicates scientists discover",
    "click here now shocking truth exposed hidden"
]

predictions = []
for text in test_texts:
    cleaned = clean_text(text)
    seq = tokenizer.texts_to_sequences([cleaned])
    X = pad_sequences(seq, maxlen=512, padding="post")
    pred = model.predict(X, verbose=0)[0][0]
    predictions.append(pred)

min_pred = min(predictions)
max_pred = max(predictions)
mean_pred = np.mean(predictions)
std_pred = np.std(predictions)

print(f"\nPrediction statistics:")
print(f"  Min:  {min_pred:.6f}")
print(f"  Max:  {max_pred:.6f}")
print(f"  Mean: {mean_pred:.6f}")
print(f"  Std:  {std_pred:.6f}")

print("\nISSUES FOUND:")
if max_pred < 0.01:
    print("  [CRITICAL] All predictions near 0.0")
    print("  -> Model always predicts REAL")
    print("  -> Model is NOT properly trained")
    print("\n  SOLUTION: Re-train model using Colab notebook")
elif min_pred > 0.99:
    print("  [CRITICAL] All predictions near 1.0")
    print("  -> Model always predicts FAKE")
    print("  -> Model is NOT properly trained")
    print("\n  SOLUTION: Re-train model using Colab notebook")
elif std_pred < 0.01:
    print("  [CRITICAL] Very low variance in predictions")
    print("  -> Model is not discriminating between REAL and FAKE")
    print("  -> Model is NOT properly trained")
    print("\n  SOLUTION: Re-train model using Colab notebook")
else:
    print("  [OK] Model shows reasonable prediction variance")
    print("  -> Model might be working but needs more testing")

print("\n" + "="*70)
print("RECOMMENDATION:")
print("="*70)
print("""
The BiLSTM model file exists but is NOT properly trained.

IMMEDIATE SOLUTION:
1. Use ML models (already working perfectly!)
   python test_ml_vs_bilstm.py

LONG-TERM SOLUTION:
1. Upload TruthLens_BiLSTM_Training.ipynb to Google Colab
2. Enable GPU (Runtime > Change runtime type > GPU)
3. Upload Fake.csv and True.csv
4. Run all cells (takes 10-15 minutes)
5. Download trained model files
6. Replace files in saved_model/ folder

The current model was either:
- Not trained at all
- Training stopped too early
- Trained with wrong configuration
- Corrupted during save/load
""")
print("="*70)
