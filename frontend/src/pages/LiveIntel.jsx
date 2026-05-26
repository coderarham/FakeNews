import { useState, useEffect } from 'react'

function LiveIntel() {
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Fetch articles from backend
  const fetchArticles = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('http://localhost:5000/api/live-news?limit=20')
      if (!response.ok) {
        throw new Error('Failed to fetch articles')
      }
      const data = await response.json()
      
      // Transform backend data to frontend format
      const transformedArticles = data.articles.map((article, index) => ({
        id: index + 1,
        headline: article.title,
        source: article.source,
        category: getCategoryFromSource(article.source),
        timestamp: getTimeAgo(article.fetched_at),
        duplicateCheck: true,
        biasStripped: article.bias_flags.includes('NEUTRAL'),
        content: article.content,
        url: article.url  // Add URL
      }))
      
      setArticles(transformedArticles)
    } catch (err) {
      setError(err.message)
      console.error('Error fetching articles:', err)
    } finally {
      setLoading(false)
    }
  }

  // Helper: Get category from source
  const getCategoryFromSource = (source) => {
    if (source.includes('Reuters') || source.includes('Financial')) return 'Finance'
    if (source.includes('BBC') || source.includes('Tech')) return 'Tech'
    if (source.includes('Onion') || source.includes('Babylon')) return 'Satire'
    if (source.includes('AP') || source.includes('CNN')) return 'Global News'
    return 'News'
  }

  // Helper: Convert timestamp to "X hours ago"
  const getTimeAgo = (timestamp) => {
    const now = new Date()
    const then = new Date(timestamp)
    const diffMs = now - then
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    
    if (diffHours < 1) return 'Just now'
    if (diffHours === 1) return '1 hour ago'
    if (diffHours < 24) return `${diffHours} hours ago`
    const diffDays = Math.floor(diffHours / 24)
    return diffDays === 1 ? '1 day ago' : `${diffDays} days ago`
  }

  // Fetch on component mount
  useEffect(() => {
    fetchArticles()
  }, [])

  const categoryData = [
    { name: 'Politics', value: 35, color: '#3b82f6' },
    { name: 'Global News', value: 25, color: '#10b981' },
    { name: 'Tech', value: 20, color: '#8b5cf6' },
    { name: 'Finance', value: 15, color: '#f59e0b' },
    { name: 'Satire', value: 5, color: '#ef4444' }
  ]

  const total = categoryData.reduce((sum, item) => sum + item.value, 0)
  let currentAngle = 0

  return (
    <div className="max-w-7xl mx-auto">
      {/* Pipeline Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-800/50 border border-green-500/30 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <h3 className="text-green-400 font-bold">Scraper Status</h3>
          </div>
          <div className="text-3xl font-black text-white mb-2">ACTIVE</div>
          <p className="text-gray-400 text-sm">Next run in 18 minutes</p>
        </div>

        <div className="bg-slate-800/50 border border-cyan-500/30 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="text-2xl">⏱️</div>
            <h3 className="text-cyan-400 font-bold">Schedule Frequency</h3>
          </div>
          <div className="text-3xl font-black text-white mb-2">30 min</div>
          <p className="text-gray-400 text-sm">Automated cron job</p>
        </div>

        <div className="bg-slate-800/50 border border-purple-500/30 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="text-2xl">💾</div>
            <h3 className="text-purple-400 font-bold">Cache Window</h3>
          </div>
          <div className="text-3xl font-black text-white mb-2">72 hrs</div>
          <p className="text-gray-400 text-sm">SQLite database</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Category Pie Chart */}
        <div className="bg-slate-800/50 border border-cyan-500/30 rounded-xl p-6">
          <h3 className="text-cyan-400 font-bold text-lg mb-6">📊 Article Category Distribution</h3>
          
          <div className="flex items-center justify-center mb-6">
            <svg width="240" height="240" viewBox="0 0 240 240">
              {categoryData.map((item, idx) => {
                const percentage = (item.value / total) * 100
                const angle = (item.value / total) * 360
                const startAngle = currentAngle
                const endAngle = currentAngle + angle
                
                const startRad = (startAngle - 90) * (Math.PI / 180)
                const endRad = (endAngle - 90) * (Math.PI / 180)
                
                const x1 = 120 + 100 * Math.cos(startRad)
                const y1 = 120 + 100 * Math.sin(startRad)
                const x2 = 120 + 100 * Math.cos(endRad)
                const y2 = 120 + 100 * Math.sin(endRad)
                
                const largeArc = angle > 180 ? 1 : 0
                
                const path = `M 120 120 L ${x1} ${y1} A 100 100 0 ${largeArc} 1 ${x2} ${y2} Z`
                
                currentAngle = endAngle
                
                return (
                  <g key={idx}>
                    <path
                      d={path}
                      fill={item.color}
                      opacity="0.8"
                      className="hover:opacity-100 transition-opacity cursor-pointer"
                    />
                  </g>
                )
              })}
              <circle cx="120" cy="120" r="60" fill="#1e293b" />
              <text x="120" y="115" textAnchor="middle" fill="#94a3b8" fontSize="14">Total</text>
              <text x="120" y="135" textAnchor="middle" fill="#fff" fontSize="24" fontWeight="bold">{total}%</text>
            </svg>
          </div>

          <div className="space-y-2">
            {categoryData.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded" style={{ backgroundColor: item.color }}></div>
                  <span className="text-gray-300 text-sm">{item.name}</span>
                </div>
                <span className="text-white font-semibold">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Pipeline Activity Log */}
        <div className="bg-slate-800/50 border border-cyan-500/30 rounded-xl p-6">
          <h3 className="text-cyan-400 font-bold text-lg mb-4">📡 Pipeline Activity Log</h3>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            <div className="flex items-center gap-3 text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-gray-400">12:45 PM</span>
              <span className="text-green-400">Scraper executed successfully</span>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-gray-400">12:44 PM</span>
              <span className="text-blue-400">Fetched 47 articles from NewsAPI</span>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span className="text-gray-400">12:43 PM</span>
              <span className="text-purple-400">RSS feeds parsed: 12 sources</span>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span className="text-gray-400">12:42 PM</span>
              <span className="text-yellow-400">Duplicate check: 8 removed</span>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <div className="w-2 h-2 bg-cyan-500 rounded-full"></div>
              <span className="text-gray-400">12:41 PM</span>
              <span className="text-cyan-400">Bias correction applied to 23 articles</span>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-gray-400">12:40 PM</span>
              <span className="text-green-400">Database updated: 39 new entries</span>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-slate-700">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Total Scraped Today:</span>
                <div className="text-2xl font-bold text-white">342</div>
              </div>
              <div>
                <span className="text-gray-400">Cache Size:</span>
                <div className="text-2xl font-bold text-white">2.4K</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Scraped Articles */}
      <div className="bg-slate-800/50 border border-cyan-500/30 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-cyan-400 font-bold text-lg">📰 Recent Scraped Articles</h3>
          <button
            onClick={fetchArticles}
            disabled={loading}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 disabled:bg-gray-600 text-white rounded-lg transition-all text-sm font-semibold"
          >
            {loading ? '🔄 Loading...' : '🔄 Refresh'}
          </button>
        </div>
        
        {error && (
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4 mb-4">
            <p className="text-red-400">Error: {error}</p>
            <p className="text-gray-400 text-sm mt-1">Make sure backend is running on port 5000</p>
          </div>
        )}
        
        {loading && (
          <div className="text-center py-8">
            <div className="text-4xl mb-2">⏳</div>
            <p className="text-gray-400">Loading articles...</p>
          </div>
        )}
        
        {!loading && articles.length === 0 && (
          <div className="text-center py-8">
            <div className="text-4xl mb-2">📭</div>
            <p className="text-gray-400">No articles found</p>
            <p className="text-gray-500 text-sm mt-1">Click Refresh to fetch latest news</p>
          </div>
        )}
        
        <div className="space-y-3">
          {articles.map(article => (
            <a
              key={article.id}
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block bg-slate-900/50 rounded-lg p-4 hover:bg-slate-900/70 transition-all border border-slate-700 hover:border-cyan-500/50 cursor-pointer"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <h4 className="text-white font-semibold mb-2 hover:text-cyan-400 transition-colors">
                    {article.headline}
                  </h4>
                  <div className="flex items-center gap-4 text-xs">
                    <span className="text-gray-400">
                      <span className="text-cyan-400">Source:</span> {article.source}
                    </span>
                    <span className={`px-2 py-1 rounded-full ${
                      article.category === 'Satire' ? 'bg-red-500/20 text-red-400' :
                      article.category === 'Tech' ? 'bg-purple-500/20 text-purple-400' :
                      article.category === 'Finance' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-blue-500/20 text-blue-400'
                    }`}>
                      {article.category}
                    </span>
                    <span className="text-gray-500">{article.timestamp}</span>
                  </div>
                </div>
                <div className="flex flex-col gap-2">
                  {article.duplicateCheck && (
                    <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded-full whitespace-nowrap">
                      ✓ Unique
                    </span>
                  )}
                  {article.biasStripped && (
                    <span className="text-xs bg-cyan-500/20 text-cyan-400 px-2 py-1 rounded-full whitespace-nowrap">
                      ✓ Bias Stripped
                    </span>
                  )}
                  <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded-full whitespace-nowrap">
                    🔗 Open
                  </span>
                </div>
              </div>
            </a>
          ))}
        </div>
      </div>

      {/* Data Sources */}
      <div className="mt-6 bg-blue-900/20 border border-blue-500/30 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <div className="text-2xl">🌐</div>
          <div>
            <h4 className="text-blue-400 font-semibold mb-1">Live Data Sources</h4>
            <p className="text-gray-400 text-sm">
              NewsAPI (newsapi.org) | RSS Feeds (BBC, Reuters, AP, NYT, CNN) | 72-hour rolling cache with SQLite
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LiveIntel
