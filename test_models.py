"""
test_models.py
Quick test script to verify ML and BiLSTM models are working
"""

import os
import sys

def test_ml_models():
    """Test if ML models can load and predict"""
    print("\n=== Testing ML Models ===")
    try:
        import joblib
        from preprocess import load_tfidf, clean_text
        
        # Check if models exist
        model_files = ["decision_tree.pkl", "gradient_boosting.pkl", 
                      "linear_svc.pkl", "logistic_regression.pkl", "random_forest.pkl"]
        
        missing = [f for f in model_files if not os.path.exists(f"models/{f}")]
        if missing:
            print(f"[X] Missing models: {missing}")
            print("   Run: python train_ml.py")
            return False
        
        # Load vectorizer
        if not os.path.exists("tfidf_vectorizer.pkl"):
            print("[X] TF-IDF vectorizer not found")
            print("   Run: python train_ml.py")
            return False
        
        vec = load_tfidf()
        print(f"[OK] TF-IDF loaded: {vec.max_features} features")
        
        # Test prediction
        test_text = "Breaking news: Scientists discover new planet in solar system"
        cleaned = clean_text(test_text)
        X = vec.transform([cleaned])
        
        for model_name in model_files:
            model = joblib.load(f"models/{model_name.replace('.pkl', '')}.pkl")
            pred = model.predict(X)[0]
            print(f"[OK] {model_name.replace('.pkl', ''):20s} -> {'FAKE' if pred == 1 else 'REAL'}")
        
        print("[SUCCESS] All ML models working!")
        return True
        
    except Exception as e:
        print(f"[ERROR] ML models error: {e}")
        return False


def test_bilstm():
    """Test if BiLSTM model can load and predict"""
    print("\n=== Testing BiLSTM Model ===")
    try:
        import pickle
        import numpy as np
        from tensorflow.keras.models import load_model
        from tensorflow.keras.preprocessing.sequence import pad_sequences
        from tensorflow.keras.layers import Layer
        import tensorflow.keras.backend as K
        from preprocess import clean_text
        
        # Define AttentionLayer for loading
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
        
        # Check if model exists
        model_paths = ["saved_model/attention_bilstm", "saved_model/attention_bilstm_model.keras"]
        model_path = None
        for path in model_paths:
            if os.path.exists(path):
                model_path = path
                break
        
        if not model_path:
            print("[X] BiLSTM model not found")
            print("   Run: python train_dl.py")
            return False
        
        if not os.path.exists("saved_model/tokenizer.pkl"):
            print("[X] Tokenizer not found")
            print("   Run: python train_dl.py")
            return False
        
        # Load model and tokenizer
        print(f"Loading model from: {model_path}")
        model = load_model(model_path, custom_objects={"AttentionLayer": AttentionLayer}, compile=False)
        print(f"[OK] Model loaded: {model.count_params():,} parameters")
        
        with open("saved_model/tokenizer.pkl", "rb") as f:
            tokenizer = pickle.load(f)
        print(f"[OK] Tokenizer loaded: {len(tokenizer.word_index)} words")
        
        # Test prediction
        test_text = "Breaking news: Scientists discover new planet in solar system"
        cleaned = clean_text(test_text)
        seq = tokenizer.texts_to_sequences([cleaned])
        X = pad_sequences(seq, maxlen=512, padding="post")
        
        pred = model.predict(X, verbose=0)[0][0]
        label = "FAKE" if pred > 0.5 else "REAL"
        print(f"[OK] Prediction: {label} (confidence: {pred:.4f})")
        
        print("[SUCCESS] BiLSTM model working!")
        return True
        
    except Exception as e:
        print(f"[ERROR] BiLSTM error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("TruthLens Model Testing")
    print("=" * 60)
    
    ml_ok = test_ml_models()
    bilstm_ok = test_bilstm()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"ML Models:    {'[WORKING]' if ml_ok else '[FAILED]'}")
    print(f"BiLSTM Model: {'[WORKING]' if bilstm_ok else '[FAILED]'}")
    print("=" * 60)
    
    if ml_ok and bilstm_ok:
        print("\n[SUCCESS] All systems operational!")
        return 0
    else:
        print("\n[WARNING] Some models need training")
        return 1


if __name__ == "__main__":
    sys.exit(main())
