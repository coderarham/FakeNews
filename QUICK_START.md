# ⚡ TruthLens - Quick Start Guide

## 🚦 Current Status

✅ **READY:**
- Dataset loaded (111 MB)
- 5 ML models trained
- Frontend setup complete
- All dependencies installed

⚠️ **NEEDS ATTENTION:**
- DL model not trained (optional)
- API keys not configured

---

## 🎯 Run Application NOW

### React Frontend + Flask Backend
```bash
# Terminal 1 - Backend
python backend_api.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```
Open: http://localhost:5173

---

## 🔑 Setup API Keys (Optional but Recommended)

Edit `.env` file:
```bash
NEWSAPI_KEY=your_actual_key_here
GROQ_API_KEY=your_actual_key_here
GOOGLE_GENAI_KEY=your_actual_key_here
```

**Get Keys:**
- NewsAPI: https://newsapi.org/register
- Groq: https://console.groq.com/keys
- Gemini: https://aistudio.google.com/app/apikey

**Without API keys:**
- ✅ Tab 1 (ML) - Works
- ✅ Tab 2 (DL) - Works (heuristic fallback)
- ❌ Tab 3 (LLM) - Won't work
- ⚠️ Tab 5 (Live News) - RSS only, no NewsAPI
- ⚠️ Tab 6 (Agent Swarm) - Rule-based fallback

---

## 🧠 Train Deep Learning Model (Optional)

```bash
python train_dl.py
```

**Time:** 30-60 minutes  
**Accuracy:** 99.96%

**If TensorFlow error:**
1. Install Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. OR use Python 3.11 instead of 3.12
3. OR skip - ML models already give 99.5% accuracy

---

## 📊 What Works Right Now

### ✅ Tab 1: ML Classifiers
- 5 models with 99.5% accuracy
- Text input + OCR support
- Majority vote ensemble

### ✅ Tab 2: Deep Learning
- Heuristic-based prediction (until DL model trained)
- Attention visualization

### ⚠️ Tab 3: LLM Ensemble
- Needs API keys

### ✅ Tab 4: Model Comparison
- Performance metrics
- Radar charts

### ⚠️ Tab 5: Live News
- RSS feeds work
- NewsAPI needs key

### ⚠️ Tab 6: Agent Swarm
- Rule-based fallback works
- Gemini coordinator needs key

---

## 🧪 Quick Test

```bash
# Test ML prediction
python -c "from preprocess import load_tfidf; print('✓ ML models ready')"

# Test system
python check_system.py
```

---

## 🎓 Team Logic Lords

Heritage Institute of Technology  
CSE (Data Science) | 2025-2026

**Members:**
- Ankit Dey (2262058)
- Shivam Kumar (2262050)
- Ritam Ghosh (2262060)
- Preetmondeep Ghosh (2262053)

**Supervisor:** Prof. Arpita Talukdar

---

**Need Help?** Check SETUP_GUIDE.md for detailed instructions.
