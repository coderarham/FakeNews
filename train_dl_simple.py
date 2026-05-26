"""
train_dl_simple.py
Simplified BiLSTM using Keras 3 (works without AVX)
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# Use Keras 3 standalone (no TensorFlow dependency)
os.environ['KERAS_BACKEND'] = 'numpy'

try:
    import keras
    from keras import layers, models, optimizers
    print(f"Using Keras {keras.__version__} with numpy backend")
except:
    print("Keras not available. Installing...")
    os.system("pip install keras>=3.0")
    import keras
    from keras import layers, models, optimizers

from preprocess import load_isot_dataset, clean_text

os.makedirs("saved_model", exist_ok=True)

# Hyperparameters
MAX_VOCAB = 80000
MAX_LEN = 512
EMB_DIM = 128
LSTM_UNITS = 128
DROPOUT = 0.3
BATCH_SIZE = 64
EPOCHS = 15

class SimpleTokenizer:
    def __init__(self, max_vocab=80000):
        self.max_vocab = max_vocab
        self.word2idx = {"<PAD>": 0, "<OOV>": 1}
        self.idx2word = {0: "<PAD>", 1: "<OOV>"}
    
    def fit(self, texts):
        from collections import Counter
        words = []
        for text in texts:
            words.extend(str(text).lower().split())
        word_counts = Counter(words)
        for idx, (word, _) in enumerate(word_counts.most_common(self.max_vocab - 2), start=2):
            self.word2idx[word] = idx
            self.idx2word[idx] = word
    
    def texts_to_sequences(self, texts):
        sequences = []
        for text in texts:
            seq = [self.word2idx.get(word, 1) for word in str(text).lower().split()]
            sequences.append(seq)
        return sequences
    
    def pad_sequences(self, sequences, maxlen=512):
        padded = np.zeros((len(sequences), maxlen), dtype=np.int32)
        for i, seq in enumerate(sequences):
            length = min(len(seq), maxlen)
            padded[i, :length] = seq[:length]
        return padded

def build_simple_model(vocab_size):
    """Simplified BiLSTM without attention (faster, works everywhere)"""
    model = models.Sequential([
        layers.Embedding(vocab_size, EMB_DIM, input_length=MAX_LEN),
        layers.Bidirectional(layers.LSTM(LSTM_UNITS, return_sequences=False)),
        layers.Dense(128, activation='relu'),
        layers.Dropout(DROPOUT),
        layers.Dense(64, activation='relu'),
        layers.Dropout(DROPOUT),
        layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer=optimizers.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    return model

def main():
    print("[train_dl] Loading dataset...")
    df = load_isot_dataset()
    
    print("[train_dl] Tokenizing...")
    tok = SimpleTokenizer(max_vocab=MAX_VOCAB)
    tok.fit(df["content"])
    seqs = tok.texts_to_sequences(df["content"])
    X = tok.pad_sequences(seqs, maxlen=MAX_LEN)
    y = df["label"].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.1, random_state=42, stratify=y_train)
    
    print(f"  Train={len(X_train)}  Val={len(X_val)}  Test={len(X_test)}")
    
    print("[train_dl] Building model...")
    model = build_simple_model(len(tok.word2idx))
    
    print("[train_dl] Training (this will take 20-30 minutes)...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        verbose=1
    )
    
    print("[train_dl] Evaluating...")
    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"[train_dl] Test accuracy={acc:.4f}  loss={loss:.4f}")
    
    print("[train_dl] Saving model...")
    model.save("saved_model/bilstm_model.keras")
    with open("saved_model/tokenizer.pkl", "wb") as f:
        pickle.dump(tok, f)
    
    # Save metrics
    metrics = {
        'accuracy': acc,
        'loss': loss,
        'history': history.history
    }
    with open("saved_model/dl_metrics.pkl", "wb") as f:
        pickle.dump(metrics, f)
    
    print("[train_dl] Done! Model saved to saved_model/")

if __name__ == "__main__":
    main()
