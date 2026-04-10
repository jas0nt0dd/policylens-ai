import React from 'react'
import { Link } from 'react-router-dom'
import { Scale, Shield, Globe, Zap, FileText, BarChart2, Languages, Download, Users, Landmark, ClipboardCheck } from 'lucide-react'

const FEATURES = [
  { icon: Shield, title: 'Bias Detection', desc: '5-dimension AI engine detects gender, ethnic, caste, regional, and socioeconomic bias in every clause.', color: 'text-red-400' },
  { icon: Globe, title: 'SDG Compliance', desc: 'Auto-scores your policy against all 17 UN Sustainable Development Goals with evidence citations.', color: 'text-green-400' },
  { icon: FileText, title: 'Loophole Flags', desc: 'Identifies vague language that could enable corruption or misinterpretation before enactment.', color: 'text-yellow-400' },
  { icon: Languages, title: 'Multilingual', desc: 'Translates citizen summaries into Hindi, Tamil, French, Spanish, and Arabic via LibreTranslate.', color: 'text-blue-400' },
  { icon: BarChart2, title: 'Interactive Reports', desc: 'Visual dashboards with clause-level highlighting, SDG scorecards, and demographic equity charts.', color: 'text-purple-400' },
  { icon: Download, title: 'Export PDF', desc: 'Download a complete audit report as a shareable PDF for NGOs, courts, or public records.', color: 'text-cyan-400' },
]

const STATS = [
  { value: '100%', label: 'Open Source' },
  { value: '<90s', label: 'Analysis Time' },
  { value: '17', label: 'SDGs Checked' },
  { value: '$0', label: 'Cost per Analysis' },
]

const USERS = [
  { icon: Users, title: 'Citizens & Activists', desc: 'Understand legal text in plain language and see exactly which clauses create harm.' },
  { icon: ClipboardCheck, title: 'NGOs & Legal Aid Teams', desc: 'Triage risky policies faster with clause-backed evidence and safer rewrite suggestions.' },
  { icon: Landmark, title: 'Policymakers', desc: 'Redraft exclusionary provisions before publication, litigation, or public backlash.' },
]

const VALIDATION = [
  { value: '10/10', label: 'flag vs no-flag benchmark' },
  { value: '10/10', label: 'bias-type match' },
  { value: '10/10', label: 'severity threshold match' },
  { value: '10/10', label: 'impacted-group coverage' },
]

export default function Home() {
  return (
    <main>
      {/* Hero */}
      <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden px-6">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-900/40 via-gray-950 to-accent-900/20"/>
        <div className="absolute top-20 left-1/4 w-96 h-96 bg-primary-600/10 rounded-full blur-3xl"/>
        <div className="absolute bottom-20 right-1/4 w-80 h-80 bg-accent-600/10 rounded-full blur-3xl"/>
        <div className="relative text-center max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass text-sm text-primary-300 mb-6">
            <Zap size={14} className="text-yellow-400"/>
            AI Tool Development Challenge 2.0 · OneEarth Theme · SDG 16
          </div>
          <h1 className="text-6xl font-black mb-6 leading-tight">
            Upload any policy draft.<br/>
            <span className="bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">
              Expose hidden bias before harm happens.
            </span>
          </h1>
          <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
            PolicyLens helps detect hidden discrimination and loopholes in public policy before the policy reaches people. It surfaces clause-level evidence, safer rewrites, and citizen-friendly summaries in under 90 seconds.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link to="/analyze"
              className="px-8 py-4 rounded-xl bg-primary-600 hover:bg-primary-500 font-semibold text-white transition-all hover:scale-105 shadow-lg shadow-primary-900/50">
              Analyze a Policy →
            </Link>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer"
              className="px-8 py-4 rounded-xl glass font-semibold text-gray-300 hover:text-white transition-all hover:scale-105">
              View on GitHub
            </a>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 px-6">
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
          {STATS.map(s => (
            <div key={s.label} className="glass rounded-2xl p-6 text-center">
              <div className="text-4xl font-black bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">{s.value}</div>
              <div className="text-sm text-gray-400 mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Why Judges Can Trust It</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map(f => (
              <div key={f.title} className="glass rounded-2xl p-6 hover:border-primary-500/40 transition-all group">
                <f.icon size={28} className={`${f.color} mb-4 group-hover:scale-110 transition-transform`}/>
                <h3 className="font-semibold text-white mb-2">{f.title}</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 px-6 bg-white/2">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Built For The People Who Need It Most</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {USERS.map((user) => (
              <div key={user.title} className="glass rounded-2xl p-6">
                <user.icon size={28} className="text-primary-400 mb-4"/>
                <h3 className="font-semibold text-white mb-2">{user.title}</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{user.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">Validation Snapshot</h2>
          <p className="text-center text-gray-400 mb-10">
            PolicyLens ships with a small manually labeled benchmark suite so teams can prove the detector catches seeded bias cases before demo day.
          </p>
          <div className="grid md:grid-cols-4 gap-4">
            {VALIDATION.map((metric) => (
              <div key={metric.label} className="glass rounded-2xl p-5 text-center">
                <div className="text-3xl font-black text-primary-300">{metric.value}</div>
                <div className="text-sm text-gray-400 mt-2">{metric.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pipeline visual */}
      <section className="py-16 px-6 bg-white/2">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">How It Works</h2>
          <p className="text-gray-400 mb-12">Upload → Reveal risky clauses → Rewrite for fairness → Export evidence-backed report</p>
          <div className="flex flex-wrap justify-center items-center gap-3">
            {['Upload Draft','Parse Clauses','Detect Exclusion','Score SDGs','Generate Safer Rewrite','Export Report'].map((step, i) => (
              <React.Fragment key={step}>
                <div className="glass rounded-xl px-5 py-3 text-sm font-medium text-white">
                  <span className="text-primary-400 font-bold mr-2">{i+1}.</span>{step}
                </div>
                {i < 5 && <span className="text-gray-600 text-lg">→</span>}
              </React.Fragment>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6 text-center">
        <div className="max-w-2xl mx-auto glass rounded-3xl p-12">
          <Scale size={48} className="text-primary-400 mx-auto mb-6"/>
          <h2 className="text-3xl font-bold mb-4">One planet. One purpose. Powered by AI.</h2>
          <p className="text-gray-400 mb-8">PolicyLens turns policy review into something explainable, evidence-backed, and accessible to every citizen, NGO, and policymaker.</p>
          <Link to="/analyze" className="px-8 py-4 rounded-xl bg-primary-600 hover:bg-primary-500 font-semibold text-white transition-all hover:scale-105 inline-block">
            Start Your First Analysis →
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-white/10 text-center text-sm text-gray-600">
        PolicyLens AI · Cifer Troop · Kathir College of Engineering · AI Tool Development Challenge 2.0
      </footer>
    </main>
  )
}
