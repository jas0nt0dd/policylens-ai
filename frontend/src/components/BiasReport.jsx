import React, { useEffect, useState } from 'react'
import api from '../api'
import SDGScoreCard from './SDGScoreCard'
import ClauseHighlighter from './ClauseHighlighter'
import ExportPanel from './ExportPanel'
import { RotateCcw, FileText, Users, BookOpen, ShieldCheck, Sparkles } from 'lucide-react'
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'

const BIAS_COLORS = { LOW: 'text-green-400', MODERATE: 'text-yellow-400', HIGH: 'text-orange-400', CRITICAL: 'text-red-400' }
const BIAS_BG = { LOW: 'border-green-500/30', MODERATE: 'border-yellow-500/30', HIGH: 'border-orange-500/30', CRITICAL: 'border-red-500/30' }

export default function BiasReport({ reportId, onReset }) {
  const [report, setReport] = useState(null)
  const [tab, setTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.get(`/api/report/${reportId}`)
      .then(r => { setReport(r.data); setLoading(false) })
      .catch(e => { setError('Failed to load report.'); setLoading(false) })
  }, [reportId])

  if (loading) return <div className="text-center py-20 text-gray-400 animate-pulse">Loading report...</div>
  if (error) return <div className="text-center py-20 text-red-400">{error}</div>
  if (!report) return null

  const TABS = ['overview', 'clauses', 'sdgs', 'demographics', 'export']

  // Radar data for bias dimensions
  const biasTypes = [...new Set(report.flagged_clauses?.map(c => c.bias_type) || [])]
  const radarData = biasTypes.map(bt => ({
    type: bt.replace('_BIAS', '').replace('_', ' '),
    score: Math.round(report.flagged_clauses.filter(c => c.bias_type === bt).reduce((a, c) => a + c.bias_score, 0) / Math.max(report.flagged_clauses.filter(c => c.bias_type === bt).length, 1))
  }))

  // Demographic bar data
  const demoData = Object.entries(report.demographic_mentions || {})
    .sort(([,a],[,b]) => b - a).slice(0, 10)
    .map(([k, v]) => ({ name: k, mentions: v }))
  const confidence = Math.round(
    (report.top_findings || []).reduce((sum, finding) => sum + (finding.confidence_score || 0), 0)
    / Math.max((report.top_findings || []).length, 1)
  )

  return (
    <div>
      {/* Header */}
      <div className={`glass rounded-2xl p-6 mb-6 border ${BIAS_BG[report.bias_level]}`}>
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <FileText size={20} className="text-primary-400"/>
              <h2 className="font-bold text-lg truncate max-w-xl">{report.document_title || report.document_name}</h2>
            </div>
            <p className="text-sm text-primary-300 mb-2">AI policy review before harm happens.</p>
            <div className="flex flex-wrap gap-3 text-sm">
              <span className="text-gray-500">{report.total_clauses_analyzed} clauses analyzed</span>
              <span className="text-gray-500">·</span>
              <span className="text-gray-500">{report.processing_time_seconds}s processing time</span>
              {report.readability_score && <>
                <span className="text-gray-500">·</span>
                <span className="text-gray-500">Grade {report.readability_score.toFixed(1)} readability</span>
              </>}
            </div>
          </div>
          <button onClick={onReset}
            className="flex items-center gap-2 px-4 py-2 glass rounded-xl text-sm text-gray-400 hover:text-white transition-all">
            <RotateCcw size={14}/> New Analysis
          </button>
        </div>
      </div>

      {/* Score cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <ScoreCard label="Bias Score" value={report.overall_bias_score} invert suffix="/100"
          sub={<span className={`font-bold ${BIAS_COLORS[report.bias_level]}`}>{report.bias_level}</span>}/>
        <ScoreCard label="SDG Compliance" value={report.sdg_overall_score} suffix="/100"/>
        <ScoreCard label="Flagged Clauses" value={report.flagged_clauses?.length || 0}
          sub={<span className="text-gray-500 text-xs">with bias detected</span>}/>
        <ScoreCard label="High Risk" value={report.flagged_clauses?.filter(c => c.loophole_risk === 'HIGH').length || 0}
          sub={<span className="text-gray-500 text-xs">loophole clauses</span>}/>
      </div>

      {/* Tab nav */}
      <div className="flex gap-1 glass rounded-xl p-1 mb-6 overflow-x-auto">
        {TABS.map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all capitalize
              ${tab === t ? 'bg-primary-600 text-white' : 'text-gray-400 hover:text-white'}`}>
            {t}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {tab === 'overview' && (
        <div className="space-y-6">
          <div className="glass rounded-2xl p-6 border border-primary-500/20">
            <div className="flex items-start gap-3">
              <ShieldCheck size={20} className="text-primary-400 mt-0.5"/>
              <div>
                <h3 className="font-semibold mb-1">What this report is doing</h3>
                <p className="text-sm text-gray-300 leading-relaxed">
                  PolicyLens is looking for clause-level discrimination, vague discretion, weak appeal rights,
                  and SDG misalignment so citizens, NGOs, and policymakers can review the text before it causes harm.
                </p>
              </div>
            </div>
          </div>

          {/* Citizen summary */}
          <div className="glass rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-3">
              <BookOpen size={18} className="text-primary-400"/>
              <h3 className="font-semibold">Citizen Summary</h3>
              <span className="text-xs glass px-2 py-0.5 rounded-full text-gray-400 ml-auto">{report.language.toUpperCase()}</span>
            </div>
            <p className="text-gray-300 leading-relaxed">{report.citizen_summary}</p>
            <p className="text-xs text-gray-500 mt-3">Summary status: {report.translation_status.replaceAll('_', ' ')}</p>
          </div>

          {(report.top_findings || []).length > 0 && (
            <div className="glass rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <Sparkles size={18} className="text-primary-400"/>
                <h3 className="font-semibold">Top 5 Flagged Clauses</h3>
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                {report.top_findings.slice(0, 5).map((finding) => (
                  <div key={finding.clause_id} className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-center justify-between gap-3 mb-2">
                      <p className="font-medium text-white">{finding.finding_title}</p>
                      <span className="text-xs text-gray-500">{finding.bias_score}/100</span>
                    </div>
                    <p className="text-xs text-gray-500 font-mono mb-2">{finding.clause_id}</p>
                    <p className="text-sm text-gray-300 leading-relaxed mb-3">{finding.why_risky}</p>
                    {finding.impacted_groups?.length > 0 && (
                      <p className="text-xs text-primary-300 mb-3">
                        Harmed groups: {finding.impacted_groups.join(', ')}
                      </p>
                    )}
                    <div className="rounded-lg bg-primary-500/10 border border-primary-500/20 p-3">
                      <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Safer Rewrite</p>
                      <p className="text-sm text-gray-200 leading-relaxed">{finding.suggested_rewrite}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-6">
            <div className="glass rounded-2xl p-6">
              <h3 className="font-semibold mb-4">Why This Report Is Credible</h3>
              <div className="space-y-3 text-sm text-gray-300">
                <p>Evidence-backed findings use exact clause text, matched signals, and policy-specific rewrite suggestions.</p>
                <p>Confidence score: <span className="text-primary-300 font-semibold">{confidence || 0}/100</span></p>
                <p>Impacted groups: {(report.impacted_groups || []).length > 0 ? report.impacted_groups.join(', ') : 'No strongly affected groups inferred.'}</p>
              </div>
            </div>
            <div className="glass rounded-2xl p-6">
              <h3 className="font-semibold mb-4">How The AI Reached This Report</h3>
              <div className="space-y-2 text-sm text-gray-300">
                <p>1. Parse the policy into clauses.</p>
                <p>2. Detect exclusion, loopholes, and procedural unfairness.</p>
                <p>3. Map clauses to SDGs and impacted groups.</p>
                <p>4. Rewrite flagged clauses into safer, plainer language.</p>
              </div>
            </div>
          </div>

          {/* Bias radar */}
          {radarData.length > 2 && (
            <div className="glass rounded-2xl p-6">
              <h3 className="font-semibold mb-4">Bias Dimension Radar</h3>
              <ResponsiveContainer width="100%" height={250}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="rgba(255,255,255,0.1)"/>
                  <PolarAngleAxis dataKey="type" tick={{ fill: '#9ca3af', fontSize: 11 }}/>
                  <Radar dataKey="score" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3}/>
                </RadarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Recommendations */}
          {report.recommendations?.length > 0 && (
            <div className="glass rounded-2xl p-6">
              <h3 className="font-semibold mb-4">Top Recommendations</h3>
              <ul className="space-y-2">
                {report.recommendations.slice(0, 6).map((r, i) => (
                  <li key={i} className="flex gap-3 text-sm text-gray-300">
                    <span className="text-primary-400 font-bold mt-0.5">{i + 1}.</span>
                    <span className="leading-relaxed">{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {tab === 'clauses' && (
        <ClauseHighlighter clauses={report.flagged_clauses || []}/>
      )}

      {tab === 'sdgs' && (
        <SDGScoreCard sdgScores={report.sdg_compliance_score} overallScore={report.sdg_overall_score}/>
      )}

      {tab === 'demographics' && (
        <div className="glass rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-6">
            <Users size={18} className="text-primary-400"/>
            <h3 className="font-semibold">Demographic Group Mentions</h3>
          </div>
          {demoData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={demoData} layout="vertical">
                <XAxis type="number" tick={{ fill: '#9ca3af', fontSize: 11 }}/>
                <YAxis dataKey="name" type="category" tick={{ fill: '#9ca3af', fontSize: 11 }} width={100}/>
                <Tooltip contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }}/>
                <Bar dataKey="mentions" fill="#3b82f6" radius={[0,4,4,0]}/>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-8">No demographic mentions detected.</p>
          )}
        </div>
      )}

      {tab === 'export' && (
        <ExportPanel report={report}/>
      )}
    </div>
  )
}

function ScoreCard({ label, value, suffix, sub, invert }) {
  const pct = Math.min(Number(value) || 0, 100)
  const color = invert
    ? pct > 60 ? 'text-red-400' : pct > 30 ? 'text-yellow-400' : 'text-green-400'
    : pct > 60 ? 'text-green-400' : pct > 30 ? 'text-yellow-400' : 'text-red-400'
  return (
    <div className="glass rounded-2xl p-5">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className={`text-3xl font-black ${color}`}>{value}<span className="text-sm text-gray-500">{suffix}</span></p>
      {sub && <div className="mt-1 text-xs">{sub}</div>}
    </div>
  )
}
