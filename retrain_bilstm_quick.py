"""
retrain_bilstm_quick.py
Quick retrain of BiLSTM with proper monitoring
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (Input, Embedding, Conv1D, MaxPooling1D,
                                     Bidirectional, LSTM, Dense, Dropout, Layer)
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import tensorflow.keras.backend as K

from preprocess import load_isot_dataset

# Reduced hyperparameters for faster training
MAX_VOCAB = 35000  # Reduced from 80000
MAX_LEN = 256      # Reduced from 512
EMB_DIM = 64       # Reduced from 128
CONV_FILTERS = 64  # Reduced from 128
LSTM_UNITS = 64    # Reduced from 128
ATTN_DIM = 32      # Reduced from 64
DROPOUT = 0.3
BATCH_SIZE = 128   # Increased for faster training
EPOCHS = 10
PATIENCE = 3

class AttentionLayer(Layer):
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

def build_model(vocab_size):
    inp = Input(shape=(MAX_LEN,))
    x = Embedding(vocab_size, EMB_DIM)(inp)
    x = Conv1D(CONV_FILTERS, 5, activation="relu", padding="same")(x)
    x = MaxPooling1D(pool_size=2)(x)
    x = Bidirectional(LSTM(LSTM_UNITS, return_sequences=True))(x)
    context, _ = AttentionLayer(ATTN_DIM)(x)
    x = Dense(64, activation="relu")(context)
    x = Dropout(DROPOUT)(x)
    x = Dense(32, activation="relu")(x)
    x = Dropout(DROPOUT)(x)
    out = Dense(1, activation="sigmoid")(x)
    
    model = Model(inputs=inp, outputs=out)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )
    return model

def main():
    print("="*70)
    print("BiLSTM Quick Retrain")
    print("="*70)
    
    # Load data
    print("\n[1] Loading ISOT dataset...")
    df = load_isot_dataset()
    print(f"    Total samples: {len(df)}")
    print(f"    FAKE: {sum(df['label']==1)}")
    print(f"    REAL: {sum(df['label']==0)}")
    
    # Tokenize
    print("\n[2] Tokenizing...")
    tok = Tokenizer(num_words=MAX_VOCAB, oov_token="<OOV>")
    tok.fit_on_texts(df["content"])
    seqs = tok.texts_to_sequences(df["content"])
    X = pad_sequences(seqs, maxlen=MAX_LEN, padding="post", truncating="post")
    y = df["label"].values
    
    print(f"    Vocabulary size: {len(tok.word_index)}")
    print(f"    Sequence shape: {X.shape}")
    
    # Split data
    print("\n[3] Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.1, random_state=42, stratify=y_train
    )
    
    print(f"    Train: {len(X_train)} (FAKE: {sum(y_train==1)}, REAL: {sum(y_train==0)})")
    print(f"    Val:   {len(X_val)} (FAKE: {sum(y_val==1)}, REAL: {sum(y_val==0)})")
    print(f"    Test:  {len(X_test)} (FAKE: {sum(y_test==1)}, REAL: {sum(y_test==0)})")
    
    # Build model
    print("\n[4] Building model...")
    vocab_size = min(MAX_VOCAB, len(tok.word_index)) + 1
    model = build_model(vocab_size)
    
    print(f"    Total parameters: {model.count_params():,}")
    
    # Train
    print("\n[5] Training...")
    print("    This will take 5-10 minutes...")
    
    callbacks = [
        EarlyStopping(monitor="val_loss", patience=PATIENCE, 
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
    
    # Evaluate
    print("\n[6] Evaluating...")
    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"    Test Loss: {loss:.4f}")
    print(f"    Test Accuracy: {acc:.4f} ({acc*100:.2f}%)")
    
    # Test predictions
    print("\n[7] Testing predictions...")
    
    # Get some fake and real samples
    fake_idx = np.where(y_test == 1)[0][:5]
    real_idx = np.where(y_test == 0)[0][:5]
    
    print("\n    FAKE samples:")
    for idx in fake_idx:
        pred = model.predict(X_test[idx:idx+1], verbose=0)[0][0]
        print(f"      Prediction: {pred:.4f} -> {'FAKE' if pred > 0.5 else 'REAL'}")
    
    print("\n    REAL samples:")
    for idx in real_idx:
        pred = model.predict(X_test[idx:idx+1], verbose=0)[0][0]
        print(f"      Prediction: {pred:.4f} -> {'FAKE' if pred > 0.5 else 'REAL'}")
    
    # Save
    print("\n[8] Saving model...")
    model.save("saved_model/attention_bilstm_model.keras")
    with open("saved_model/tokenizer.pkl", "wb") as f:
        pickle.dump(tok, f)
    
    print("\n" + "="*70)
    print("Training Complete!")
    print("="*70)
    print(f"Model saved to: saved_model/attention_bilstm_model.keras")
    print(f"Tokenizer saved to: saved_model/tokenizer.pkl")
    print(f"Final accuracy: {acc*100:.2f}%")
    print("="*70)

if __name__ == "__main__":
    main()
