import { useState } from 'react'

function Sidebar({ inputText, setInputText, setPresetArticle }) {
  const [dragActive, setDragActive] = useState(false)

  const presets = [
    {
      id: 1,
      title: 'Real Reuters',
      type: 'real',
      text: 'WASHINGTON (Reuters) - The U.S. Federal Reserve raised interest rates by 25 basis points on Wednesday, marking the tenth consecutive rate hike as the central bank continues its fight against inflation. Fed Chair Jerome Powell stated that the committee remains committed to bringing inflation back to its 2% target.'
    },
    {
      id: 2,
      title: 'Sensational Fake',
      type: 'fake',
      text: 'BREAKING: Secret government documents reveal shocking truth about alien technology being used in smartphones! Whistleblower claims major tech companies have been hiding this for decades. Click here to learn what THEY don\'t want you to know!'
    },
    {
      id: 3,
      title: 'Satirical News',
      type: 'satire',
      text: 'Local Man Discovers Internet Argument He Won in 2015 Still Going Strong. "I thought I had the last word," says Dave Thompson, 34, who recently checked back on a Reddit thread about pineapple on pizza. "Turns out, 47 people have continued the debate without me."'
    }
  ]

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleFile = (file) => {
    alert('OCR processing: ' + file.name)
  }

  const getPresetClass = (type) => {
    if (type === 'real') return 'border-green-500/50 bg-green-900/20 hover:bg-green-900/40 hover:border-green-500'
    if (type === 'fake') return 'border-red-500/50 bg-red-900/20 hover:bg-red-900/40 hover:border-red-500'
    return 'border-yellow-500/50 bg-yellow-900/20 hover:bg-yellow-900/40 hover:border-yellow-500'
  }

  const getPresetIconClass = (type) => {
    if (type === 'real') return 'text-green-400'
    if (type === 'fake') return 'text-red-400'
    return 'text-yellow-400'
  }

  const getPresetIcon = (type) => {
    if (type === 'real') return '✓'
    if (type === 'fake') return '⚠'
    return '😄'
  }

  return (
    <div className="w-96 bg-slate-800/50 border-r border-cyan-500/30 p-6 overflow-y-auto h-[calc(100vh-180px)]">
      {/* Input Text Area */}
      <div className="mb-6">
        <label className="block text-cyan-400 font-semibold mb-2 text-sm">
          📝 Input News Article
        </label>
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Paste your news article here..."
          className="w-full h-40 bg-slate-900/50 border border-cyan-500/30 rounded-lg p-3 text-gray-300 text-sm focus:outline-none focus:border-cyan-500 resize-none"
        />
      </div>

      {/* Preset Selector */}
      <div className="mb-6">
        <label className="block text-cyan-400 font-semibold mb-3 text-sm">
          🎯 Preset Test Articles
        </label>
        <div className="space-y-3">
          {presets.map(preset => (
            <button
              key={preset.id}
              onClick={() => setInputText(preset.text)}
              className={`w-full p-3 rounded-lg border-2 transition-all text-left ${getPresetClass(preset.type)}`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-xs font-bold ${getPresetIconClass(preset.type)}`}>
                  {getPresetIcon(preset.type)}
                </span>
                <span className="text-white font-semibold text-sm">{preset.title}</span>
              </div>
              <p className="text-gray-400 text-xs line-clamp-2">{preset.text}</p>
            </button>
          ))}
        </div>
      </div>

      {/* OCR Uploader */}
      <div className="mb-6">
        <label className="block text-cyan-400 font-semibold mb-3 text-sm">
          📷 OCR Image Upload
        </label>
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-6 text-center transition-all ${dragActive ? 'border-cyan-500 bg-cyan-900/20' : 'border-cyan-500/30 bg-slate-900/30 hover:border-cyan-500/50'}`}
        >
          <svg className="w-12 h-12 mx-auto mb-3 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p className="text-gray-400 text-sm mb-2">Drag & drop image here</p>
          <p className="text-gray-500 text-xs mb-3">or</p>
          <label className="cursor-pointer bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors inline-block">
            Browse Files
            <input type="file" className="hidden" accept="image/*" onChange={(e) => e.target.files[0] && handleFile(e.target.files[0])} />
          </label>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="bg-slate-900/50 border border-cyan-500/30 rounded-lg p-4">
        <h3 className="text-cyan-400 font-semibold text-sm mb-3">📊 Quick Stats</h3>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-400">Character Count:</span>
            <span className="text-white font-semibold">{inputText.length}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Word Count:</span>
            <span className="text-white font-semibold">{inputText.split(/\s+/).filter(w => w).length}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Status:</span>
            <span className={`font-semibold ${inputText.length > 50 ? 'text-green-400' : 'text-yellow-400'}`}>
              {inputText.length > 50 ? 'Ready' : 'Need more text'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
