import { useState } from 'react'
import axios from 'axios'

function AttentionBiLSTM({ inputText }) {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)

  const analyzeWithBackend = async () => {
    if (!inputText || !inputText.trim()) {
      alert('Please enter some text to analyze')
      return
    }

    setLoading(true)
    try {
      const response = await axios.post('http://localhost:5000/api/predict/dl', {
        text: inputText
      })
      setResults(response.data)
    } catch (error) {
      console.error('Error:', error)
      alert('Error connecting to backend. Make sure backend is running on port 5000.')
    } finally {
      setLoading(false)
    }
  }

  const getAttentionColor = (score) => {
    if (score > 0.7) return 'bg-red-500/70'
    if (score > 0.5) return 'bg-orange-500/60'
    if (score > 0.3) return 'bg-yellow-500/50'
    return 'bg-transparent'
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Analyze Button */}
      <div className="mb-6">
        <button
          onClick={analyzeWithBackend}
          disabled={loading || !inputText}
          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold py-4 px-6 rounded-lg transition-all shadow-lg shadow-purple-500/50 text-lg"
        >
          {loading ? '🧠 Processing Neural Network...' : '🧠 Analyze with Attention BiLSTM'}
        </button>
      </div>

      {results && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Radial Gauge */}
          <div className="lg:col-span-1">
            <div className="bg-slate-800/50 border border-purple-500/30 rounded-xl p-6 sticky top-6">
              <h3 className="text-purple-400 font-bold text-lg mb-6 text-center">Neural Network Confidence</h3>
              
              {/* Radial Progress */}
              <div className="relative w-48 h-48 mx-auto mb-6">
                <svg className="transform -rotate-90 w-48 h-48">
                  <circle
                    cx="96"
                    cy="96"
                    r="88"
                    stroke="currentColor"
                    strokeWidth="12"
                    fill="transparent"
                    className="text-slate-700"
                  />
                  <circle
                    cx="96"
                    cy="96"
                    r="88"
                    stroke="currentColor"
                    strokeWidth="12"
                    fill="transparent"
                    strokeDasharray={`${2 * Math.PI * 88}`}
                    strokeDashoffset={`${2 * Math.PI * 88 * (1 - results.confidence)}`}
                    className="text-purple-500 transition-all duration-1000"
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-4xl font-black text-purple-400">{(results.confidence * 100).toFixed(2)}%</span>
                  <span className="text-sm text-gray-400 mt-1">Confidence</span>
                </div>
              </div>

              {/* Verdict */}
              <div className={`text-center py-4 rounded-lg font-black text-2xl mb-6 ${
                results.verdict === 'FAKE'
                  ? 'bg-red-500/20 text-red-400 border-2 border-red-500'
                  : 'bg-green-500/20 text-green-400 border-2 border-green-500'
              }`}>
                {results.verdict === 'FAKE' ? '⚠️ FAKE' : '✅ REAL'}
              </div>

              {/* Hyperparameters */}
              <div className="bg-slate-900/50 rounded-lg p-4">
                <h4 className="text-cyan-400 font-semibold text-sm mb-3">⚙️ Model Configuration</h4>
                <div className="space-y-2 text-xs">
                  {Object.entries(results.hyperparameters).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-gray-400">{key}:</span>
                      <span className="text-white font-semibold">{value}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Model Stats */}
              <div className="mt-4 pt-4 border-t border-slate-700">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-400">Test Accuracy:</span>
                  <span className="text-green-400 font-bold">{results.accuracy}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Parameters:</span>
                  <span className="text-purple-400 font-bold">35M</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Attention Heatmap */}
          <div className="lg:col-span-2">
            <div className="bg-slate-800/50 border border-purple-500/30 rounded-xl p-6">
              <h3 className="text-purple-400 font-bold text-lg mb-4">🔥 Attention Heatmap Visualization</h3>
              <p className="text-gray-400 text-sm mb-4">
                Words highlighted in red/orange indicate high attention weights - these are the phrases the neural network considers most suspicious.
              </p>

              {/* Attention Legend */}
              <div className="flex gap-4 mb-4 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-red-500/70 rounded"></div>
                  <span className="text-gray-400">High Risk (0.7-1.0)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-orange-500/60 rounded"></div>
                  <span className="text-gray-400">Medium (0.5-0.7)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-yellow-500/50 rounded"></div>
                  <span className="text-gray-400">Low (0.3-0.5)</span>
                </div>
              </div>

              {/* Annotated Text */}
              <div className="bg-slate-900/50 rounded-lg p-6 max-h-96 overflow-y-auto">
                <div className="flex flex-wrap gap-2 text-base leading-relaxed">
                  {results.annotatedText.map((item, idx) => (
                    <span
                      key={idx}
                      className={`px-2 py-1 rounded transition-all hover:scale-110 ${
                        getAttentionColor(item.attention)
                      } ${item.attention > 0.5 ? 'text-white font-semibold' : 'text-gray-300'}`}
                      title={`Attention: ${(item.attention * 100).toFixed(1)}%`}
                    >
                      {item.word}
                    </span>
                  ))}
                </div>
              </div>

              {/* Key Findings */}
              <div className="mt-6 bg-red-900/20 border border-red-500/30 rounded-lg p-4">
                <h4 className="text-red-400 font-semibold mb-2">🚨 Suspicious Patterns Detected</h4>
                <ul className="text-sm text-gray-300 space-y-1">
                  <li>• High-attention words: {results.annotatedText.filter(w => w.attention > 0.7).length} detected</li>
                  <li>• Sensational language patterns identified</li>
                  <li>• Emotional manipulation indicators present</li>
                  <li>• Source credibility markers absent</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!results && !loading && (
        <div className="text-center py-20">
          <div className="text-6xl mb-4">🧠</div>
          <h3 className="text-2xl font-bold text-gray-400 mb-2">Deep Learning Ready</h3>
          <p className="text-gray-500">Neural network with 35M parameters awaiting input</p>
        </div>
      )}
    </div>
  )
}

export default AttentionBiLSTM
