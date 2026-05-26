function DatasetAudit() {
  const kpis = [
    { label: 'Total Articles', value: '44.9K', color: 'cyan', icon: '📰' },
    { label: 'Fake Samples', value: '23.5K', color: 'red', icon: '⚠️' },
    { label: 'Real Samples', value: '21.4K', color: 'green', icon: '✅' },
    { label: 'Vocabulary Size', value: '81.5K', color: 'purple', icon: '📚' }
  ]

  const features = [
    {
      title: 'Continuous Learning',
      description: 'Model retraining pipeline with incremental learning capabilities',
      icon: '🔄',
      status: 'Active'
    },
    {
      title: 'Audio/Video OCR',
      description: 'Multimodal content extraction from images, audio, and video sources',
      icon: '🎥',
      status: 'Enabled'
    },
    {
      title: 'XAI (Explainable AI)',
      description: 'Transparent decision-making with attention visualization and SHAP values',
      icon: '🔍',
      status: 'Active'
    },
    {
      title: 'Reuters Dateline Mitigation',
      description: 'Bias correction engine to remove location-based classification shortcuts',
      icon: '🌍',
      status: 'Enabled'
    }
  ]

  return (
    <div className="max-w-7xl mx-auto">
      {/* KPI Counters */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {kpis.map((kpi, idx) => (
          <div
            key={idx}
            className={`bg-slate-800/50 border-2 border-${kpi.color}-500/50 rounded-xl p-6 hover:scale-105 transition-all`}
          >
            <div className="text-4xl mb-3">{kpi.icon}</div>
            <div className={`text-4xl font-black text-${kpi.color}-400 mb-2`}>{kpi.value}</div>
            <div className="text-gray-400 text-sm">{kpi.label}</div>
          </div>
        ))}
      </div>

      {/* Distribution Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Class Distribution */}
        <div className="bg-slate-800/50 border border-cyan-500/30 rounded-xl p-6">
          <h3 className="text-cyan-400 font-bold text-lg mb-4">📊 Class Distribution</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-400">Fake News</span>
                <span className="text-red-400 font-bold">52.3%</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-8 overflow-hidden">
                <div className="h-full bg-gradient-to-r from-red-600 to-red-400 flex items-center justify-end pr-3 text-white text-xs font-bold" style={{ width: '52.3%' }}>
                  23,481
                </div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-400">Real News</span>
                <span className="text-green-400 font-bold">47.7%</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-8 overflow-hidden">
                <div className="h-full bg-gradient-to-r from-green-600 to-green-400 flex items-center justify-end pr-3 text-white text-xs font-bold" style={{ width: '47.7%' }}>
                  21,417
                </div>
              </div>
            </div>
          </div>
          <div className="mt-4 p-3 bg-yellow-900/20 border border-yellow-500/30 rounded-lg">
            <p className="text-yellow-400 text-xs">⚠️ Class Imbalance Ratio: 1.096 (Slight imbalance detected)</p>
          </div>
        </div>

        {/* Train/Test Split */}
        <div className="bg-slate-800/50 border border-cyan-500/30 rounded-xl p-6">
          <h3 className="text-cyan-400 font-bold text-lg mb-4">🔀 Train/Test Split</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-400">Training Set</span>
                <span className="text-blue-400 font-bold">80%</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-8 overflow-hidden">
                <div className="h-full bg-gradient-to-r from-blue-600 to-blue-400 flex items-center justify-end pr-3 text-white text-xs font-bold" style={{ width: '80%' }}>
                  35,918
                </div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-400">Testing Set</span>
                <span className="text-purple-400 font-bold">20%</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-8 overflow-hidden">
                <div className="h-full bg-gradient-to-r from-purple-600 to-purple-400 flex items-center justify-end pr-3 text-white text-xs font-bold" style={{ width: '20%' }}>
                  8,980
                </div>
              </div>
            </div>
          </div>
          <div className="mt-4 p-3 bg-green-900/20 border border-green-500/30 rounded-lg">
            <p className="text-green-400 text-xs">✅ Stratified split maintains class distribution</p>
          </div>
        </div>
      </div>

      {/* Dataset Issues */}
      <div className="bg-slate-800/50 border border-red-500/30 rounded-xl p-6 mb-8">
        <h3 className="text-red-400 font-bold text-lg mb-4">🚨 Known Dataset Biases & Mitigations</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="text-2xl">📍</div>
              <div>
                <h4 className="text-white font-semibold mb-1">Reuters Dateline Bias</h4>
                <p className="text-gray-400 text-sm mb-2">78.3% of real news contains Reuters dateline markers</p>
                <div className="text-xs text-cyan-400">✓ Mitigation: Bias correction engine strips location markers</div>
              </div>
            </div>
          </div>
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="text-2xl">📋</div>
              <div>
                <h4 className="text-white font-semibold mb-1">Near-Duplicates</h4>
                <p className="text-gray-400 text-sm mb-2">1,247 near-duplicate articles detected</p>
                <div className="text-xs text-cyan-400">✓ Mitigation: Deduplication preprocessing applied</div>
              </div>
            </div>
          </div>
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="text-2xl">📅</div>
              <div>
                <h4 className="text-white font-semibold mb-1">Temporal Bias</h4>
                <p className="text-gray-400 text-sm mb-2">Dataset limited to 2015-2017 US politics</p>
                <div className="text-xs text-cyan-400">✓ Mitigation: Live scraping adds recent articles</div>
              </div>
            </div>
          </div>
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="text-2xl">✍️</div>
              <div>
                <h4 className="text-white font-semibold mb-1">Stylistic Patterns</h4>
                <p className="text-gray-400 text-sm mb-2">Models may overfit to writing style vs. content</p>
                <div className="text-xs text-cyan-400">✓ Mitigation: LLM ensemble for semantic analysis</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Architecture Features */}
      <div className="bg-slate-800/50 border border-cyan-500/30 rounded-xl p-6">
        <h3 className="text-cyan-400 font-bold text-lg mb-4">🏗️ System Architecture Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {features.map((feature, idx) => (
            <div key={idx} className="bg-slate-900/50 rounded-lg p-4 hover:bg-slate-900/70 transition-all">
              <div className="flex items-start gap-3">
                <div className="text-3xl">{feature.icon}</div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-white font-semibold">{feature.title}</h4>
                    <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded-full">
                      {feature.status}
                    </span>
                  </div>
                  <p className="text-gray-400 text-sm">{feature.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Dataset Info */}
      <div className="mt-6 bg-blue-900/20 border border-blue-500/30 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <div className="text-2xl">ℹ️</div>
          <div>
            <h4 className="text-blue-400 font-semibold mb-1">ISOT Fake News Dataset</h4>
            <p className="text-gray-400 text-sm">
              Source: University of Victoria | Date Range: 2015-2017 | Topics: US Politics, World News, Government
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DatasetAudit
