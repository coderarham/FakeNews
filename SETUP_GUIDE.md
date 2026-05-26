# 🚀 TruthLens - Complete Setup & Usage Guide

## 📦 Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## 📊 Step 2: Prepare Dataset

Dataset already present in `ISOT Fake News Dataset/` folder:
- `Fake.csv` - 23,481 fake news articles
- `True.csv` - 21,417 real news articles

## 🔑 Step 3: Setup API Keys

Create `.env` file in project root:

```
NEWSAPI_KEY=your_newsapi_key_here
GROQ_API_KEY=your_groq_key_here
GOOGLE_GENAI_KEY=your_gemini_key_here
```

**Get API Keys:**
- NewsAPI: https://newsapi.org/
- Groq (LLaMA): https://console.groq.com/
- Google Gemini: https://aistudio.google.com/

## 🤖 Step 4: Train Models

### Train ML Classifiers (5-10 minutes)
```bash
python train_ml.py
```
This will train 5 models and save them in `models/` folder:
- Decision Tree
- Gradient Boosting
- Linear SVC
- Logistic Regression
- Random Forest

### Train Deep Learning Model (30-60 minutes)
```bash
python train_dl.py
```
This will train Attention BiLSTM and save in `saved_model/` folder.

**Note:** If TensorFlow gives DLL error on Python 3.12, you need to:
1. Downgrade to Python 3.11, OR
2. Install Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe

### Generate Dataset Audit Report
```bash
python generate_dataset_audit.py
```

## 🎯 Step 5: Run Application

### Start Backend Server
```bash
python backend_api.py
```
Backend will run on: `http://localhost:5000`

### Start Frontend (New Terminal)
```bash
cd frontend
npm run dev
```
Frontend will open at: `http://localhost:5173`

## 📱 Application Features

### Tab 1: ML Classifiers
- Upload text or image (OCR)
- Get predictions from 5 ML models
- Majority vote ensemble result

### Tab 2: Deep Learning
- Attention BiLSTM prediction
- 99.96% accuracy
- Confidence score

### Tab 3: LLM Ensemble
- Multi-LLM analysis (LLaMA, GPT-4o, Gemini)
- Semantic reasoning
- 4-metric evaluation

### Tab 4: Model Comparison
- Performance metrics dashboard
- Radar charts
- Comparative analysis

### Tab 5: Live News Intelligence
- Real-time news scraping
- 3-Layer bias correction
- NewsAPI + RSS feeds

### Tab 6: Agent Swarm
- 20 parallel fact-checking agents
- Web cross-verification
- Explainable results

## 🔧 Tesseract OCR Setup (for image text extraction)

**Windows:**
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR`
3. Add to PATH

**Linux:**
```bash
sudo apt install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

## 📁 Project Structure

```
Fake News/
├── app.py                          # Main Streamlit application
├── preprocess.py                   # Text preprocessing + TF-IDF
├── train_ml.py                     # Train ML classifiers
├── train_dl.py                     # Train Deep Learning model
├── generate_dataset_audit.py       # Dataset analysis
├── news_scraper.py                 # Live news scraping
├── fact_swarm.py                   # Agent swarm verification
├── requirements.txt                # Dependencies
├── .env                            # API keys (create this)
├── README.md                       # Project overview
├── SETUP_GUIDE.md                  # This file
├── Fake.csv                        # Fake news dataset
├── True.csv                        # Real news dataset
├── tfidf_vectorizer.pkl            # TF-IDF vectorizer
├── models/                         # Trained ML models
│   ├── decision_tree.pkl
│   ├── gradient_boosting.pkl
│   ├── linear_svc.pkl
│   ├── logistic_regression.pkl
│   ├── random_forest.pkl
│   └── ml_metrics.pkl
├── saved_model/                    # Trained DL model
│   ├── attention_bilstm/
│   └── tokenizer.pkl
├── ISOT Fake News Dataset/         # Original dataset
│   ├── Fake.csv
│   └── True.csv
└── frontend/                       # React frontend (optional)
```

## 🧪 Testing

```bash
# Test preprocessing
python -c "from preprocess import clean_text; print(clean_text('Test article'))"

# Test ML models
python -c "from preprocess import load_tfidf; vec = load_tfidf(); print('TF-IDF loaded')"

# Test news scraper
python news_scraper.py

# Test fact swarm
python -c "from fact_swarm import run_swarm; print('Swarm ready')"
```

## ⚠️ Common Issues

### Issue 1: TensorFlow DLL Error
**Solution:** Install Visual C++ Redistributable or use Python 3.11

### Issue 2: Tesseract not found
**Solution:** Install Tesseract OCR and add to PATH

### Issue 3: API rate limits
**Solution:** Use free tier limits wisely or upgrade API plans

### Issue 4: Out of memory during training
**Solution:** Reduce batch size in train_dl.py (line 42: BATCH_SIZE = 32)

## 📊 Expected Performance

| Model | Accuracy | Training Time |
|-------|----------|---------------|
| Decision Tree | 99.6% | 2 min |
| Gradient Boosting | 99.5% | 5 min |
| Linear SVC | 99.4% | 3 min |
| Logistic Regression | 98.6% | 1 min |
| Random Forest | 99.5% | 4 min |
| Attention BiLSTM | 99.96% | 30-60 min |

## 👥 Team Logic Lords

- Ankit Dey (2262058)
- Shivam Kumar (2262050)
- Ritam Ghosh (2262060)
- Preetmondeep Ghosh (2262053)

**Supervisor:** Prof. Arpita Talukdar  
**Institution:** Heritage Institute of Technology

---

**Need Help?** Contact the team or supervisor.
