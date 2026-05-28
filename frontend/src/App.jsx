import { useState } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import MLEnsemble from './pages/MLEnsemble'
import AttentionBiLSTM from './pages/AttentionBiLSTM'
import LLMEnsemble from './pages/LLMEnsemble'
import DatasetAudit from './pages/DatasetAudit'
import LiveIntel from './pages/LiveIntel'
import AgentSwarm from './pages/AgentSwarm'

function App() {
  const [activeTab, setActiveTab] = useState(0)
  const [biasCorrection, setBiasCorrection] = useState(true)
  const [inputText, setInputText] = useState('')
  const [presetArticle, setPresetArticle] = useState(null)

  const tabs = [
    { id: 0, name: 'ML Ensemble', icon: '' },
    { id: 1, name: 'Attention BiLSTM', icon: '' },
    { id: 2, name: 'LLM Ensemble', icon: '' },
    { id: 3, name: 'Dataset Audit', icon: '' },
    { id: 4, name: 'Live Intel', icon: '' },
    { id: 5, name: 'Agent Swarm', icon: '' }
  ]

  const renderContent = () => {
    switch(activeTab) {
      case 0: return <MLEnsemble inputText={inputText} biasCorrection={biasCorrection} />
      case 1: return <AttentionBiLSTM inputText={inputText} />
      case 2: return <LLMEnsemble inputText={inputText} />
      case 3: return <DatasetAudit />
      case 4: return <LiveIntel />
      case 5: return <AgentSwarm inputText={inputText} />
      default: return <MLEnsemble inputText={inputText} biasCorrection={biasCorrection} />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Header 
        biasCorrection={biasCorrection} 
        setBiasCorrection={setBiasCorrection}
      />
      
      {/* Phase Toggle Bar */}
      <div className="bg-gradient-to-r from-cyan-900/50 to-purple-900/50 border-b border-cyan-500/30 px-6 py-3">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-6">
            <span className="text-cyan-400 font-semibold">Phase 1: Static Classifiers</span>
            <span className="text-purple-400">|</span>
            <span className="text-purple-400 font-semibold">Phase 2: Live Bias Correction & Agent Swarm</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-gray-300 text-sm">Bias Correction:</span>
            <button
              onClick={() => setBiasCorrection(!biasCorrection)}
              className={`relative w-14 h-7 rounded-full transition-colors ${
                biasCorrection ? 'bg-green-500' : 'bg-gray-600'
              }`}
            >
              <span className={`absolute top-1 left-1 w-5 h-5 bg-white rounded-full transition-transform ${
                biasCorrection ? 'translate-x-7' : ''
              }`} />
            </button>
            <span className={`text-sm font-bold ${
              biasCorrection ? 'text-green-400' : 'text-gray-400'
            }`}>
              {biasCorrection ? 'ON' : 'OFF'}
            </span>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Sidebar */}
        <Sidebar 
          inputText={inputText}
          setInputText={setInputText}
          setPresetArticle={setPresetArticle}
        />

        {/* Main Content */}
        <div className="flex-1">
          {/* Tab Navigation */}
          <div className="bg-slate-800/50 border-b border-cyan-500/30">
            <div className="flex overflow-x-auto">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-6 py-4 font-semibold transition-all whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'bg-cyan-600 text-white border-b-4 border-cyan-400'
                      : 'text-gray-400 hover:text-white hover:bg-slate-700/50'
                  }`}
                >
                  {tab.name}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {renderContent()}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-cyan-500/30 py-4 text-center text-gray-400">
        <p>Built by VerifAI | Techno India University</p>
      </footer>
    </div>
  )
}

export default App
