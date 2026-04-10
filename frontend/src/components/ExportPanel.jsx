import React, { useState } from 'react'
import { Download, FileJson, Copy, Check } from 'lucide-react'

export default function ExportPanel({ report }) {
  const [copied, setCopied] = useState(false)

  const exportPDF = async () => {
    const { jsPDF } = await import('jspdf')
    const doc = new jsPDF()
    let y = 18
    const pageWidth = 190
    const title = report.document_title || report.document_name

    const ensureSpace = (required = 16) => {
      if (y + required > 280) {
        doc.addPage()
        y = 18
      }
    }

    const addSectionTitle = (label) => {
      ensureSpace(12)
      doc.setFont('helvetica', 'bold')
      doc.setFontSize(14)
      doc.setTextColor(30, 64, 175)
      doc.text(label, 14, y)
      y += 8
    }

    const addParagraph = (text, width = 182, gap = 6) => {
      const lines = doc.splitTextToSize(text || '', width)
      ensureSpace(lines.length * 5 + gap)
      doc.setFont('helvetica', 'normal')
      doc.setFontSize(10)
      doc.setTextColor(40, 40, 40)
      doc.text(lines, 14, y)
      y += lines.length * 5 + gap
    }

    doc.setFillColor(18, 35, 73)
    doc.rect(0, 0, 210, 38, 'F')
    doc.setTextColor(255, 255, 255)
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(20)
    doc.text('PolicyLens AI Report', 14, 16)
    doc.setFontSize(11)
    doc.text('Hidden discrimination and loophole review before policy harm happens', 14, 24)
    doc.setFontSize(10)
    doc.text(title, 14, 32)
    y = 48

    addSectionTitle('Executive Summary')
    addParagraph(`Document: ${title}`)
    addParagraph(`Bias Score: ${report.overall_bias_score}/100 (${report.bias_level})`)
    addParagraph(`SDG Score: ${report.sdg_overall_score}/100`)
    addParagraph(`Impacted groups: ${(report.impacted_groups || []).join(', ') || 'No strong group-level signal detected.'}`)
    addParagraph(report.citizen_summary)

    addSectionTitle('Top Risks')
    ;(report.top_findings || []).slice(0, 5).forEach((finding, index) => {
      ensureSpace(34)
      doc.setDrawColor(220, 227, 240)
      doc.roundedRect(14, y - 2, 182, 28, 3, 3)
      doc.setFont('helvetica', 'bold')
      doc.setFontSize(11)
      doc.setTextColor(18, 35, 73)
      doc.text(`${index + 1}. ${finding.finding_title}`, 18, y + 4)
      doc.setFont('helvetica', 'normal')
      doc.setFontSize(9)
      doc.setTextColor(70, 70, 70)
      const riskLines = doc.splitTextToSize(`Why risky: ${finding.why_risky}`, 170)
      doc.text(riskLines, 18, y + 10)
      const impacted = (finding.impacted_groups || []).join(', ') || 'General public'
      const rewriteLines = doc.splitTextToSize(`Who is harmed: ${impacted}\nSafer rewrite: ${finding.suggested_rewrite}`, 170)
      doc.text(rewriteLines, 18, y + 18)
      y += 34
    })

    addSectionTitle('Clause Evidence Table')
    ;(report.evidence_clauses || []).slice(0, 5).forEach((finding) => {
      const evidenceLines = doc.splitTextToSize(`Clause ${finding.clause_id}: ${finding.exact_clause}`, pageWidth - 12)
      ensureSpace(evidenceLines.length * 4 + 18)
      doc.setFont('helvetica', 'bold')
      doc.setFontSize(10)
      doc.setTextColor(20, 20, 20)
      doc.text(`${finding.clause_id} · ${finding.bias_score}/100 · ${finding.loophole_risk} risk`, 14, y)
      y += 5
      doc.setFont('helvetica', 'normal')
      doc.setFontSize(9)
      doc.setTextColor(70, 70, 70)
      doc.text(evidenceLines, 20, y)
      y += evidenceLines.length * 4 + 4
    })

    addSectionTitle('SDG Snapshot')
    const sortedSdgs = Object.entries(report.sdg_compliance_score || {})
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
    sortedSdgs.forEach(([sdg, score]) => addParagraph(`${sdg}: ${score}/100`, 182, 4))

    addSectionTitle('Recommendations')
    ;(report.recommendations || []).slice(0, 6).forEach((recommendation, index) => {
      addParagraph(`${index + 1}. ${recommendation}`, 182, 4)
    })

    doc.setFontSize(9)
    doc.setTextColor(140, 140, 140)
    doc.text(`Generated ${new Date(report.created_at).toLocaleString()} · Report ID ${report.report_id}`, 14, 288)
    doc.save(`PolicyLens_Report_${title.replace(/\s+/g, '_')}.pdf`)
  }

  const exportJSON = () => {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `PolicyLens_${report.report_id}.json`
    a.click()
  }

  const copyId = () => {
    navigator.clipboard.writeText(report.report_id)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="glass rounded-2xl p-6">
      <h3 className="font-semibold mb-4">Export Report</h3>
      <p className="text-sm text-gray-400 mb-4">
        PDF export now includes an executive summary, top risks, clause evidence, SDG snapshot, and clear recommendations.
      </p>
      <div className="flex flex-wrap gap-3">
        <button onClick={exportPDF}
          className="flex items-center gap-2 px-5 py-2.5 bg-primary-600 hover:bg-primary-500 rounded-xl text-sm font-medium transition-all">
          <Download size={16}/> Download PDF
        </button>
        <button onClick={exportJSON}
          className="flex items-center gap-2 px-5 py-2.5 glass hover:bg-white/10 rounded-xl text-sm font-medium transition-all text-gray-300">
          <FileJson size={16}/> Export JSON
        </button>
        <button onClick={copyId}
          className="flex items-center gap-2 px-5 py-2.5 glass hover:bg-white/10 rounded-xl text-sm font-medium transition-all text-gray-300">
          {copied ? <Check size={16} className="text-green-400"/> : <Copy size={16}/>}
          {copied ? 'Copied!' : 'Copy Report ID'}
        </button>
      </div>
      <p className="text-xs text-gray-600 mt-3">Report ID: <code className="text-gray-400">{report.report_id}</code></p>
    </div>
  )
}
