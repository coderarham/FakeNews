import { useState } from 'react'

function LLMEnsemble({ inputText }) {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)

  const analyzeLLM = async () => {
    if (!inputText || inputText.trim().length === 0) {
      alert('Please enter some text to analyze')
      return
    }

    setLoading(true)
    try {
      const response = await fetch('http://localhost:5000/api/predict/llm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText })
      })

      if (!response.ok) {
        throw new Error('API request failed')
      }

      const data = await response.json()
      
      // Transform backend response to match frontend format
      setResults({
        llama: {
          verdict: data.verdict || 'UNCERTAIN',
          confidence: data.confidence || 0.5,
          reasoning: data.reasoning || 'No reasoning provided',
          metrics: {
            factual: data.metrics?.factual || 0.5,
            sensationalism: data.metrics?.sensationalism || 0.5,
            credibility: data.metrics?.credibility || 0.5,
            style: data.metrics?.style || 0.5
          }
        }
      })
    } catch (error) {
      console.error('LLM API Error:', error)
      alert('Failed to analyze with LLM. Make sure backend is running on port 5000.')
    } finally {
      setLoading(false)
    }
  }

  const MetricBar = ({ label, value, color }) => (
    <div className="mb-3">
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-400">{label}</span>
        <span className="text-white font-semibold">{(value * 100).toFixed(0)}%</span>
      </div>
      <div className="w-full bg-slate-700 rounded-full h-2">
        <div
          className={`h-full ${color} rounded-full transition-all duration-1000`}
          style={{ width: `${value * 100}%` }}
        />
      </div>
    </div>
  )

  return (
    <div className="max-w-7xl mx-auto">
      {/* Analyze Button */}
      <div className="mb-6">
        <button
          onClick={analyzeLLM}
          disabled={loading || !inputText}
          className="w-full bg-gradient-to-r from-green-600 to-cyan-600 hover:from-green-700 hover:to-cyan-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold py-4 px-6 rounded-lg transition-all shadow-lg shadow-green-500/50 text-lg"
        >
          {loading ? '🦙 Querying LLaMA 3.3 70B...' : '🦙 Analyze with LLaMA 3.3 70B'}
        </button>
      </div>

      {results && (
        <>
          {/* Single LLaMA Result */}
          <div className="mb-6 bg-gradient-to-r from-slate-900/50 to-slate-800/50 border-2 border-green-500 rounded-xl p-6">
            <div className="text-center mb-4">
              <h2 className="text-3xl font-black text-green-400 mb-2">
                {results.llama.verdict === 'FAKE' ? '⚠️ FAKE NEWS' : results.llama.verdict === 'REAL' ? '✅ REAL NEWS' : '❓ UNCERTAIN'}
              </h2>
              <p className="text-gray-300 text-lg">LLaMA 3.3 70B Analysis - Confidence: {(results.llama.confidence * 100).toFixed(1)}%</p>
            </div>
          </div>

          {/* Single LLaMA Card */}
          <div className="grid grid-cols-1 gap-6 mb-6">
            <div className="bg-slate-800/50 border-2 border-green-500/50 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-700 rounded-lg flex items-center justify-center text-2xl">
                  🦙
                </div>
                <div>
                  <h3 className="text-green-400 font-bold text-lg">LLaMA 3.3 70B</h3>
                  <p className="text-xs text-gray-400">via Groq API (Meta AI)</p>
                </div>
              </div>

              <div className={`mb-4 py-3 px-4 rounded-lg text-center font-black text-xl ${
                results.llama.verdict === 'FAKE' 
                  ? 'bg-red-500/20 text-red-400' 
                  : results.llama.verdict === 'REAL'
                  ? 'bg-green-500/20 text-green-400'
                  : 'bg-yellow-500/20 text-yellow-400'
              }`}>
                {results.llama.verdict}
              </div>

              <div className="mb-4">
                <div className="text-sm text-gray-400 mb-2">Confidence</div>
                <div className="text-3xl font-black text-green-400">{(results.llama.confidence * 100).toFixed(1)}%</div>
              </div>

              <div className="mb-4 p-4 bg-slate-900/50 rounded-lg">
                <div className="text-xs text-gray-400 mb-2">Reasoning:</div>
                <p className="text-sm text-gray-300 leading-relaxed">{results.llama.reasoning}</p>
              </div>

              <div className="space-y-2">
                <MetricBar label="Factual Consistency" value={results.llama.metrics.factual} color="bg-blue-500" />
                <MetricBar label="Sensationalism" value={results.llama.metrics.sensationalism} color="bg-red-500" />
                <MetricBar label="Source Credibility" value={results.llama.metrics.credibility} color="bg-green-500" />
                <MetricBar label="Journalistic Style" value={results.llama.metrics.style} color="bg-purple-500" />
              </div>
            </div>
          </div>
        </>
      )}

      {/* Empty State */}
      {!results && !loading && (
        <div className="text-center py-20">
          <div className="text-6xl mb-4">🦙</div>
          <h3 className="text-2xl font-bold text-gray-400 mb-2">LLaMA 3.3 70B Ready</h3>
          <p className="text-gray-500">70 billion parameter language model by Meta AI</p>
          <p className="text-gray-600 text-sm mt-2">Powered by Groq API</p>
        </div>
      )}
    </div>
  )
}

export default LLMEnsemble
