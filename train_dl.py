"""
train_dl.py
Build and train the Attention BiLSTM model described in the TruthLens report.
Run: python train_dl.py
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (Input, Embedding, Conv1D, MaxPooling1D,
                                     Bidirectional, LSTM, Dense, Dropout,
                                     Layer, Multiply, Softmax, Lambda)
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import tensorflow.keras.backend as K

from preprocess import load_isot_dataset, clean_text

os.makedirs("saved_model", exist_ok=True)

# ── Hyperparameters (Table 2) ──────────────────────────────────────────────
MAX_VOCAB    = 80000
MAX_LEN      = 512
EMB_DIM      = 128
CONV_FILTERS = 128
CONV_KERNEL  = 5
LSTM_UNITS   = 128
ATTN_DIM     = 64
DROPOUT      = 0.3
BATCH_SIZE   = 64
EPOCHS       = 15
PATIENCE     = 3


# ── Custom Attention Layer ─────────────────────────────────────────────────
class AttentionLayer(Layer):
    """Bahdanau-style additive attention over BiLSTM hidden states."""

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
        # H: (batch, T, 2*LSTM_UNITS)
        score = K.tanh(K.dot(H, self.W) + self.b)   # (batch, T, units)
        score = K.dot(score, self.u)                  # (batch, T, 1)
        alpha = K.softmax(score, axis=1)              # (batch, T, 1)
        context = K.sum(H * alpha, axis=1)            # (batch, 2*LSTM_UNITS)
        return context, alpha

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"units": self.units})
        return cfg


def build_model(vocab_size):
    inp = Input(shape=(MAX_LEN,))
    x = Embedding(vocab_size, EMB_DIM, mask_zero=False)(inp)
    x = Conv1D(CONV_FILTERS, CONV_KERNEL, activation="relu", padding="same")(x)
    x = MaxPooling1D(pool_size=2)(x)
    x = Bidirectional(LSTM(LSTM_UNITS, return_sequences=True))(x)
    context, _ = AttentionLayer(ATTN_DIM)(x)
    x = Dense(128, activation="relu")(context)
    x = Dropout(DROPOUT)(x)
    x = Dense(64, activation="relu")(x)
    x = Dropout(DROPOUT)(x)
    out = Dense(1, activation="sigmoid")(x)
    model = Model(inputs=inp, outputs=out)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
                  loss="binary_crossentropy",
                  metrics=["accuracy"])
    return model


def main():
    print("[train_dl] Loading dataset...")
    df = load_isot_dataset()

    tok = Tokenizer(num_words=MAX_VOCAB, oov_token="<OOV>")
    tok.fit_on_texts(df["content"])
    seqs = tok.texts_to_sequences(df["content"])
    X = pad_sequences(seqs, maxlen=MAX_LEN, padding="post", truncating="post")
    y = df["label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.1, random_state=42, stratify=y_train)

    print(f"  Train={len(X_train)}  Val={len(X_val)}  Test={len(X_test)}")

    model = build_model(min(MAX_VOCAB, len(tok.word_index)) + 1)
    model.summary()

    callbacks = [
        EarlyStopping(monitor="val_loss", patience=PATIENCE, restore_best_weights=True),
        ModelCheckpoint("saved_model/best_bilstm.keras", save_best_only=True),
    ]

    model.fit(X_train, y_train,
              validation_data=(X_val, y_val),
              epochs=EPOCHS,
              batch_size=BATCH_SIZE,
              callbacks=callbacks)

    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"[train_dl] Test accuracy={acc:.4f}  loss={loss:.4f}")

    model.save("saved_model/attention_bilstm")
    with open("saved_model/tokenizer.pkl", "wb") as f:
        pickle.dump(tok, f)
    print("[train_dl] Model + tokenizer saved to saved_model/")


if __name__ == "__main__":
    main()
