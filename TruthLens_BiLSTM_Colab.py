"""
TruthLens_BiLSTM_Training_Colab.ipynb

Copy this entire code to Google Colab and run cell by cell
GPU recommended for faster training (Runtime > Change runtime type > GPU)
"""

# ============================================================================
# CELL 1: Install Dependencies
# ============================================================================
!pip install -q pandas numpy scikit-learn nltk tensorflow

import nltk
nltk.download('stopwords')
nltk.download('punkt')

print("✅ Dependencies installed!")

# ============================================================================
# CELL 2: Upload Dataset Files
# ============================================================================
from google.colab import files
import os

print("📁 Upload Fake.csv and True.csv from your computer")
print("(These files are from ISOT Fake News Dataset)")
print()

uploaded = files.upload()

# Check if files uploaded
if 'Fake.csv' in uploaded and 'True.csv' in uploaded:
    print("✅ Dataset files uploaded successfully!")
else:
    print("❌ Please upload both Fake.csv and True.csv")

# ============================================================================
# CELL 3: Preprocessing Functions
# ============================================================================
import re
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

STEMMER = PorterStemmer()
STOP_WORDS = set(stopwords.words("english"))

def clean_text(text: str) -> str:
    """Clean and preprocess text"""
    text = str(text).lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    tokens = text.split()
    tokens = [STEMMER.stem(t) for t in tokens if t not in STOP_WORDS and len(t) > 2]
    return " ".join(tokens)

def load_isot_dataset(fake_path="Fake.csv", true_path="True.csv"):
    """Load and merge ISOT dataset"""
    fake = pd.read_csv(fake_path)
    true = pd.read_csv(true_path)
    
    fake["label"] = 1  # 1 = FAKE
    true["label"] = 0  # 0 = REAL
    
    df = pd.concat([fake, true], ignore_index=True).sample(frac=1, random_state=42)
    df["content"] = df.get("title", "").fillna("") + " " + df.get("text", "").fillna("")
    
    print(f"Cleaning {len(df)} articles...")
    df["content"] = df["content"].apply(clean_text)
    
    return df

print("✅ Preprocessing functions defined!")

# ============================================================================
# CELL 4: Load and Prepare Data
# ============================================================================
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

print("📊 Loading dataset...")
df = load_isot_dataset()

print(f"Total samples: {len(df)}")
print(f"FAKE: {sum(df['label']==1)}")
print(f"REAL: {sum(df['label']==0)}")

# Hyperparameters
MAX_VOCAB = 35000
MAX_LEN = 256
BATCH_SIZE = 128
EPOCHS = 10

print(f"\n🔧 Tokenizing (vocab={MAX_VOCAB}, max_len={MAX_LEN})...")
tok = Tokenizer(num_words=MAX_VOCAB, oov_token="<OOV>")
tok.fit_on_texts(df["content"])
seqs = tok.texts_to_sequences(df["content"])
X = pad_sequences(seqs, maxlen=MAX_LEN, padding="post", truncating="post")
y = df["label"].values

print(f"Vocabulary size: {len(tok.word_index)}")
print(f"Sequence shape: {X.shape}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
X_train, X_val, y_train, y_val = train_test_split(
    X_train, y_train, test_size=0.1, random_state=42, stratify=y_train
)

print(f"\n📦 Data split:")
print(f"  Train: {len(X_train)} (FAKE: {sum(y_train==1)}, REAL: {sum(y_train==0)})")
print(f"  Val:   {len(X_val)} (FAKE: {sum(y_val==1)}, REAL: {sum(y_val==0)})")
print(f"  Test:  {len(X_test)} (FAKE: {sum(y_test==1)}, REAL: {sum(y_test==0)})")

print("\n✅ Data ready for training!")

# ============================================================================
# CELL 5: Build Model Architecture
# ============================================================================
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (Input, Embedding, Conv1D, MaxPooling1D,
                                     Bidirectional, LSTM, Dense, Dropout, Layer)
import tensorflow.keras.backend as K

class AttentionLayer(Layer):
    """Custom Attention Layer"""
    def __init__(self, units=32, **kwargs):
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

def build_bilstm_model(vocab_size):
    """Build Attention BiLSTM Model"""
    inp = Input(shape=(MAX_LEN,))
    x = Embedding(vocab_size, 64)(inp)
    x = Conv1D(64, 5, activation="relu", padding="same")(x)
    x = MaxPooling1D(pool_size=2)(x)
    x = Bidirectional(LSTM(64, return_sequences=True))(x)
    context, _ = AttentionLayer(32)(x)
    x = Dense(64, activation="relu")(context)
    x = Dropout(0.3)(x)
    x = Dense(32, activation="relu")(x)
    x = Dropout(0.3)(x)
    out = Dense(1, activation="sigmoid")(x)
    
    model = Model(inputs=inp, outputs=out)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )
    return model

