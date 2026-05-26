import { useState, useEffect } from 'react'

function Header({ biasCorrection, setBiasCorrection }) {
  const [systemStatus, setSystemStatus] = useState({
    ready: true,
    geminiConnected: true,
    fallback: false
  })

  return (
    <header className="bg-gradient-to-r from-slate-900 via-purple-900 to-slate-900 border-b-2 border-cyan-500 shadow-lg shadow-cyan-500/50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo & Title */}
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-cyan-500 blur-xl opacity-50 animate-pulse"></div>
              <div className="relative bg-gradient-to-br from-cyan-500 to-purple-600 p-3 rounded-lg">
                <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent animate-pulse">
                TRUTHLENS
              </h1>
              <p className="text-xs text-cyan-400 font-semibold tracking-wider">v2.5 Pro</p>
            </div>
          </div>

          {/* System Status Indicators */}
          <div className="flex items-center gap-6">
            {/* System Ready */}
            <div className="flex items-center gap-2">
              <div className="relative">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <div className="absolute inset-0 w-3 h-3 bg-green-500 rounded-full animate-ping"></div>
              </div>
              <span className="text-green-400 text-sm font-semibold">System Ready</span>
            </div>

            {/* Gemini API Status */}
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${
                systemStatus.geminiConnected ? 'bg-cyan-500' : 'bg-yellow-500'
              } animate-pulse`}></div>
              <span className={`text-sm font-semibold ${
                systemStatus.geminiConnected ? 'text-cyan-400' : 'text-yellow-400'
              }`}>
                Gemini API: {systemStatus.geminiConnected ? 'Connected' : 'Fallback'}
              </span>
            </div>

            {/* User Profile */}
            <div className="flex items-center gap-2 bg-slate-800/50 px-4 py-2 rounded-lg border border-cyan-500/30">
              <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                TL
              </div>
              <span className="text-gray-300 text-sm">Team Logic Lords</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
