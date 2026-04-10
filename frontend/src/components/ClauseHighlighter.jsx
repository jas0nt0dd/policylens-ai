import React, { useState } from 'react'
import { ChevronDown, ChevronRight, Info } from 'lucide-react'

const RISK_COLORS = { HIGH: 'border-red-500/40 bg-red-500/5', MEDIUM: 'border-yellow-500/40 bg-yellow-500/5', LOW: 'border-green-500/20 bg-green-500/5' }
const RISK_BADGE = { HIGH: 'bg-red-500/20 text-red-400', MEDIUM: 'bg-yellow-500/20 text-yellow-400', LOW: 'bg-green-500/20 text-green-400' }
const BIAS_BADGE = {
  GENDER_BIAS: 'bg-pink-500/20 text-pink-300',
  SOCIOECONOMIC_BIAS: 'bg-orange-500/20 text-orange-300',
  ETHNIC_CASTE_BIAS: 'bg-purple-500/20 text-purple-300',
  REGIONAL_BIAS: 'bg-cyan-500/20 text-cyan-300',
  AGE_BIAS: 'bg-teal-500/20 text-teal-300',
  DISABILITY_HEALTH_BIAS: 'bg-lime-500/20 text-lime-300',
  PROCEDURAL_FAIRNESS_BIAS: 'bg-blue-500/20 text-blue-300',
  GENERAL_BIAS: 'bg-gray-500/20 text-gray-300',
}

export default function ClauseHighlighter({ clauses }) {
  const [expanded, setExpanded] = useState(null)
  const [filter, setFilter] = useState('ALL')

  const biasTypes = ['ALL', ...new Set(clauses.map(c => c.bias_type))]
  const filtered = filter === 'ALL' ? clauses : clauses.filter(c => c.bias_type === filter)

  return (
    <div>
      {/* Filter pills */}
      <div className="flex flex-wrap gap-2 mb-6">
        {biasTypes.map(bt => (
          <button key={bt} onClick={() => setFilter(bt)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-all
              ${filter === bt ? 'bg-primary-600 text-white' : 'glass text-gray-400 hover:text-white'}`}>
            {bt.replace('_', ' ')}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {filtered.map((clause, i) => (
          <div key={clause.clause_id}
            className={`rounded-xl border transition-all ${RISK_COLORS[clause.loophole_risk] || RISK_COLORS.LOW}`}>
            {/* Header row */}
            <button className="w-full flex items-center gap-3 p-4 text-left"
              onClick={() => setExpanded(expanded === i ? null : i)}>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1 flex-wrap">
                  <span className="text-xs font-mono text-gray-500">{clause.clause_id}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${BIAS_BADGE[clause.bias_type] || BIAS_BADGE.GENERAL_BIAS}`}>
                    {clause.bias_type?.replace('_', ' ')}
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${RISK_BADGE[clause.loophole_risk]}`}>
                    {clause.loophole_risk} RISK
                  </span>
                  <span className="text-xs text-gray-500">Bias: {clause.bias_score}/100</span>
                  <span className="text-xs text-gray-500">Confidence: {clause.confidence_score || 0}/100</span>
                </div>
                <p className="text-sm text-white mb-1">{clause.finding_title || 'Flagged clause'}</p>
                <p className="text-sm text-gray-300 truncate">{clause.original_text?.slice(0, 140)}...</p>
              </div>
              {expanded === i ? <ChevronDown size={16} className="text-gray-500 flex-shrink-0"/> : <ChevronRight size={16} className="text-gray-500 flex-shrink-0"/>}
            </button>

            {/* Expanded detail */}
            {expanded === i && (
              <div className="px-4 pb-4 space-y-4 border-t border-white/5 pt-4">
                <div>
                  <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Original Text</p>
                  <p className="text-sm text-gray-300 leading-relaxed bg-white/3 rounded-lg p-3 font-mono">{clause.original_text}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Plain English</p>
                  <p className="text-sm text-green-300 leading-relaxed bg-green-500/5 rounded-lg p-3">{clause.plain_english}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Why It Was Flagged</p>
                  <p className="text-sm text-gray-300 leading-relaxed">{clause.explanation}</p>
                </div>
                {clause.why_it_matters && (
                  <div>
                    <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Why This Matters</p>
                    <p className="text-sm text-gray-300 leading-relaxed">{clause.why_it_matters}</p>
                  </div>
                )}
                {clause.impacted_groups?.length > 0 && (
                  <div>
                    <p className="text-xs text-gray-500 mb-2 uppercase tracking-wider">Impacted Groups</p>
                    <div className="flex flex-wrap gap-2">
                      {clause.impacted_groups.map(group => (
                        <span key={group} className="text-xs bg-primary-500/20 text-primary-300 px-2 py-0.5 rounded-full">{group}</span>
                      ))}
                    </div>
                  </div>
                )}
                {clause.matched_signals?.length > 0 && (
                  <div>
                    <p className="text-xs text-gray-500 mb-2 uppercase tracking-wider">Evidence Signals</p>
                    <div className="flex flex-wrap gap-2">
                      {clause.matched_signals.map(signal => (
                        <span key={signal} className="text-xs bg-white/5 text-gray-300 px-2 py-0.5 rounded-full">{signal}</span>
                      ))}
                    </div>
                  </div>
                )}
                {clause.sdg_violations?.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    <p className="text-xs text-gray-500 mr-2 self-center">SDG Violations:</p>
                    {clause.sdg_violations.map(s => (
                      <span key={s} className="text-xs bg-orange-500/20 text-orange-300 px-2 py-0.5 rounded-full">{s}</span>
                    ))}
                  </div>
                )}
                <div className="glass rounded-lg p-3">
                  <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Recommendation</p>
                  <p className="text-sm text-blue-300">{clause.recommendation}</p>
                </div>
                {clause.suggested_rewrite && (
                  <div className="rounded-lg border border-primary-500/20 bg-primary-500/10 p-3">
                    <p className="text-xs text-gray-500 mb-1 uppercase tracking-wider">Safer Rewrite</p>
                    <p className="text-sm text-gray-200 leading-relaxed">{clause.suggested_rewrite}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {filtered.length === 0 && (
          <div className="text-center py-12 text-gray-600">
            <Info size={32} className="mx-auto mb-3"/>
            <p>No clauses found for this filter.</p>
          </div>
        )}
      </div>
    </div>
  )
}
