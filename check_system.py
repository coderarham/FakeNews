"""
check_system.py
Quick system verification for TruthLens
"""

import os
import sys

print("=" * 70)
print("TRUTHLENS SYSTEM CHECK")
print("=" * 70)
print()

# 1. Check Python version
print("[1/6] Python Version:")
print(f"  {sys.version}")
print()

# 2. Check dataset files
print("[2/6] Dataset Files:")
fake_exists = os.path.exists("Fake.csv")
true_exists = os.path.exists("True.csv")
if fake_exists:
    size = os.path.getsize("Fake.csv") / (1024*1024)
    print(f"  [OK] Fake.csv ({size:.1f} MB)")
else:
    print("  [MISSING] Fake.csv")

if true_exists:
    size = os.path.getsize("True.csv") / (1024*1024)
    print(f"  [OK] True.csv ({size:.1f} MB)")
else:
    print("  [MISSING] True.csv")
print()

# 3. Check ML models
print("[3/6] ML Models:")
ml_models = ["decision_tree", "gradient_boosting", "linear_svc", 
             "logistic_regression", "random_forest"]
trained = 0
for model in ml_models:
    if os.path.exists(f"models/{model}.pkl"):
        print(f"  [OK] {model}.pkl")
        trained += 1
    else:
        print(f"  [MISSING] {model}.pkl")

if os.path.exists("tfidf_vectorizer.pkl"):
    print(f"  [OK] tfidf_vectorizer.pkl")
else:
    print(f"  [MISSING] tfidf_vectorizer.pkl")
print(f"  Total: {trained}/5 models trained")
print()

# 4. Check DL model
print("[4/6] Deep Learning Model:")
if os.path.exists("saved_model/attention_bilstm_model.keras"):
    size = os.path.getsize("saved_model/attention_bilstm_model.keras") / (1024*1024)
    print(f"  [OK] attention_bilstm_model.keras ({size:.1f} MB)")
elif os.path.exists("saved_model/attention_bilstm"):
    print("  [OK] attention_bilstm model (folder format)")
else:
    print("  [MISSING] attention_bilstm model")

if os.path.exists("saved_model/tokenizer.pkl"):
    print("  [OK] tokenizer.pkl")
else:
    print("  [MISSING] tokenizer.pkl")
print()

# 5. Check key dependencies
print("[5/6] Key Dependencies:")
deps = [
    ("sklearn", "Scikit-Learn"),
    ("pandas", "Pandas"),
    ("numpy", "NumPy"),
    ("flask", "Flask"),
]

for module, name in deps:
    try:
        __import__(module)
        print(f"  [OK] {name}")
    except ImportError:
        print(f"  [MISSING] {name}")
print()

# 6. Check frontend
print("[6/6] Frontend:")
if os.path.exists("frontend/package.json"):
    print("  [OK] React frontend setup")
    if os.path.exists("frontend/node_modules"):
        print("  [OK] Node modules installed")
    else:
        print("  [PENDING] Run: cd frontend && npm install")
else:
    print("  [MISSING] Frontend not found")
print()

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)

if fake_exists and true_exists:
    print("[OK] Dataset ready")
else:
    print("[ACTION NEEDED] Download ISOT dataset")

if trained == 5:
    print("[OK] ML models trained")
else:
    print("[ACTION NEEDED] Run: python train_ml.py")

if os.path.exists("saved_model/attention_bilstm_model.keras") or os.path.exists("saved_model/attention_bilstm"):
    print("[OK] DL model trained")
else:
    print("[OPTIONAL] Run: python train_dl.py (if TensorFlow works)")

if os.path.exists("frontend/package.json"):
    print("[OK] Frontend ready")
    if not os.path.exists("frontend/node_modules"):
        print("[ACTION NEEDED] Run: cd frontend && npm install")
else:
    print("[INFO] Frontend available")

print()
print("=" * 70)
print("READY TO RUN:")
print("  Backend:   python backend_api.py")
print("  Frontend:  cd frontend && npm run dev")
print("=" * 70)
