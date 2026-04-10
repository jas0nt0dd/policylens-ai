import React from 'react'
import { Scale } from 'lucide-react'

export default function AnalysisProgress({ progress, stage, stages }) {
  return (
    <div className="max-w-xl mx-auto text-center py-12">
      {/* Animated icon */}
      <div className="relative w-24 h-24 mx-auto mb-8">
        <div className="w-24 h-24 rounded-full bg-primary-600/20 flex items-center justify-center animate-pulse">
          <Scale size={40} className="text-primary-400"/>
        </div>
        <svg className="absolute inset-0 w-24 h-24 -rotate-90" viewBox="0 0 96 96">
          <circle cx="48" cy="48" r="44" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="4"/>
          <circle cx="48" cy="48" r="44" fill="none" stroke="#3b82f6" strokeWidth="4"
            strokeDasharray={`${2 * Math.PI * 44}`}
            strokeDashoffset={`${2 * Math.PI * 44 * (1 - progress / 100)}`}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.6s ease' }}/>
        </svg>
      </div>

      <h2 className="text-2xl font-bold mb-2">Analyzing Policy Document</h2>
      <p className="text-primary-400 font-medium mb-8">{stage || 'Initializing...'}</p>

      {/* Progress bar */}
      <div className="glass rounded-full h-3 mb-4 overflow-hidden">
        <div className="h-full bg-gradient-to-r from-primary-600 to-accent-500 bias-bar rounded-full"
          style={{ width: `${progress}%` }}/>
      </div>
      <p className="text-gray-400 text-sm mb-10">{progress}% complete</p>

      {/* Stage checklist */}
      <div className="space-y-2 text-left">
        {stages.map((s, i) => {
          const stageProgress = (i + 1) / stages.length * 100
          const done = progress >= stageProgress
          const active = progress >= (i / stages.length * 100) && !done
          return (
            <div key={s} className={`flex items-center gap-3 px-4 py-2 rounded-lg text-sm transition-all
              ${done ? 'text-green-400' : active ? 'text-primary-300' : 'text-gray-600'}`}>
              <span>{done ? '✓' : active ? '◌' : '○'}</span>
              <span>{s}</span>
            </div>
          )
        })}
      </div>

      <p className="text-xs text-gray-600 mt-8">
        Using 100% open-source AI — Mistral 7B · BERT · FAISS · spaCy
      </p>
    </div>
  )
}
