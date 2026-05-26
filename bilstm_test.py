"""
bilstm_test.py
Simple CLI to test BiLSTM model with user input
Run: python bilstm_test.py
"""

import os
import pickle
from preprocess import clean_text

def load_bilstm():
    """Load BiLSTM model with custom AttentionLayer"""
    try:
        import tensorflow as tf
        from tensorflow.keras.layers import Layer
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
        
        # Try loading model
        model_paths = [
            "saved_model/attention_bilstm_model.keras",
            "saved_model/attention_bilstm"
        ]
        
        for model_path in model_paths:
            if os.path.exists(model_path):
                print(f"Loading model from: {model_path}")
                model = tf.keras.models.load_model(
                    model_path,
                    custom_objects={"AttentionLayer": AttentionLayer},
                    compile=False
                )
                
                with open("saved_model/tokenizer.pkl", "rb") as f:
                    tokenizer = pickle.load(f)
                
                print(f"[OK] Model loaded: {model.count_params():,} parameters")
                print(f"[OK] Tokenizer loaded: {len(tokenizer.word_index)} words\n")
                return model, tokenizer
        
        print("[ERROR] Model file not found!")
        return None, None
        
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return None, None


def predict(model, tokenizer, text):
    """Make prediction on input text"""
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    
    # Preprocess
    cleaned = clean_text(text)
    
    # Tokenize and pad
    seq = tokenizer.texts_to_sequences([cleaned])
    X = pad_sequences(seq, maxlen=512, padding="post")
    
    # Predict
    pred_prob = model.predict(X, verbose=0)[0][0]
    verdict = "FAKE" if pred_prob > 0.5 else "REAL"
    confidence = pred_prob if pred_prob > 0.5 else 1 - pred_prob
    
    return verdict, confidence, pred_prob


def main():
    print("=" * 70)
    print("TruthLens BiLSTM - Fake News Detection")
    print("=" * 70)
    print()
    
    # Load model
    model, tokenizer = load_bilstm()
    
    if not model:
        print("\n[ERROR] Cannot proceed without model. Please train first:")
        print("  python train_dl.py")
        return
    
    print("Model ready! Enter news articles to analyze.")
    print("Type 'quit' or 'exit' to stop.\n")
    print("-" * 70)
    
    while True:
        print("\nEnter article text (or 'quit' to exit):")
        text = input("> ").strip()
        
        if text.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if not text:
            print("[ERROR] Please enter some text!")
            continue
        
        print("\nAnalyzing...")
        verdict, confidence, fake_prob = predict(model, tokenizer, text)
        
        print("\n" + "=" * 70)
        print(f"VERDICT: {verdict}")
        print(f"Confidence: {confidence*100:.2f}%")
        print(f"Fake Probability: {fake_prob*100:.2f}%")
        print("=" * 70)


if __name__ == "__main__":
    main()
