"""
quick_test.py
Quick BiLSTM test with command line argument
Usage: python quick_test.py "Your news article text here"
"""

import sys
import os
import pickle
from preprocess import clean_text

def predict_bilstm(text):
    """Load model and predict"""
    try:
        import tensorflow as tf
        from tensorflow.keras.layers import Layer
        from tensorflow.keras.preprocessing.sequence import pad_sequences
        import tensorflow.keras.backend as K
        
        # Define custom AttentionLayer
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
        
        # Load model
        model_path = "saved_model/attention_bilstm_model.keras"
        if not os.path.exists(model_path):
            model_path = "saved_model/attention_bilstm"
        
        print("Loading BiLSTM model...")
        model = tf.keras.models.load_model(
            model_path,
            custom_objects={"AttentionLayer": AttentionLayer},
            compile=False
        )
        
        with open("saved_model/tokenizer.pkl", "rb") as f:
            tokenizer = pickle.load(f)
        
        print(f"[OK] Model loaded: {model.count_params():,} parameters\n")
        
        # Preprocess
        cleaned = clean_text(text)
        seq = tokenizer.texts_to_sequences([cleaned])
        X = pad_sequences(seq, maxlen=256, padding="post")
        
        # Predict
        pred_prob = model.predict(X, verbose=0)[0][0]
        verdict = "FAKE" if pred_prob > 0.5 else "REAL"
        confidence = pred_prob if pred_prob > 0.5 else 1 - pred_prob
        
        return verdict, confidence, pred_prob
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return None, None, None


if __name__ == "__main__":
    print("=" * 70)
    print("TruthLens BiLSTM - Quick Test")
    print("=" * 70)
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python quick_test.py \"Your news article text\"")
        print("\nExample:")
        print('  python quick_test.py "Breaking news: Scientists discover alien life"')
        print()
        
        # Use default test cases
        test_cases = [
            "Breaking news: Scientists discover new planet in solar system",
            "President announces new economic policy to boost growth",
            "SHOCKING: Secret government conspiracy revealed! Click here!",
            "Study shows climate change affecting global temperatures"
        ]
        
        print("Running default test cases:\n")
        for i, text in enumerate(test_cases, 1):
            print(f"\n[Test {i}] {text[:60]}...")
            verdict, confidence, fake_prob = predict_bilstm(text)
            
            if verdict:
                print(f"  VERDICT: {verdict}")
                print(f"  Confidence: {confidence*100:.2f}%")
                print(f"  Fake Probability: {fake_prob*100:.2f}%")
    else:
        text = " ".join(sys.argv[1:])
        print(f"Input: {text}\n")
        
        verdict, confidence, fake_prob = predict_bilstm(text)
        
        if verdict:
            print("\n" + "=" * 70)
            print(f"VERDICT: {verdict}")
            print(f"Confidence: {confidence*100:.2f}%")
            print(f"Fake Probability: {fake_prob*100:.2f}%")
            print("=" * 70)
