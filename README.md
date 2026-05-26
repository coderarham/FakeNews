# 🔍 TruthLens — Multimodal Fake News Detection System

**AI-Powered Fake News Detection using Machine Learning, Deep Learning, and Multi-Agent Systems**

---

## 📋 Project Overview

TruthLens is a comprehensive fake news detection system developed by **Team Logic Lords** at Heritage Institute of Technology. The system implements a dual-phase approach:

### **Phase 1: Static Detection Engine**
- 5 Traditional ML Classifiers (Decision Tree, Gradient Boosting, Linear SVC, Logistic Regression, Random Forest)
- Attention BiLSTM Deep Learning Model (35M parameters, 99.96% accuracy)
- LLM Ensemble (LLaMA 3.3 70B, GPT-4o, Gemini 2.5 Flash)

### **Phase 2: Live Intelligence & Agent Swarm**
- 3-Layer Bias Correction Engine
- Live News Scraper (NewsAPI + RSS feeds)
- 20-Agent Fact Verification Swarm (parallel web cross-verification)

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/coderarham/FakeNews.git
cd FakeNews
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
cd frontend
npm install
cd ..
```

### 3. Download Pre-trained Models

**Option A: Download from Google Drive (Recommended)**

Download and extract these files to project root:

1. **ML Models (67 MB)** - [Download Link](https://drive.google.com/file/d/16E9Oh1s0pGyPxdqFRvNRJbSKrOXE2cb1/view?usp=sharing)
   - Extract to `models/` folder
   - Contains: 5 ML classifiers + metrics

2. **BiLSTM Model (32 MB)** - [Download Link](https://drive.google.com/file/d/1r_hzw1MrU7gbkMrHE3NGCu6yyCKMczSL/view?usp=sharing)
   - Extract to `saved_model/` folder
   - Contains: attention_bilstm_model.keras + tokenizer.pkl

3. **TF-IDF Vectorizer (5 MB)** - [Download Link](https://drive.google.com/file/d/1TCyNMwwbw3dUT6JcwHdTJu1bDR0sj30f/view?usp=sharing)
   - Extract to project root
   - File: tfidf_vectorizer.pkl

**Option B: Train Models Yourself**

Download `Fake.csv` and `True.csv` from [ISOT Fake News Dataset](https://www.uvic.ca/engineering/ece/isot/datasets/fake-news/index.php) and place them in the project root.

```bash
# Train ML classifiers (5-10 minutes)
python train_ml.py

# Train Deep Learning model (30-60 minutes)
python train_dl.py
```

### 4. Set API Keys

Create a `.env` file:

```bash
cp .env.example .env
```

Add your API keys:

```bash
NEWSAPI_KEY=your_newsapi_key
GROQ_API_KEY=your_groq_key
GOOGLE_GENAI_KEY=your_gemini_key
```

### 5. Run Application

```bash
# Terminal 1 - Start Backend
python backend_api.py

# Terminal 2 - Start Frontend
cd frontend
npm run dev
```

Open browser at:
- **Frontend:** `http://localhost:3000`
- **Backend API:** `http://localhost:5000`

---

## 📁 Project Structure

```
Fake News/
├── app.py                          # Main Streamlit UI (6 tabs)
├── preprocess.py                   # Text preprocessing + TF-IDF
├── train_ml.py                     # Train 5 ML classifiers
├── train_dl.py                     # Train Attention BiLSTM
├── generate_dataset_audit.py       # Dataset bias analysis
├── news_scraper.py                 # Live news scraping + bias correction
├── fact_swarm.py                   # 20-agent fact verification swarm
├── requirements.txt                # Python dependencies
├── Fake.csv                        # ISOT fake news dataset
├── True.csv                        # ISOT real news dataset
├── models/                         # Saved ML models
│   ├── decision_tree.pkl
│   ├── gradient_boosting.pkl
│   ├── linear_svc.pkl
│   ├── logistic_regression.pkl
│   ├── random_forest.pkl
│   ├── ml_metrics.pkl
│   └── audit_report.pkl
├── saved_model/                    # Saved DL model
│   ├── attention_bilstm/
│   └── tokenizer.pkl
├── tfidf_vectorizer.pkl            # Fitted TF-IDF vectorizer
└── news_cache.db                   # SQLite cache for live news
```

