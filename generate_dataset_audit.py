"""
generate_dataset_audit.py
Performs 3 diagnostic operations on the ISOT dataset:
  1. Class imbalance ratio
  2. Exact + near-duplicate detection (MD5 + Jaccard on 4-grams)
  3. Reuters dateline bias quantification
Run: python generate_dataset_audit.py
"""

import re
import hashlib
import joblib
import pandas as pd
import numpy as np
from collections import defaultdict
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from preprocess import load_isot_dataset

REUTERS_PATTERN = re.compile(r"[A-Z\s]+(Reuters)", re.IGNORECASE)


# ── 1. Class Imbalance ─────────────────────────────────────────────────────
def class_imbalance(df):
    counts = df["label"].value_counts()
    ir = counts.max() / counts.min()
    print(f"\n[Audit] Class counts → FAKE={counts.get(1,0)}  REAL={counts.get(0,0)}")
    print(f"        Imbalance Ratio (IR) = {ir:.3f}")
    return ir


# ── 2. Duplicate Detection ─────────────────────────────────────────────────
def md5(text):
    return hashlib.md5(str(text).encode()).hexdigest()


def shingles(text, k=4):
    words = text.split()
    return set(" ".join(words[i:i+k]) for i in range(len(words) - k + 1))


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def find_duplicates(df, near_threshold=0.8, sample=5000):
    """Exact duplicates via MD5; near-duplicates via Jaccard on 4-grams (sampled)."""
    hashes = df["content"].apply(md5)
    exact = hashes.duplicated().sum()
    print(f"\n[Audit] Exact duplicates = {exact}")

    # Near-duplicate check on a sample to keep runtime reasonable
    sub = df["content"].sample(min(sample, len(df)), random_state=42).tolist()
    shingle_sets = [shingles(t) for t in sub]
    near = 0
    for i in range(len(shingle_sets)):
        for j in range(i + 1, len(shingle_sets)):
            if jaccard(shingle_sets[i], shingle_sets[j]) >= near_threshold:
                near += 1
    print(f"        Near-duplicates (Jaccard≥{near_threshold}, sample={sample}) = {near}")
    return exact, near


# ── 3. Reuters Bias ────────────────────────────────────────────────────────
def reuters_bias(df):
    raw_real = df[df["label"] == 0]["content"]
    raw_fake = df[df["label"] == 1]["content"]

    real_pct = raw_real.apply(lambda t: bool(REUTERS_PATTERN.search(t))).mean() * 100
    fake_pct = raw_fake.apply(lambda t: bool(REUTERS_PATTERN.search(t))).mean() * 100
    print(f"\n[Audit] Reuters dateline in REAL = {real_pct:.1f}%")
    print(f"        Reuters dateline in FAKE = {fake_pct:.1f}%")

    # Odds ratio via logistic regression on raw (un-stemmed) content
    raw_df = pd.concat([
        pd.read_csv("True.csv").assign(label=0),
        pd.read_csv("Fake.csv").assign(label=1),
    ], ignore_index=True)
    raw_df["content"] = (raw_df.get("title", "").fillna("") + " " +
                         raw_df.get("text", "").fillna(""))
    vec = TfidfVectorizer(max_features=10000, sublinear_tf=True)
    X = vec.fit_transform(raw_df["content"])
    y = raw_df["label"].values
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
    lr = LogisticRegression(max_iter=500, random_state=42)
    lr.fit(X_tr, y_tr)

    feature_names = vec.get_feature_names_out()
    coefs = lr.coef_[0]
    top5_idx = np.argsort(np.abs(coefs))[-5:][::-1]
    print("\n[Audit] Top-5 LR features (by |coef|):")
    for idx in top5_idx:
        odds = np.exp(coefs[idx])
        print(f"  '{feature_names[idx]}'  coef={coefs[idx]:.3f}  odds_ratio={odds:.1f}")

    return real_pct, fake_pct


# ── 4. Train-Test Vocabulary Overlap ──────────────────────────────────────
def vocab_overlap(df):
    X_tr, X_te = train_test_split(df["content"], test_size=0.2, random_state=42)
    train_vocab = set(" ".join(X_tr).split())
    test_vocab  = set(" ".join(X_te).split())
    overlap = len(train_vocab & test_vocab) / len(test_vocab) * 100
    print(f"\n[Audit] Train-Test vocabulary overlap = {overlap:.1f}%")
    return overlap


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    print("[Audit] Loading ISOT dataset...")
    df = load_isot_dataset()

    ir      = class_imbalance(df)
    exact, near = find_duplicates(df)
    real_pct, fake_pct = reuters_bias(df)
    overlap = vocab_overlap(df)

    report = {
        "imbalance_ratio": ir,
        "exact_duplicates": exact,
        "near_duplicates": near,
        "reuters_real_pct": real_pct,
        "reuters_fake_pct": fake_pct,
        "vocab_overlap_pct": overlap,
    }
    joblib.dump(report, "models/audit_report.pkl")
    print("\n[Audit] Report saved → models/audit_report.pkl")
    return report


if __name__ == "__main__":
    main()
