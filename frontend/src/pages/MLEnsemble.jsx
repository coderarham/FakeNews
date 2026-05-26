import { useState, useEffect } from 'react'
import axios from 'axios'

function MLEnsemble({ inputText, biasCorrection }) {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)

  const models = [
    { name: 'Decision Tree', key: 'decision_tree', color: 'cyan' },
    { name: 'Gradient Boosting', key: 'gradient_boosting', color: 'purple' },
    { name: 'Linear SVC', key: 'linear_svc', color: 'pink' },
    { name: 'Logistic Regression', key: 'logistic_regression', color: 'blue' },
    { name: 'Random Forest', key: 'random_forest', color: 'green' }
  ]

  const analyzeWithBackend = async () => {
    if (!inputText || !inputText.trim()) {
      alert('Please enter some text to analyze')
      return
    }

    setLoading(true)
    try {
      const response = await axios.post('http://localhost:5000/api/predict/ml', {
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

  return (
    <div className="max-w-7xl mx-auto">
      {/* Analyze Button */}
      <div className="mb-6">
        <button
          onClick={analyzeWithBackend}
          disabled={loading || !inputText}
          className="w-full bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-700 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold py-4 px-6 rounded-lg transition-all shadow-lg shadow-cyan-500/50 text-lg"
        >
          {loading ? '🔄 Analyzing...' : '🚀 Analyze with ML Ensemble'}
        </button>
      </div>

      {/* Verdict Banner */}
      {results && (
        <div className={`mb-8 p-6 rounded-xl border-4 animate-pulse shadow-2xl ${
          results.verdict === 'FAKE'
            ? 'bg-red-900/30 border-red-500 shadow-red-500/50'
            : 'bg-green-900/30 border-green-500 shadow-green-500/50'
        }`}>
          <div className="text-center">
            <h2 className={`text-5xl font-black mb-2 ${
              results.verdict === 'FAKE' ? 'text-red-400' : 'text-green-400'
            }`}>
              {results.verdict === 'FAKE' ? '⚠️ FAKE NEWS' : '✅ REAL NEWS'}
            </h2>
            <p className="text-gray-300 text-xl">
              Ensemble Confidence: <span className="font-bold text-white">{(results.confidence * 100).toFixed(1)}%</span>
            </p>
            <p className="text-cyan-400 mt-2">{results.consensus}</p>
          </div>
        </div>
      )}

      {/* Model Cards Grid */}
      {results && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {models.map(model => {
            const result = results.models[model.key]
            const isFake = result.prediction === 'FAKE'
            
            return (
              <div
                key={model.key}
                className={`bg-slate-800/50 border-2 rounded-xl p-6 transition-all hover:scale-105 ${
                  isFake ? 'border-red-500/50' : 'border-green-500/50'
                }`}
              >
                <h3 className={`text-lg font-bold mb-4 text-${model.color}-400`}>
                  {model.name}
                </h3>
                
                {/* Probability Bar */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-400">Confidence</span>
                    <span className="text-white font-bold">{(result.probability * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
                    <div
                      className={`h-full transition-all duration-1000 ${
                        isFake ? 'bg-gradient-to-r from-red-600 to-red-400' : 'bg-gradient-to-r from-green-600 to-green-400'
                      }`}
                      style={{ width: `${result.probability * 100}%` }}
                    />
                  </div>
                </div>

                {/* Verdict */}
                <div className={`text-center py-3 rounded-lg font-black text-xl ${
                  isFake ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'
                }`}>
                  {result.prediction}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Ensemble Statistics */}
      {results && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Bar Chart */}
          <div className="bg-slate-800/50 border border-cyan-500/30 rounded-xl p-6">
            <h3 className="text-cyan-400 font-bold text-lg mb-4">📊 Model Confidence Distribution</h3>
            <div className="space-y-3">
              {models.map(model => {
                const result = results.models[model.key]
                return (
                  <div key={model.key}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-400">{model.name}</span>
                      <span className="text-white">{(result.probability * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-slate-700 rounded-full h-2">
                      <div
                        className={`h-full bg-${model.color}-500 rounded-full`}
                        style={{ width: `${result.probability * 100}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Consensus Summary */}
          <div className="bg-slate-800/50 border border-cyan-500/30 rounded-xl p-6">
            <h3 className="text-cyan-400 font-bold text-lg mb-4">🎯 Ensemble Summary</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Final Verdict:</span>
                <span className={`font-black text-xl ${
                  results.verdict === 'FAKE' ? 'text-red-400' : 'text-green-400'
                }`}>
                  {results.verdict}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Consensus:</span>
                <span className="text-white font-bold">{results.consensus}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Avg Confidence:</span>
                <span className="text-white font-bold">{(results.confidence * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Bias Correction:</span>
                <span className={`font-bold ${biasCorrection ? 'text-green-400' : 'text-gray-400'}`}>
                  {biasCorrection ? 'ACTIVE' : 'INACTIVE'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!results && !loading && (
        <div className="text-center py-20">
          <div className="text-6xl mb-4">🤖</div>
          <h3 className="text-2xl font-bold text-gray-400 mb-2">Ready to Analyze</h3>
          <p className="text-gray-500">Enter text in the sidebar and click analyze</p>
        </div>
      )}
    </div>
  )
}

export default MLEnsemble
