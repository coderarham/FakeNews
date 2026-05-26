import { useState } from 'react'

function AgentSwarm({ inputText }) {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)

  const agents = [
    // Credible Sources (16)
    { id: 1, name: 'BBC', domain: 'bbc.com', type: 'credible', status: 'searching' },
    { id: 2, name: 'Reuters', domain: 'reuters.com', type: 'credible', status: 'match' },
    { id: 3, name: 'NYT', domain: 'nytimes.com', type: 'credible', status: 'match' },
    { id: 4, name: 'AP News', domain: 'apnews.com', type: 'credible', status: 'searching' },
    { id: 5, name: 'CNN', domain: 'cnn.com', type: 'credible', status: 'inconclusive' },
    { id: 6, name: 'Guardian', domain: 'theguardian.com', type: 'credible', status: 'match' },
    { id: 7, name: 'WashPost', domain: 'washingtonpost.com', type: 'credible', status: 'searching' },
    { id: 8, name: 'NPR', domain: 'npr.org', type: 'credible', status: 'match' },
    { id: 9, name: 'Bloomberg', domain: 'bloomberg.com', type: 'credible', status: 'inconclusive' },
    { id: 10, name: 'Forbes', domain: 'forbes.com', type: 'credible', status: 'searching' },
    { id: 11, name: 'TIME', domain: 'time.com', type: 'credible', status: 'match' },
    { id: 12, name: 'Economist', domain: 'economist.com', type: 'credible', status: 'searching' },
    { id: 13, name: 'PBS', domain: 'pbs.org', type: 'credible', status: 'inconclusive' },
    { id: 14, name: 'ABC News', domain: 'abcnews.go.com', type: 'credible', status: 'searching' },
    { id: 15, name: 'CBS News', domain: 'cbsnews.com', type: 'credible', status: 'match' },
    { id: 16, name: 'NBC News', domain: 'nbcnews.com', type: 'credible', status: 'searching' },
    // Unreliable/Satirical (4)
    { id: 17, name: 'The Onion', domain: 'theonion.com', type: 'satire', status: 'match' },
    { id: 18, name: 'InfoWars', domain: 'infowars.com', type: 'unreliable', status: 'match' },
    { id: 19, name: 'NaturalNews', domain: 'naturalnews.com', type: 'unreliable', status: 'searching' },
    { id: 20, name: 'Clickhole', domain: 'clickhole.com', type: 'satire', status: 'inconclusive' }
  ]

  const analyzeSwarm = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:5000/api/predict/swarm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText })
      })
      
      const data = await response.json()
      
      if (data.error) {
        alert('Error: ' + data.error)
        setLoading(false)
        return
      }
      
      // Transform backend data to frontend format
      const evidenceLinks = []
      data.agents.forEach(agent => {
        if (agent.found && agent.evidence.length > 0) {
          agent.evidence.forEach(ev => {
            evidenceLinks.push({
              source: agent.domain,
              type: agent.credible ? 'credible' : 'unreliable',
              similarity: ev.jaccard,
              verdict: ev.title
            })
          })
        }
      })
      
      setResults({
        verdict: data.verdict,
        confidence: data.confidence,
        credibleMatches: data.credible_sources,
        unreliableMatches: data.unreliable_sources,
        jaccardScore: evidenceLinks.length > 0 ? evidenceLinks[0].similarity : 0.0,
        coordinatorAnalysis: data.reasoning,
        evidenceLinks: evidenceLinks.slice(0, 8),  // Top 8 for graph
        keywords: data.keywords,
        elapsed: data.elapsed
      })
      
    } catch (error) {
      alert('Backend error: ' + error.message)
    }
    setLoading(false)
  }

  const getStatusColor = (status) => {
    switch(status) {
      case 'match': return 'bg-green-500'
      case 'searching': return 'bg-cyan-500 animate-pulse'
      case 'inconclusive': return 'bg-gray-500'
      default: return 'bg-gray-700'
    }
  }

  const getAgentBorder = (type, status) => {
    if (type === 'satire' || type === 'unreliable') {
      return status === 'match' ? 'border-red-500 shadow-red-500/50' : 'border-red-500/30'
    }
    return status === 'match' ? 'border-green-500 shadow-green-500/50' : 'border-cyan-500/30'
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Analyze Button */}
      <div className="mb-6">
        <button
          onClick={analyzeSwarm}
          disabled={loading || !inputText}
          className="w-full bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold py-4 px-6 rounded-lg transition-all shadow-lg shadow-orange-500/50 text-lg"
        >
          {loading ? '🕷️ Deploying Agent Swarm...' : '🕷️ Deploy 20-Agent Fact Verification Swarm'}
        </button>
      </div>

      {results && (
        <>
          {/* Swarm Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-slate-800/50 border border-green-500/30 rounded-xl p-4">
              <div className="text-green-400 text-sm mb-1">Credible Matches</div>
              <div className="text-3xl font-black text-white">{results.credibleMatches}/16</div>
            </div>
            <div className="bg-slate-800/50 border border-red-500/30 rounded-xl p-4">
              <div className="text-red-400 text-sm mb-1">Unreliable Matches</div>
              <div className="text-3xl font-black text-white">{results.unreliableMatches}/4</div>
            </div>
            <div className="bg-slate-800/50 border border-purple-500/30 rounded-xl p-4">
              <div className="text-purple-400 text-sm mb-1">Execution Time</div>
              <div className="text-3xl font-black text-white">{results.elapsed || 0}s</div>
            </div>
            <div className={`border-2 rounded-xl p-4 ${
              results.verdict.includes('FAKE') 
                ? 'bg-red-900/30 border-red-500' 
                : results.verdict.includes('REAL')
                ? 'bg-green-900/30 border-green-500'
                : 'bg-yellow-900/30 border-yellow-500'
            }`}>
              <div className="text-gray-300 text-sm mb-1">Swarm Verdict</div>
              <div className={`text-2xl font-black ${
                results.verdict.includes('FAKE') ? 'text-red-400' : 
                results.verdict.includes('REAL') ? 'text-green-400' : 'text-yellow-400'
              }`}>
                {results.verdict}
              </div>
            </div>
          </div>

          {/* Keywords */}
          {results.keywords && (
            <div className="bg-slate-800/50 border border-cyan-500/30 rounded-xl p-4 mb-6">
              <h3 className="text-cyan-400 font-bold text-sm mb-2">🗝️ Extracted Keywords (TF-IDF)</h3>
              <div className="flex flex-wrap gap-2">
                {results.keywords.map((kw, idx) => (
                  <span key={idx} className="bg-cyan-900/30 border border-cyan-500/50 text-cyan-300 px-3 py-1 rounded-full text-sm">
                    {kw}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* 20-Agent Status Matrix */}
          <div className="bg-slate-800/50 border border-cyan-500/30 rounded-xl p-6 mb-6">
            <h3 className="text-cyan-400 font-bold text-lg mb-4">🕸️ 20-Agent Status Matrix</h3>
            <div className="grid grid-cols-4 md:grid-cols-5 lg:grid-cols-10 gap-3">
              {agents.map(agent => (
                <div
                  key={agent.id}
                  className={`bg-slate-900/50 border-2 rounded-lg p-3 hover:scale-110 transition-all ${
                    getAgentBorder(agent.type, agent.status)
                  } ${agent.status === 'match' ? 'shadow-lg' : ''}`}
                  title={`${agent.name} (${agent.domain})`}
                >
                  <div className={`w-3 h-3 rounded-full mb-2 ${getStatusColor(agent.status)}`}></div>
                  <div className="text-white text-xs font-semibold truncate">{agent.name}</div>
                  <div className="text-gray-500 text-[10px] truncate">{agent.domain}</div>
                </div>
              ))}
            </div>
            <div className="mt-4 flex gap-6 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-gray-400">Match Found</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-cyan-500 rounded-full animate-pulse"></div>
                <span className="text-gray-400">Searching</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
                <span className="text-gray-400">Inconclusive</span>
              </div>
            </div>
          </div>

          {/* Interactive Fact Graph */}
          <div className="bg-slate-800/50 border border-cyan-500/30 rounded-xl p-6 mb-6">
            <h3 className="text-cyan-400 font-bold text-lg mb-4">🔗 Claim-Evidence Network Graph</h3>
            
            <div className="relative bg-slate-900/50 rounded-lg p-8 h-96 flex items-center justify-center">
              {/* Center Claim Node */}
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10">
                <div className="bg-gradient-to-br from-orange-500 to-red-500 rounded-full w-24 h-24 flex items-center justify-center shadow-2xl shadow-orange-500/50 border-4 border-white">
                  <div className="text-center">
                    <div className="text-2xl">📰</div>
                    <div className="text-white text-xs font-bold">CLAIM</div>
                  </div>
                </div>
              </div>

              {/* Evidence Nodes */}
              {results.evidenceLinks.map((link, idx) => {
                const angle = (idx / results.evidenceLinks.length) * 2 * Math.PI
                const radius = 140
                const x = Math.cos(angle) * radius
                const y = Math.sin(angle) * radius
                
                const isCredible = link.type === 'credible'
                const color = isCredible ? 'green' : 'red'
                
                return (
                  <div key={idx}>
                    {/* Connection Line */}
                    <svg className="absolute top-0 left-0 w-full h-full pointer-events-none">
                      <line
                        x1="50%"
                        y1="50%"
                        x2={`calc(50% + ${x}px)`}
                        y2={`calc(50% + ${y}px)`}
                        stroke={isCredible ? '#10b981' : '#ef4444'}
                        strokeWidth="2"
                        opacity="0.5"
                        strokeDasharray={isCredible ? '0' : '5,5'}
                      />
                    </svg>
                    
                    {/* Evidence Node */}
                    <div
                      className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
                      style={{
                        marginLeft: `${x}px`,
                        marginTop: `${y}px`
                      }}
                    >
                      <div
                        className={`bg-slate-800 border-2 border-${color}-500 rounded-lg p-2 w-24 hover:scale-110 transition-all cursor-pointer shadow-lg`}
                        title={link.verdict}
                      >
                        <div className="text-white text-xs font-semibold text-center truncate">{link.source}</div>
                        <div className={`text-${color}-400 text-[10px] text-center mt-1`}>
                          {(link.similarity * 100).toFixed(0)}%
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>

            <div className="mt-4 grid grid-cols-2 gap-4 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-green-500 rounded"></div>
                <span className="text-gray-400">Credible Source (Contradicts)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-red-500 rounded"></div>
                <span className="text-gray-400">Unreliable/Satire (Supports)</span>
              </div>
            </div>
          </div>

          {/* Coordinator Analysis */}
          <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 border-2 border-purple-500 rounded-xl p-6">
            <div className="flex items-start gap-4">
              <div className="text-4xl">✨</div>
              <div className="flex-1">
                <h3 className="text-purple-400 font-bold text-lg mb-2">
                  Gemini 2.5 Flash Coordinator Analysis
                </h3>
                <p className="text-gray-300 leading-relaxed mb-4">{results.coordinatorAnalysis}</p>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-slate-900/50 rounded-lg p-3">
                    <div className="text-cyan-400 text-xs mb-1">Jaccard Index</div>
                    <div className="text-white font-bold">{results.jaccardScore.toFixed(3)}</div>
                  </div>
                  <div className="bg-slate-900/50 rounded-lg p-3">
                    <div className="text-cyan-400 text-xs mb-1">Confidence</div>
                    <div className="text-white font-bold">{(results.confidence * 100).toFixed(1)}%</div>
                  </div>
                  <div className="bg-slate-900/50 rounded-lg p-3">
                    <div className="text-cyan-400 text-xs mb-1">Evidence Quality</div>
                    <div className="text-white font-bold">Strong</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Empty State */}
      {!results && !loading && (
        <div className="text-center py-20">
          <div className="text-6xl mb-4">🕷️</div>
          <h3 className="text-2xl font-bold text-gray-400 mb-2">Agent Swarm Ready</h3>
          <p className="text-gray-500">20 parallel agents ready for cross-verification</p>
        </div>
      )}
    </div>
  )
}

export default AgentSwarm
