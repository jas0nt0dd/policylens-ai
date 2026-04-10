import React, { useState } from 'react'
import { GitCompare, CheckCircle, XCircle, Minus } from 'lucide-react'
import api from '../api'

export default function Compare() {
  const [id1, setId1] = useState('')
  const [id2, setId2] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleCompare = async () => {
    if (!id1.trim() || !id2.trim()) return
    setLoading(true); setError(null)
    try {
      const { data } = await api.post('/api/compare', { report_id_1: id1.trim(), report_id_2: id2.trim() })
      setResult(data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Comparison failed.')
    } finally { setLoading(false) }
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <div className="mb-10">
        <h1 className="text-4xl font-black mb-2">Compare Policies</h1>
        <p className="text-gray-400">Compare a biased draft against an improved one and show judges exactly why one policy is fairer.</p>
      </div>

      <div className="glass rounded-2xl p-8 mb-8">
        <div className="grid md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="text-sm text-gray-400 mb-2 block">Report ID 1</label>
            <input value={id1} onChange={e => setId1(e.target.value)}
              placeholder="e.g. abc123..."
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-primary-500"/>
          </div>
          <div>
            <label className="text-sm text-gray-400 mb-2 block">Report ID 2</label>
            <input value={id2} onChange={e => setId2(e.target.value)}
              placeholder="e.g. def456..."
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-primary-500"/>
          </div>
        </div>
        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}
        <button onClick={handleCompare} disabled={loading}
          className="flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-500 rounded-xl font-semibold transition-all disabled:opacity-50">
          <GitCompare size={18}/>
          {loading ? 'Comparing...' : 'Compare Documents'}
        </button>
      </div>

      {result && (
        <div className="space-y-6">
          {/* Summary */}
          <div className="glass rounded-2xl p-6">
            <h2 className="font-semibold text-lg mb-3">Comparison Summary</h2>
            <p className="text-gray-300 leading-relaxed">{result.comparison_summary}</p>
            <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-600/20 text-primary-300 text-sm">
              ✓ Better policy: <strong className="text-white">{result.better_document}</strong>
            </div>
            <p className="text-sm text-gray-400 mt-4">{result.better_document_reason}</p>
          </div>

          {/* Score comparison */}
          <div className="grid md:grid-cols-2 gap-6">
            {[result.document_1_title, result.document_2_title].map((name, i) => (
              <div key={name} className="glass rounded-2xl p-6">
                <h3 className="font-medium text-gray-300 mb-4 truncate">{name}</h3>
                <div className="space-y-3">
                  <ScoreRow
                    label="Bias Score"
                    value={i === 0 ? result.document_1_bias_score : result.document_2_bias_score}
                    max={100}
                    invert
                  />
                  <ScoreRow
                    label="SDG Score"
                    value={i === 0 ? result.document_1_sdg_score : result.document_2_sdg_score}
                    max={100}
                  />
                </div>
                <div className="mt-5">
                  <p className="text-xs uppercase tracking-wider text-gray-500 mb-2">Top Findings</p>
                  <div className="space-y-2">
                    {(i === 0 ? result.document_1_top_findings : result.document_2_top_findings).map((finding) => (
                      <div key={finding} className="text-sm text-gray-300 bg-white/5 rounded-lg px-3 py-2">
                        {finding}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Issues */}
          <div className="grid md:grid-cols-3 gap-6">
            <IssueList title="Common Issues" items={result.common_issues} icon={<Minus size={14} className="text-yellow-400"/>}/>
            <IssueList title={`${result.document_1} Only`} items={result.doc1_unique_issues} icon={<XCircle size={14} className="text-red-400"/>}/>
            <IssueList title={`${result.document_2} Only`} items={result.doc2_unique_issues} icon={<XCircle size={14} className="text-red-400"/>}/>
          </div>
        </div>
      )}
    </div>
  )
}

function ScoreRow({ label, value, max, invert }) {
  const pct = Math.min(Math.max(Math.round(value), 0), 100)
  const color = invert
    ? pct > 60 ? 'bg-red-500' : pct > 30 ? 'bg-yellow-500' : 'bg-green-500'
    : pct > 60 ? 'bg-green-500' : pct > 30 ? 'bg-yellow-500' : 'bg-red-500'
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-400">{label}</span>
        <span className="text-white font-medium">{pct}/100</span>
      </div>
      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
        <div className={`h-full ${color} bias-bar`} style={{ width: `${pct}%` }}/>
      </div>
    </div>
  )
}

function IssueList({ title, items, icon }) {
  return (
    <div className="glass rounded-2xl p-5">
      <h3 className="font-medium text-sm text-gray-400 mb-3">{title}</h3>
      {items.length === 0
        ? <p className="text-xs text-gray-600">None</p>
        : items.map(it => (
          <div key={it} className="flex items-center gap-2 py-1 text-sm text-gray-300">
            {icon}<span>{it.replace('_', ' ')}</span>
          </div>
        ))
      }
    </div>
  )
}
