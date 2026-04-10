import React, { useState, useCallback } from 'react'
import UploadZone from '../components/UploadZone'
import AnalysisProgress from '../components/AnalysisProgress'
import BiasReport from '../components/BiasReport'
import api from '../api'

const STAGES = [
  'Parsing document',
  'Semantic analysis',
  'Detecting bias',
  'SDG classification',
  'LLM deep analysis',
  'Complete',
]

export default function Analyze() {
  const [phase, setPhase] = useState('upload') // upload | processing | done
  const [taskId, setTaskId] = useState(null)
  const [progress, setProgress] = useState(0)
  const [stage, setStage] = useState('')
  const [reportId, setReportId] = useState(null)
  const [error, setError] = useState(null)
  const [language, setLanguage] = useState('en')

  const handleUpload = useCallback(async (file, url) => {
    setError(null)
    setPhase('processing')
    try {
      const form = new FormData()
      if (file) form.append('file', file)
      if (url) form.append('url', url)
      form.append('language_output', language)

      const { data } = await api.post('/api/analyze', form)
      setTaskId(data.task_id)
      pollStatus(data.task_id)
    } catch (e) {
      setError(e.response?.data?.detail || 'Upload failed. Is the backend running?')
      setPhase('upload')
    }
  }, [language])

  const pollStatus = (tid) => {
    let failureCount = 0
    const iv = setInterval(async () => {
      try {
        const { data } = await api.get(`/api/status/${tid}`)
        failureCount = 0
        setProgress(data.progress)
        setStage(data.stage || '')
        if (data.status === 'completed') {
          clearInterval(iv)
          setReportId(data.result_id)
          setPhase('done')
        } else if (data.status === 'failed') {
          clearInterval(iv)
          setError(data.error || 'Analysis failed. Check backend logs.')
          setPhase('upload')
        }
      } catch {
        failureCount += 1
        if (failureCount >= 3) {
          clearInterval(iv)
          setError('Lost connection while checking analysis status. Please try again.')
          setPhase('upload')
        }
      }
    }, 1500)
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <div className="mb-10">
        <h1 className="text-4xl font-black mb-2">Analyze Policy</h1>
        <p className="text-gray-400">Upload a PDF or paste a document URL to start AI-powered analysis.</p>
      </div>

      {phase === 'upload' && (
        <UploadZone onAnalyze={handleUpload} language={language} setLanguage={setLanguage} error={error}/>
      )}
      {phase === 'processing' && (
        <AnalysisProgress progress={progress} stage={stage} stages={STAGES}/>
      )}
      {phase === 'done' && reportId && (
        <BiasReport reportId={reportId} onReset={() => { setPhase('upload'); setReportId(null); setProgress(0) }}/>
      )}
    </div>
  )
}
