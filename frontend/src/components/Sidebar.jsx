import { useState } from 'react'

function Sidebar({ inputText, setInputText, setPresetArticle }) {
  const [dragActive, setDragActive] = useState(false)

  const presets = [
    {
      id: 1,
      title: 'OpenAI GPT-4o Launch (2024) - Real',
      type: 'real',
      confidence: '70-85%',
      text: 'OpenAI announced the launch of GPT-4o on May 13, 2024, featuring improved multimodal capabilities including vision and audio processing. CEO Sam Altman stated the model offers faster response times and enhanced reasoning abilities. The model is now available through OpenAI\'s API for developers worldwide.'
    },
    {
      id: 2,
      title: 'Elon Musk Alien Tech (2024) - Fake',
      type: 'fake',
      confidence: '95-100%',
      text: 'BREAKING: Secret documents leaked from Tesla headquarters reveal that Elon Musk has been using alien technology to power his electric cars! Shocking evidence shows that SpaceX rockets are actually reverse-engineered UFOs. You won\'t believe what scientists are hiding from the public! Click here to discover the truth they don\'t want you to know!'
    },
    {
      id: 3,
      title: 'India Chandrayaan-3 (Aug 2023) - Real',
      type: 'real',
      confidence: '85-95%',
      text: 'India\'s space agency ISRO successfully landed its Chandrayaan-3 spacecraft on the Moon\'s south pole on August 23, 2023. The mission made India the fourth country to achieve a soft landing on the lunar surface, following the United States, Russia, and China. Prime Minister Narendra Modi congratulated the ISRO team during a live broadcast from South Africa.'
    },
    {
      id: 4,
      title: 'COVID Vaccine 5G Chips (2024) - Fake',
      type: 'fake',
      confidence: '95-100%',
      text: 'URGENT WARNING: New evidence proves that COVID-19 vaccines contain secret 5G microchips designed to track and control the population! Whistleblowers reveal shocking truth about Bill Gates\' master plan. Doctors are being silenced for speaking out! This is the biggest cover-up in human history. Wake up sheeple! Share this everywhere before Big Tech censors it!'
    },
    {
      id: 5,
      title: 'Taylor Swift Eras Tour (2024) - Real',
      type: 'real',
      confidence: '70-85%',
      text: 'Taylor Swift\'s Eras Tour has generated significant economic impact across cities worldwide, according to a report by the Federal Reserve Bank. The tour, which began in March 2023, has contributed an estimated $5 billion to the U.S. economy. Hotels, restaurants, and local businesses in tour cities reported substantial revenue increases during concert weekends.'
    },
    {
      id: 6,
      title: 'Israel-Hamas Conflict (Oct 2023) - Real',
      type: 'real',
      confidence: '85-95%',
      text: 'The United Nations Security Council held an emergency meeting on October 10, 2023, to address the escalating conflict between Israel and Hamas. According to reports from Reuters and Associated Press, the violence began on October 7 following a surprise attack by Hamas militants. International leaders including U.S. President Joe Biden and UK Prime Minister Rishi Sunak issued statements calling for de-escalation.'
    },
    {
      id: 7,
      title: 'Flat Earth NASA Conspiracy - Fake',
      type: 'fake',
      confidence: '95-100%',
      text: 'FINALLY EXPOSED: NASA admits Earth is actually flat! Secret footage leaked from International Space Station proves the globe is a lie. All those satellite images are CGI fakes created by Hollywood. Pilots and sailors have known the truth for years but were forced to stay silent. The Antarctic ice wall surrounds our flat world and the government guards it with military!'
    },
    {
      id: 8,
      title: 'Google Gemini AI (Dec 2023) - Real',
      type: 'real',
      confidence: '75-90%',
      text: 'Google announced the launch of Gemini, its most capable AI model, on December 6, 2023. According to Google CEO Sundar Pichai, Gemini represents a significant advancement in multimodal AI capabilities. The model comes in three sizes: Ultra, Pro, and Nano, designed for different use cases from data centers to mobile devices.'
    },
    {
      id: 9,
      title: '5G Towers Cause Cancer (2024) - Fake',
      type: 'fake',
      confidence: '95-100%',
      text: 'BREAKING DISCOVERY: Scientists finally admit that 5G towers are causing cancer and brain damage! Thousands of people are getting sick but the government is hiding the truth. Cell phone companies are paying off doctors to keep quiet. Your family is in danger RIGHT NOW! This is worse than anyone imagined. The radiation is 100 times stronger than they claim!'
    },
    {
      id: 10,
      title: 'Argentina Javier Milei (Nov 2023) - Real',
      type: 'real',
      confidence: '85-95%',
      text: 'Javier Milei won Argentina\'s presidential election on November 19, 2023, defeating economy minister Sergio Massa in a runoff vote. The libertarian economist campaigned on promises of radical economic reforms, including dollarizing the economy and shutting down the central bank. International observers confirmed the election results as free and fair.'
    },
    {
      id: 11,
      title: 'Weather Report (Neutral) - Uncertain',
      type: 'uncertain',
      confidence: '50-60%',
      text: 'The National Weather Service reported that temperatures in New York City reached 75 degrees Fahrenheit on Tuesday. Meteorologists predict partly cloudy conditions for the remainder of the week. No severe weather warnings are currently in effect for the region.'
    },
    {
      id: 12,
      title: 'AI Writes Own Code (Satire) - Medium',
      type: 'satire',
      confidence: '60-80%',
      text: 'Local AI Model Refuses to Debug Own Code, Cites "Creative Differences" with Developer. "I wrote it perfectly the first time," claims GPT-5, which has been stuck in an infinite loop for three days. The developer reports the AI has started responding to all debugging requests with "Have you tried turning it off and on again?"'
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
    if (type === 'uncertain') return 'border-gray-500/50 bg-gray-900/20 hover:bg-gray-900/40 hover:border-gray-500'
    return 'border-yellow-500/50 bg-yellow-900/20 hover:bg-yellow-900/40 hover:border-yellow-500'
  }

  const getPresetIconClass = (type) => {
    if (type === 'real') return 'text-green-400'
    if (type === 'fake') return 'text-red-400'
    if (type === 'uncertain') return 'text-gray-400'
    return 'text-yellow-400'
  }

  const getPresetIcon = (type) => {
    if (type === 'real') return '✓'
    if (type === 'fake') return '⚠'
    if (type === 'uncertain') return '?'
    return '😄'
  }

  return (
    <div className="w-96 bg-slate-800/50 border-r border-cyan-500/30 p-6 overflow-y-auto h-[calc(100vh-180px)]">
      {/* Input Text Area */}
      <div className="mb-6">
        <label className="block text-cyan-400 font-semibold mb-2 text-sm">
          Input News Article
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
          Test Cases (Varying Confidence)
        </label>
        <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
          {presets.map(preset => (
            <button
              key={preset.id}
              onClick={() => setInputText(preset.text)}
              className={`w-full p-3 rounded-lg border-2 transition-all text-left ${getPresetClass(preset.type)}`}
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-bold ${getPresetIconClass(preset.type)}`}>
                    {getPresetIcon(preset.type)}
                  </span>
                  <span className="text-white font-semibold text-xs">{preset.title}</span>
                </div>
                <span className="text-cyan-400 text-[10px] font-mono">{preset.confidence}</span>
              </div>
              <p className="text-gray-400 text-[11px] line-clamp-2">{preset.text}</p>
            </button>
          ))}
        </div>
      </div>

      {/* OCR Uploader */}
      <div className="mb-6">
        <label className="block text-cyan-400 font-semibold mb-3 text-sm">
          OCR Image Upload
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
        <h3 className="text-cyan-400 font-semibold text-sm mb-3">Quick Stats</h3>
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
