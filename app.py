"""
app.py
TruthLens — Multimodal Fake News Detection System
6-Tab Streamlit Interface: ML, DL, LLM, Comparison, Live News, Agent Swarm
Run: streamlit run app.py
"""

import os
import sys
import pickle
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import pytesseract
import cv2

# Import local modules
from preprocess import clean_text, load_tfidf
from news_scraper import start_scheduler, stop_scheduler, get_cached_articles
from fact_swarm import run_swarm

# ══════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="TruthLens — Fake News Detection",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS — Dark Cyberpunk Theme
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 100%);}
    .stTabs [data-baseweb="tab-list"] {gap: 8px;}
    .stTabs [data-baseweb="tab"] {
        background: #16213e;
        border-radius: 8px;
        padding: 12px 24px;
        color: #00d9ff;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #00d9ff 0%, #7b2cbf 100%);
        color: white;
    }
    h1, h2, h3 {color: #00d9ff; text-shadow: 0 0 10px rgba(0,217,255,0.5);}
    .verdict-real {
        background: linear-gradient(135deg, #06ffa5 0%, #00d9ff 100%);
        padding: 20px;
        border-radius: 12px;
        color: #0a0e27;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        margin: 20px 0;
    }
    .verdict-fake {
        background: linear-gradient(135deg, #ff006e 0%, #fb5607 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        margin: 20px 0;
    }
    .metric-card {
        background: rgba(22, 33, 62, 0.8);
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #00d9ff;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# LOAD MODELS (cached)
# ══════════════════════════════════════════════════════════════════════════
@st.cache_resource
def load_ml_models():
    models = {}
    for name in ["decision_tree", "gradient_boosting", "linear_svc", 
                 "logistic_regression", "random_forest"]:
        path = f"models/{name}.pkl"
        if os.path.exists(path):
            models[name] = joblib.load(path)
    return models

@st.cache_resource
def load_dl_model():
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
        
        # Try both .keras file and folder format
        model_paths = [
            "saved_model/attention_bilstm_model.keras",
            "saved_model/attention_bilstm"
        ]
        tok_path = "saved_model/tokenizer.pkl"
        
        for model_path in model_paths:
            if os.path.exists(model_path) and os.path.exists(tok_path):
                model = tf.keras.models.load_model(
                    model_path, 
                    custom_objects={"AttentionLayer": AttentionLayer},
                    compile=False
                )
                with open(tok_path, "rb") as f:
                    tokenizer = pickle.load(f)
                return model, tokenizer
    except ImportError:
        pass  # TensorFlow not available
    except Exception as e:
        st.sidebar.warning(f"DL model load error: {str(e)[:50]}...")
    return None, None

@st.cache_resource
def load_metrics():
    path = "models/ml_metrics.pkl"
    if os.path.exists(path):
        return joblib.load(path)
    return {}

# ══════════════════════════════════════════════════════════════════════════
# LLM ENSEMBLE
# ══════════════════════════════════════════════════════════════════════════
def llm_ensemble_predict(text: str) -> dict:
    """Call LLaMA 3.3 70B via Groq API."""
    from groq import Groq
    import json, re
    
    GROQ_KEY = os.getenv("GROQ_API_KEY", "")
    
    if not GROQ_KEY:
        return {
            "verdict": "ERROR",
            "confidence": 0.0,
            "error": "GROQ_API_KEY not found in .env"
        }
    
    prompt = f"""Analyze this news article for fake news detection.
Provide JSON response with:
- verdict: REAL / FAKE / UNCERTAIN
- confidence: 0.0-1.0
- factual_consistency_score: 0.0-1.0
- sensationalism_score: 0.0-1.0
- source_credibility_score: 0.0-1.0
- writing_style_score: 0.0-1.0
- reasoning: brief explanation

ARTICLE:
{text[:2000]}

Respond ONLY with valid JSON."""
    
    try:
        client = Groq(api_key=GROQ_KEY)
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        txt = resp.choices[0].message.content
        match = re.search(r'\{.*\}', txt, re.DOTALL)
        
        if match:
            result = json.loads(match.group())
            return {
                "verdict": result.get("verdict", "UNCERTAIN"),
                "confidence": result.get("confidence", 0.5),
                "factual_consistency_score": result.get("factual_consistency_score", 0.5),
                "sensationalism_score": result.get("sensationalism_score", 0.5),
                "source_credibility_score": result.get("source_credibility_score", 0.5),
                "writing_style_score": result.get("writing_style_score", 0.5),
                "reasoning": result.get("reasoning", "No reasoning provided")
            }
        else:
            return {
                "verdict": "ERROR",
                "confidence": 0.0,
                "error": "Could not parse JSON from LLaMA response"
            }
    
    except Exception as e:
        return {
            "verdict": "ERROR",
            "confidence": 0.0,
            "error": str(e)
        }

# ══════════════════════════════════════════════════════════════════════════
# OCR
# ══════════════════════════════════════════════════════════════════════════
def extract_text_from_image(img: Image.Image) -> str:
    """Preprocess + Tesseract OCR."""
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    img_cv = cv2.GaussianBlur(img_cv, (5, 5), 0)
    img_cv = cv2.adaptiveThreshold(img_cv, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 11, 2)
    text = pytesseract.image_to_string(img_cv)
    return text

# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/truth.png", width=80)
    st.title("🔍 TruthLens")
    st.markdown("**AI-Powered Fake News Detection**")
    st.markdown("---")
    st.markdown("### 📊 System Status")
    
    ml_models = load_ml_models()
    dl_model, dl_tok = load_dl_model()
    
    st.metric("ML Models Loaded", len(ml_models))
    if dl_model:
        st.metric("DL Model", "✅ Ready")
    else:
        st.metric("DL Model", "❌ Not Available (TensorFlow issue)")
    st.metric("Agent Swarm", "20 Agents")
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    enable_scraper = st.checkbox("Enable Live News Scraper", value=False)
    
    if enable_scraper:
        start_scheduler()
        st.success("Scraper running (30 min interval)")
    else:
        stop_scheduler()

# ══════════════════════════════════════════════════════════════════════════
# MAIN TABS
# ══════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🤖 ML Classifiers",
    "🧠 Deep Learning",
    "🌐 LLM Ensemble",
    "📊 Model Comparison",
    "📰 Live News",
    "🕸️ Agent Swarm"
])

# ──────────────────────────────────────────────────────────────────────────
# TAB 1: ML CLASSIFIERS
# ──────────────────────────────────────────────────────────────────────────
with tab1:
    st.header("🤖 Traditional Machine Learning Pipeline")
    st.markdown("5 classifiers + Majority Vote Ensemble")
    
    input_method = st.radio("Input Method:", ["Text", "Image (OCR)"], horizontal=True)
    
    if input_method == "Text":
        article_text = st.text_area("Enter article text:", height=200,
                                     placeholder="Paste news article here...")
    else:
        uploaded_img = st.file_uploader("Upload image:", type=["png", "jpg", "jpeg"])
        if uploaded_img:
            img = Image.open(uploaded_img)
            st.image(img, width=400)
            article_text = extract_text_from_image(img)
            st.text_area("Extracted Text:", article_text, height=150)
        else:
            article_text = ""
    
    if st.button("🔍 Analyze with ML", key="ml_btn"):
        if not article_text.strip():
            st.error("Please provide text input.")
        elif not ml_models:
            st.error("ML models not found. Run train_ml.py first.")
        else:
            with st.spinner("Processing..."):
                cleaned = clean_text(article_text)
                vec = load_tfidf()
                X = vec.transform([cleaned])
                
                predictions = {}
                for name, model in ml_models.items():
                    pred = model.predict(X)[0]
                    predictions[name] = "FAKE" if pred == 1 else "REAL"
                
                # Majority vote
                votes = list(predictions.values())
                final = "FAKE" if votes.count("FAKE") > len(votes) / 2 else "REAL"
                
                st.markdown("### 🎯 Ensemble Verdict")
                if final == "REAL":
                    st.markdown('<div class="verdict-real">✅ REAL NEWS</div>', 
                                unsafe_allow_html=True)
                else:
                    st.markdown('<div class="verdict-fake">⚠️ FAKE NEWS</div>', 
                                unsafe_allow_html=True)
                
                st.markdown("### 📋 Individual Model Predictions")
                cols = st.columns(5)
                for i, (name, verdict) in enumerate(predictions.items()):
                    with cols[i]:
                        emoji = "✅" if verdict == "REAL" else "⚠️"
                        st.metric(name.replace("_", " ").title(), f"{emoji} {verdict}")

# ──────────────────────────────────────────────────────────────────────────
# TAB 2: DEEP LEARNING
# ──────────────────────────────────────────────────────────────────────────
with tab2:
    st.header("🧠 Attention BiLSTM Neural Network")
    st.markdown("35M parameters | 99.96% accuracy")
    
    input_method_dl = st.radio("Input Method:", ["Text", "Image (OCR)"], 
                                horizontal=True, key="dl_input")
    
    if input_method_dl == "Text":
        article_text_dl = st.text_area("Enter article text:", height=200,
                                        placeholder="Paste news article here...",
                                        key="dl_text")
    else:
        uploaded_img_dl = st.file_uploader("Upload image:", type=["png", "jpg", "jpeg"],
                                            key="dl_img")
        if uploaded_img_dl:
            img_dl = Image.open(uploaded_img_dl)
            st.image(img_dl, width=400)
            article_text_dl = extract_text_from_image(img_dl)
            st.text_area("Extracted Text:", article_text_dl, height=150, key="dl_ocr")
        else:
            article_text_dl = ""
    
    if st.button("🔍 Analyze with Deep Learning", key="dl_btn"):
        if not article_text_dl.strip():
            st.error("Please provide text input.")
        elif not dl_model:
            st.error("DL model not available. TensorFlow is not working on this system. Please use Tab 1 (ML Classifiers) instead.")
        else:
            with st.spinner("Processing with neural network..."):
                from tensorflow.keras.preprocessing.sequence import pad_sequences
                cleaned_dl = clean_text(article_text_dl)
                seq = dl_tok.texts_to_sequences([cleaned_dl])
                X_dl = pad_sequences(seq, maxlen=256, padding="post")
                
                pred_prob = dl_model.predict(X_dl, verbose=0)[0][0]
                verdict_dl = "FAKE" if pred_prob > 0.5 else "REAL"
                
                # Calculate confidence properly
                if pred_prob > 0.5:
                    confidence_dl = 0.5 + (pred_prob - 0.5)  # Maps 0.5-1.0 to 0.5-1.0
                else:
                    confidence_dl = 0.5 + (0.5 - pred_prob)  # Maps 0.0-0.5 to 1.0-0.5
                
                st.markdown("### 🎯 Neural Network Verdict")
                if verdict_dl == "REAL":
                    st.markdown('<div class="verdict-real">✅ REAL NEWS</div>', 
                                unsafe_allow_html=True)
                else:
                    st.markdown('<div class="verdict-fake">⚠️ FAKE NEWS</div>', 
                                unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Confidence", f"{confidence_dl*100:.2f}%")
                with col2:
                    st.metric("Fake Probability", f"{pred_prob*100:.2f}%")
                
                # Confidence gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=confidence_dl * 100,
                    title={'text': "Confidence Score"},
                    gauge={'axis': {'range': [0, 100]},
                           'bar': {'color': "#00d9ff"},
                           'steps': [
                               {'range': [0, 50], 'color': "#ff006e"},
                               {'range': [50, 75], 'color': "#fb5607"},
                               {'range': [75, 100], 'color': "#06ffa5"}
                           ]}
                ))
                st.plotly_chart(fig, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────
# TAB 3: LLM ENSEMBLE
# ──────────────────────────────────────────────────────────────────────────
with tab3:
    st.header("🌐 Large Language Model Analysis")
    st.markdown("**LLaMA 3.3 70B** (Meta AI) — 70 billion parameters")
    
    article_text_llm = st.text_area("Enter article text:", height=200,
                                     placeholder="Paste news article here...",
                                     key="llm_text")
    
    if st.button("🔍 Analyze with LLaMA", key="llm_btn"):
        if not article_text_llm.strip():
            st.error("Please provide text input.")
        else:
            with st.spinner("Querying LLaMA 3.3 70B... (5-10 seconds)"):
                result = llm_ensemble_predict(article_text_llm)
                
                if result.get("verdict") == "ERROR":
                    st.error(f"Error: {result.get('error', 'Unknown error')}")
                else:
                    st.markdown("### 🎯 LLaMA Verdict")
                    if result["verdict"] == "REAL":
                        st.markdown('<div class="verdict-real">✅ REAL NEWS</div>', 
                                    unsafe_allow_html=True)
                    elif result["verdict"] == "FAKE":
                        st.markdown('<div class="verdict-fake">⚠️ FAKE NEWS</div>', 
                                    unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ UNCERTAIN")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Confidence", f"{result['confidence']*100:.1f}%")
                    with col2:
                        st.metric("Model", "LLaMA 3.3 70B")
                    
                    st.markdown("### 📊 Analysis Scores")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Factual Consistency", 
                                  f"{result.get('factual_consistency_score', 0)*100:.0f}%")
                    with col2:
                        st.metric("Sensationalism", 
                                  f"{result.get('sensationalism_score', 0)*100:.0f}%")
                    with col3:
                        st.metric("Source Credibility", 
                                  f"{result.get('source_credibility_score', 0)*100:.0f}%")
                    with col4:
                        st.metric("Writing Style", 
                                  f"{result.get('writing_style_score', 0)*100:.0f}%")
                    
                    st.markdown("### 🧠 Reasoning")
                    st.info(result.get('reasoning', 'No reasoning provided'))

# ──────────────────────────────────────────────────────────────────────────
# TAB 4: MODEL COMPARISON
# ──────────────────────────────────────────────────────────────────────────
with tab4:
    st.header("📊 Model Performance Comparison")
    
    metrics = load_metrics()
    
    if metrics:
        df_metrics = pd.DataFrame(metrics).T
        df_metrics = df_metrics[["accuracy", "precision", "recall", "f1", "auc_roc"]]
        
        st.dataframe(df_metrics.style.highlight_max(axis=0, color="#06ffa5"), 
                     use_container_width=True)
        
        # Radar chart
        fig = go.Figure()
        for model in df_metrics.index:
            fig.add_trace(go.Scatterpolar(
                r=df_metrics.loc[model].values,
                theta=["Accuracy", "Precision", "Recall", "F1", "AUC-ROC"],
                fill='toself',
                name=model.replace("_", " ").title()
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0.9, 1.0])),
            showlegend=True,
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Bar chart
        fig2 = px.bar(df_metrics.reset_index(), x="index", y="accuracy",
                      title="Model Accuracy Comparison",
                      labels={"index": "Model", "accuracy": "Accuracy"},
                      template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No metrics found. Train models first.")

# ──────────────────────────────────────────────────────────────────────────
# TAB 5: LIVE NEWS
# ──────────────────────────────────────────────────────────────────────────
with tab5:
    st.header("📰 Live News Intelligence Pipeline")
    st.markdown("Real-time scraping from NewsAPI + RSS with Bias Correction")
    
    if st.button("🔄 Refresh Cache"):
        st.rerun()
    
    articles = get_cached_articles(limit=100)
    
    if articles:
        st.success(f"📦 {len(articles)} articles in cache (72h retention)")
        
        for i, (title, content, source, fetched, bias_flags, verdict) in enumerate(articles[:20]):
            with st.expander(f"📄 {title[:80]}..."):
                st.markdown(f"**Source:** {source}")
                st.markdown(f"**Fetched:** {fetched}")
                st.markdown(f"**Bias Flags:** {bias_flags}")
                st.markdown(f"**ML Verdict:** {verdict}")
                st.text_area("Content Preview:", content[:500], height=100, key=f"news_{i}")
    else:
        st.info("No articles in cache. Enable scraper in sidebar.")

# ──────────────────────────────────────────────────────────────────────────
# TAB 6: AGENT SWARM
# ──────────────────────────────────────────────────────────────────────────
with tab6:
    st.header("🕸️ Fact Verification Agent Swarm")
    st.markdown("20 parallel agents | 16 credible + 4 unreliable domains")
    
    article_text_swarm = st.text_area("Enter article/claim to verify:", height=200,
                                       placeholder="Paste article or claim here...",
                                       key="swarm_text")
    
    if st.button("🚀 Launch Agent Swarm", key="swarm_btn"):
        if not article_text_swarm.strip():
            st.error("Please provide text input.")
        else:
            with st.spinner("🕷️ Deploying 20 agents... (20-40 seconds)"):
                result = run_swarm(article_text_swarm)
                
                st.markdown("### 🎯 Swarm Verdict")
                verdict_swarm = result["verdict"]["verdict"]
                
                if "REAL" in verdict_swarm:
                    st.markdown('<div class="verdict-real">✅ ' + verdict_swarm + '</div>', 
                                unsafe_allow_html=True)
                elif "FAKE" in verdict_swarm:
                    st.markdown('<div class="verdict-fake">⚠️ ' + verdict_swarm + '</div>', 
                                unsafe_allow_html=True)
                else:
                    st.warning("⚠️ " + verdict_swarm)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Confidence", f"{result['verdict']['confidence']*100:.1f}%")
                with col2:
                    st.metric("Credible Sources", result['verdict']['credible_sources_found'])
                with col3:
                    st.metric("Execution Time", f"{result['elapsed_seconds']}s")
                
                st.markdown("### 🔍 Reasoning")
                st.info(result["verdict"]["reasoning"])
                
                st.markdown("### 🗝️ Extracted Keywords")
                st.code(", ".join(result["keywords"]))
                
                st.markdown("### 🌐 Agent Evidence")
                for agent in result["agent_results"]:
                    if agent["found"]:
                        with st.expander(f"{'✅' if agent['credible'] else '⚠️'} {agent['domain']} ({agent['site']})"):
                            for ev in agent["evidence"]:
                                st.markdown(f"**{ev['title']}**")
                                st.caption(f"Jaccard: {ev['jaccard']} | {ev['snippet']}")
                                st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #00d9ff; padding: 20px;'>
    <h3>🔍 TruthLens v1.0</h3>
    <p>Multimodal Fake News Detection using Machine Learning and Deep Learning</p>
    <p><b>Team Logic Lords</b> | Heritage Institute of Technology | 2025-2026</p>
    <p>Ankit Dey • Shivam Kumar • Ritam Ghosh • Preetmondeep Ghosh</p>
</div>
""", unsafe_allow_html=True)
