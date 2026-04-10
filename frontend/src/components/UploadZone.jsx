import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Link2, FileText, AlertCircle } from 'lucide-react'

const LANGUAGES = [
  { code: 'en', label: 'English' }, { code: 'hi', label: 'Hindi' },
  { code: 'ta', label: 'Tamil' }, { code: 'fr', label: 'French' },
  { code: 'es', label: 'Spanish' }, { code: 'ar', label: 'Arabic' },
]

export default function UploadZone({ onAnalyze, language, setLanguage, error }) {
  const [file, setFile] = useState(null)
  const [url, setUrl] = useState('')
  const [mode, setMode] = useState('file') // 'file' | 'url'

  const onDrop = useCallback(accepted => {
    if (accepted[0]) setFile(accepted[0])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'], 'text/plain': ['.txt'] },
    maxFiles: 1
  })

  const canSubmit = mode === 'file' ? !!file : url.trim().length > 10

  return (
    <div className="space-y-6">
      {/* Mode toggle */}
      <div className="flex gap-2 glass rounded-xl p-1 w-fit">
        {['file', 'url'].map(m => (
          <button key={m} onClick={() => setMode(m)}
            className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${mode === m ? 'bg-primary-600 text-white' : 'text-gray-400 hover:text-white'}`}>
            {m === 'file' ? '📎 Upload File' : '🔗 Paste URL'}
          </button>
        ))}
      </div>

      {mode === 'file' ? (
        <div {...getRootProps()}
          className={`glass rounded-2xl p-16 text-center cursor-pointer transition-all
            ${isDragActive ? 'border-primary-500 bg-primary-500/10' : 'hover:border-primary-500/50 hover:bg-white/5'}`}>
          <input {...getInputProps()}/>
          <Upload size={48} className="mx-auto mb-4 text-primary-400"/>
          {file ? (
            <div>
              <div className="flex items-center justify-center gap-2 text-green-400 font-medium mb-1">
                <FileText size={18}/>{file.name}
              </div>
              <p className="text-sm text-gray-500">{(file.size/1024/1024).toFixed(2)} MB · Click or drop to replace</p>
            </div>
          ) : (
            <>
              <p className="text-lg font-medium text-white mb-2">
                {isDragActive ? 'Drop it here!' : 'Drag & drop your policy document'}
              </p>
              <p className="text-sm text-gray-500">PDF, DOCX, or TXT · Up to 50MB</p>
            </>
          )}
        </div>
      ) : (
        <div className="glass rounded-2xl p-8">
          <label className="text-sm text-gray-400 mb-3 block">Policy Document URL</label>
          <input value={url} onChange={e => setUrl(e.target.value)}
            placeholder="https://example.gov/policy-document.pdf"
            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-primary-500 font-mono text-sm"/>
          <p className="text-xs text-gray-600 mt-2">Supports direct PDF links and web pages with policy text.</p>
        </div>
      )}

      {/* Language selector */}
      <div className="glass rounded-2xl p-6">
        <label className="text-sm text-gray-400 mb-3 block">Output Language for Citizen Summary</label>
        <div className="flex flex-wrap gap-2">
          {LANGUAGES.map(l => (
            <button key={l.code} onClick={() => setLanguage(l.code)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all
                ${language === l.code ? 'bg-primary-600 text-white' : 'glass text-gray-400 hover:text-white'}`}>
              {l.label}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 glass rounded-xl px-4 py-3 text-red-400 border border-red-500/20">
          <AlertCircle size={18}/>{error}
        </div>
      )}

      <button onClick={() => onAnalyze(file, url)} disabled={!canSubmit}
        className="w-full py-4 rounded-xl bg-primary-600 hover:bg-primary-500 font-semibold text-white transition-all hover:scale-[1.01] disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100 text-lg shadow-lg shadow-primary-900/50">
        Analyze Document →
      </button>

      <p className="text-center text-xs text-gray-600">
        Open-source and local-first · Optional translation / LLM fallbacks can be enabled when configured
      </p>
    </div>
  )
}
