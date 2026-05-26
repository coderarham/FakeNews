# TruthLens Frontend

React + Vite + Tailwind CSS frontend for TruthLens fake news detection system.

## 🎨 Features

### Global Layout
- **Glowing Header** with TRUTHLENS v2.5 Pro logo and security shield
- **System Status Indicators**: Real-time connection status (System Ready, Gemini API)
- **Phase Toggle Bar**: Switch between Phase 1 (Static) and Phase 2 (Live + Swarm)
- **Bias Correction Toggle**: ON/OFF switch for Reuters dateline removal
- **Sidebar**: Preset articles, OCR uploader, quick stats

### 6 Interactive Tabs

#### Tab 1: ML Ensemble 🤖
- Big verdict banner (FAKE/REAL with crimson/green glow)
- 5 model performance cards with neon probability bars
- Individual predictions + ensemble consensus
- Dynamic bar charts and radar visualization

#### Tab 2: Attention BiLSTM 🧠
- Radial progress gauge (99.96% accuracy)
- Interactive attention heatmap with color-coded suspicious words
- Hyperparameter configuration table
- Real-time neural network confidence display

#### Tab 3: LLM Ensemble 💬
- 3-column comparison (LLaMA, GPT-4o, Gemini)
- Neon-colored cards with reasoning text
- 4 quality metrics: Factual, Sensationalism, Credibility, Style
- Unanimous verdict display

#### Tab 4: Dataset Audit 📊
- 4 KPI counters (44.9K articles, vocabulary size)
- Class distribution bar charts
- Known biases & mitigation strategies
- Architecture feature cards

#### Tab 5: Live Intel 🌐
- Pipeline activity log with real-time status
- Category breakdown pie chart
- Recent scraped articles list
- 72-hour cache monitoring

#### Tab 6: Agent Swarm 🕷️
- 20-agent status matrix with blinking indicators
- Interactive claim-evidence network graph
- Jaccard similarity matching
- Gemini coordinator analysis block

## 🚀 Setup

```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## 🎯 Usage

1. **Start Backend**: `streamlit run app.py` (port 8501)
2. **Start Frontend**: `npm run dev` (port 3000)
3. **Open Browser**: `http://localhost:3000`

## 🎨 Design Features

- Dark theme with gradient backgrounds
- Neon glow effects on cards and buttons
- Animated status indicators (pulse, ping)
- Responsive grid layouts
- Hover effects and transitions
- Custom scrollbars
- Color-coded verdicts (red=fake, green=real)

## 🛠️ Tech Stack

- **React 18**: Component-based UI
- **Vite**: Fast build tool
- **Tailwind CSS**: Utility-first styling
- **Axios**: API communication
- **SVG Graphics**: Custom charts and graphs

## 📱 Responsive Design

- Mobile: Single column layout
- Tablet: 2-column grids
- Desktop: Full multi-column experience

## 🎭 Mock Data

Currently uses mock data for demonstration. To connect to real backend:

1. Update API endpoints in each page component
2. Replace `analyzeMock()` with actual `axios.post()` calls
3. Configure CORS in backend if needed

## 🎨 Color Scheme

- **Primary**: Cyan (#06b6d4)
- **Secondary**: Purple (#a855f7)
- **Success**: Green (#10b981)
- **Danger**: Red (#ef4444)
- **Warning**: Yellow (#f59e0b)
- **Background**: Slate (#0f172a, #1e293b)

---

**Built with ❤️ by Team Logic Lords**
