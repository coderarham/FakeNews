"""
train_ml.py
Train 5 ML classifiers on ISOT dataset and save models to /models folder.
Run: python train_ml.py
"""

import os
import joblib
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, f1_score, roc_auc_score)
from preprocess import load_isot_dataset, get_train_test_split

os.makedirs("models", exist_ok=True)

CLASSIFIERS = {
    "decision_tree":      DecisionTreeClassifier(random_state=42),
    "gradient_boosting":  GradientBoostingClassifier(n_estimators=100, random_state=42),
    "linear_svc":         LinearSVC(C=1.0, max_iter=2000, random_state=42),
    "logistic_regression":LogisticRegression(C=1.0, max_iter=1000, random_state=42),
    "random_forest":      RandomForestClassifier(n_estimators=100, random_state=42),
}


def evaluate(model, X_test, y_test, name):
    y_pred = model.predict(X_test)
    # LinearSVC has no predict_proba; use decision_function for AUC
    if hasattr(model, "predict_proba"):
        y_score = model.predict_proba(X_test)[:, 1]
    else:
        y_score = model.decision_function(X_test)
    metrics = {
        "accuracy":  round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall":    round(recall_score(y_test, y_pred), 4),
        "f1":        round(f1_score(y_test, y_pred), 4),
        "auc_roc":   round(roc_auc_score(y_test, y_score), 4),
    }
    print(f"  [{name}] acc={metrics['accuracy']} f1={metrics['f1']} auc={metrics['auc_roc']}")
    return metrics


def majority_vote(models, X):
    preds = np.array([m.predict(X) for m in models])   # shape (5, n_samples)
    return (preds.sum(axis=0) > 2).astype(int)          # majority of 5


def main():
    print("[train_ml] Loading ISOT dataset...")
    df = load_isot_dataset()
    (X_train, X_test, y_train, y_test), vec = get_train_test_split(df)
    print(f"  Train={X_train.shape[0]}  Test={X_test.shape[0]}")

    results = {}
    trained = {}
    for name, clf in CLASSIFIERS.items():
        print(f"[train_ml] Training {name}...")
        clf.fit(X_train, y_train)
        results[name] = evaluate(clf, X_test, y_test, name)
        joblib.dump(clf, f"models/{name}.pkl")
        trained[name] = clf

    # Majority ensemble evaluation
    models_list = list(trained.values())
    y_ens = majority_vote(models_list, X_test)
    results["ensemble"] = {
        "accuracy":  round(accuracy_score(y_test, y_ens), 4),
        "precision": round(precision_score(y_test, y_ens), 4),
        "recall":    round(recall_score(y_test, y_ens), 4),
        "f1":        round(f1_score(y_test, y_ens), 4),
        "auc_roc":   None,
    }
    print(f"  [ensemble] acc={results['ensemble']['accuracy']} f1={results['ensemble']['f1']}")

    joblib.dump(results, "models/ml_metrics.pkl")
    print("[train_ml] Done. All models saved to /models")


if __name__ == "__main__":
    main()