vocab_size = min(MAX_VOCAB, len(tok.word_index)) + 1
model = build_bilstm_model(vocab_size)

print("🧠 Model Architecture:")
model.summary()

print(f"\n✅ Model built with {model.count_params():,} parameters!")

# ============================================================================
# CELL 6: Train Model (This will take 5-10 minutes)
# ============================================================================
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import os

os.makedirs('saved_model', exist_ok=True)

print("🚀 Starting training...")
print("⏱️  This will take 5-10 minutes (faster with GPU)")
print()

callbacks = [
    EarlyStopping(monitor="val_loss", patience=3, 
                 restore_best_weights=True, verbose=1),
    ModelCheckpoint("saved_model/attention_bilstm_model.keras", 
                   save_best_only=True, verbose=1)
]

history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=callbacks,
    verbose=1
)

print("\n✅ Training complete!")

# ============================================================================
# CELL 7: Evaluate Model
# ============================================================================
print("📊 Evaluating on test set...")

loss, acc = model.evaluate(X_test, y_test, verbose=0)
print(f"\n🎯 Test Results:")
print(f"  Loss: {loss:.4f}")
print(f"  Accuracy: {acc:.4f} ({acc*100:.2f}%)")

# Test on sample predictions
print("\n🧪 Testing predictions...")

fake_idx = np.where(y_test == 1)[0][:5]
real_idx = np.where(y_test == 0)[0][:5]

print("\n  FAKE samples from test set:")
for idx in fake_idx:
    pred = model.predict(X_test[idx:idx+1], verbose=0)[0][0]
    verdict = "FAKE" if pred > 0.5 else "REAL"
    emoji = "✅" if verdict == "FAKE" else "❌"
    print(f"    {emoji} Prediction: {pred:.4f} -> {verdict}")

print("\n  REAL samples from test set:")
for idx in real_idx:
    pred = model.predict(X_test[idx:idx+1], verbose=0)[0][0]
    verdict = "FAKE" if pred > 0.5 else "REAL"
    emoji = "✅" if verdict == "REAL" else "❌"
    print(f"    {emoji} Prediction: {pred:.4f} -> {verdict}")

# ============================================================================
# CELL 8: Test with Custom Text
# ============================================================================
def predict_text(text):
    """Predict if text is FAKE or REAL"""
    cleaned = clean_text(text)
    seq = tok.texts_to_sequences([cleaned])
    padded = pad_sequences(seq, maxlen=MAX_LEN, padding="post")
    pred = model.predict(padded, verbose=0)[0][0]
    verdict = "FAKE" if pred > 0.5 else "REAL"
    return verdict, pred

print("🧪 Testing with custom examples:")
print()

test_cases = [
    "SHOCKING: Secret government documents reveal alien technology in smartphones!",
    "President announces new economic policy during press conference today",
    "BREAKING NEWS: Whistleblower exposes massive conspiracy! Click here!",
    "According to Reuters, the stock market showed gains in morning trading"
]

for text in test_cases:
    verdict, confidence = predict_text(text)
    emoji = "⚠️" if verdict == "FAKE" else "✅"
    print(f"{emoji} {verdict} ({confidence:.2f})")
    print(f"   {text[:70]}...")
    print()

# ============================================================================
# CELL 9: Save Model and Tokenizer
# ============================================================================
import pickle

print("💾 Saving model and tokenizer...")

# Save model
model.save("saved_model/attention_bilstm_model.keras")
print("  ✅ Model saved: saved_model/attention_bilstm_model.keras")

# Save tokenizer
with open("saved_model/tokenizer.pkl", "wb") as f:
    pickle.dump(tok, f)
print("  ✅ Tokenizer saved: saved_model/tokenizer.pkl")

print("\n📦 Download these files to use in your project:")
print("  1. saved_model/attention_bilstm_model.keras")
print("  2. saved_model/tokenizer.pkl")

# ============================================================================
# CELL 10: Download Files
# ============================================================================
from google.colab import files

print("⬇️ Downloading trained model files...")

files.download("saved_model/attention_bilstm_model.keras")
files.download("saved_model/tokenizer.pkl")

print("\n✅ Download complete!")
print("\n📝 Next steps:")
print("  1. Copy these files to your project's 'saved_model/' folder")
print("  2. Run: python quick_test.py 'Your article text'")
print("  3. BiLSTM will now work properly!")

# ============================================================================
# CELL 11: Training History Visualization (Optional)
# ============================================================================
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 4))

# Accuracy plot
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Val Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)

# Loss plot
plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Val Loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

print(f"\n🎯 Final Training Accuracy: {history.history['accuracy'][-1]*100:.2f}%")
print(f"🎯 Final Validation Accuracy: {history.history['val_accuracy'][-1]*100:.2f}%")
print(f"🎯 Test Accuracy: {acc*100:.2f}%")