---

## 🎯 Features

### Tab 1: ML Classifiers
- 5 traditional ML models with majority vote ensemble
- Text input or OCR from images
- Individual model predictions + ensemble verdict

### Tab 2: Deep Learning
- Attention BiLSTM with 35M parameters
- 99.96% test accuracy
- Confidence score visualization

### Tab 3: LLM Ensemble
- Multi-LLM reasoning (LLaMA, GPT-4o, Gemini)
- Structured semantic analysis
- 4-metric evaluation (factual consistency, sensationalism, source credibility, writing style)

### Tab 4: Model Comparison
- Performance metrics dashboard
- Radar charts and bar graphs
- Comparative analysis

### Tab 5: Live News Intelligence
- Real-time scraping from NewsAPI + RSS
- 3-Layer Bias Correction Engine
- 72-hour cache with SQLite

### Tab 6: Agent Swarm
- 20 parallel agents (16 credible + 4 unreliable domains)
- Jaccard similarity matching
- Gemini-powered coordinator
- Explainable fact graph

---

## 📊 Performance Metrics

| Model | Accuracy | Precision | Recall | F1-Score | AUC-ROC |
|-------|----------|-----------|--------|----------|---------|
| Decision Tree | 99.6% | 0.996 | 0.996 | 0.996 | 0.996 |
| Gradient Boosting | 99.5% | 0.995 | 0.995 | 0.995 | 0.998 |
| Linear SVC | 99.4% | 0.994 | 0.994 | 0.994 | 0.997 |
| Logistic Regression | 98.6% | 0.986 | 0.986 | 0.986 | 0.999 |
| Random Forest | 99.5% | 0.995 | 0.995 | 0.995 | 0.999 |
| **Attention BiLSTM** | **99.96%** | **0.9997** | **0.9995** | **0.9996** | **0.9999** |

---

## 🔧 Configuration

### Tesseract OCR Setup

**Windows:**
1. Download from https://github.com/UB-Mannheim/tesseract/wiki
2. Install to `C:\Program Files\Tesseract-OCR`
3. Add to PATH or set in code:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Linux/Mac:**
```bash
sudo apt install tesseract-ocr  # Ubuntu/Debian
brew install tesseract          # macOS
```

### API Keys

- **NewsAPI**: Get free key at https://newsapi.org/
- **Groq (LLaMA)**: Get key at https://console.groq.com/
- **Google GenAI (Gemini)**: Get key at https://aistudio.google.com/

---

## 🧪 Testing

```bash
# Test preprocessing
python -c "from preprocess import clean_text; print(clean_text('Test article'))"

# Test ML prediction
python -c "from preprocess import load_tfidf; vec = load_tfidf(); print(vec)"

# Test news scraper
python news_scraper.py

# Test agent swarm
python -c "from fact_swarm import run_swarm; print(run_swarm('Test claim'))"
```

---

## 📚 Dataset Information

**ISOT Fake News Dataset**
- Total Articles: 44,898
- Fake News: 23,481
- Real News: 21,417
- Date Range: 2015-2017
- Topics: US Politics, World News, Government

**Known Biases (Addressed by Phase 2):**
- Reuters dateline bias (78.3% of real news)
- Class imbalance ratio: 1.096
- Near-duplicates detected and handled

---

## 👥 Team Logic Lords

- **Ankit Dey** (2262058)
- **Shivam Kumar** (2262050)
- **Ritam Ghosh** (2262060)
- **Preetmondeep Ghosh** (2262053)

**Supervisor:** Prof. Arpita Talukdar  
**Institution:** Heritage Institute of Technology  
**Department:** CSE (Data Science)  
**Academic Year:** 2025-2026

---

## 📄 License

This project is developed for academic purposes as part of the B.Tech final year project at Heritage Institute of Technology.

---

## 🙏 Acknowledgements

- Prof. (Dr.) Basab Chaudhuri, Principal, HIT
- Prof. (Dr.) Subhajit Datta, HOD, CSE (Data Science)
- Prof. (Dr.) Nilina Bera, Departmental Coordinator
- Prof. Arpita Talukdar, Project Mentor

---

## 📞 Support

For issues or questions, please contact the team through the project repository or reach out to the supervisor.

---

**Built with ❤️ by Team Logic Lords**
