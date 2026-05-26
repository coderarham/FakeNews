"""
preprocess.py
Shared preprocessing pipeline: cleaning, tokenizing, stemming, TF-IDF vectorization.
"""

import re
import os
import joblib
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

try:
    nltk.download("stopwords", quiet=True)
    nltk.download("punkt", quiet=True)
except:
    pass  # Already downloaded

STEMMER = PorterStemmer()
STOP_WORDS = set(stopwords.words("english"))
TFIDF_PATH = "tfidf_vectorizer.pkl"


def clean_text(text: str) -> str:
    """Lowercase → remove non-alpha → tokenize → remove stopwords → stem."""
    text = str(text).lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    tokens = text.split()
    tokens = [STEMMER.stem(t) for t in tokens if t not in STOP_WORDS and len(t) > 2]
    return " ".join(tokens)


def load_isot_dataset(fake_path="Fake.csv", true_path="True.csv") -> pd.DataFrame:
    """Load and merge ISOT Fake/True CSVs into a single labelled DataFrame."""
    fake = pd.read_csv(fake_path)
    true = pd.read_csv(true_path)
    fake["label"] = 1   # 1 = FAKE
    true["label"] = 0   # 0 = REAL
    df = pd.concat([fake, true], ignore_index=True).sample(frac=1, random_state=42)
    # Combine title + text for richer features
    df["content"] = df.get("title", "").fillna("") + " " + df.get("text", "").fillna("")
    df["content"] = df["content"].apply(clean_text)
    return df


def build_tfidf(texts, max_features=81500, save=True):
    """Fit TF-IDF vectorizer and optionally save to disk."""
    vec = TfidfVectorizer(max_features=max_features, sublinear_tf=True)
    X = vec.fit_transform(texts)
    if save:
        joblib.dump(vec, TFIDF_PATH)
        print(f"[preprocess] TF-IDF saved -> {TFIDF_PATH}  shape={X.shape}")
    return vec, X


def load_tfidf():
    """Load a previously saved TF-IDF vectorizer."""
    if not os.path.exists(TFIDF_PATH):
        raise FileNotFoundError(f"{TFIDF_PATH} not found. Run train_ml.py first.")
    return joblib.load(TFIDF_PATH)


def get_train_test_split(df, test_size=0.2):
    """Return (X_train, X_test, y_train, y_test) as TF-IDF matrices."""
    vec, X = build_tfidf(df["content"])
    y = df["label"].values
    return train_test_split(X, y, test_size=test_size, random_state=42, stratify=y), vec
