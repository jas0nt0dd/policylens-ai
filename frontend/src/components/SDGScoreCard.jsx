import React from 'react'

const SDG_INFO = {
  1:'No Poverty',2:'Zero Hunger',3:'Good Health',4:'Quality Education',
  5:'Gender Equality',6:'Clean Water',7:'Clean Energy',8:'Decent Work',
  9:'Innovation',10:'Reduced Inequalities',11:'Sustainable Cities',
  12:'Responsible Consumption',13:'Climate Action',14:'Life Below Water',
  15:'Life on Land',16:'Peace & Justice',17:'Partnerships'
}
const SDG_COLORS = {
  1:'#E5243B',2:'#DDA63A',3:'#4C9F38',4:'#C5192D',5:'#FF3A21',
  6:'#26BDE2',7:'#FCC30B',8:'#A21942',9:'#FD6925',10:'#DD1367',
  11:'#FD9D24',12:'#BF8B2E',13:'#3F7E44',14:'#0A97D9',15:'#56C02B',
  16:'#00689D',17:'#19486A'
}

export default function SDGScoreCard({ sdgScores, overallScore }) {
  const scores = Object.entries(sdgScores || {}).map(([key, val]) => ({
    num: parseInt(key.replace('SDG_', '')),
    score: val
  })).sort((a, b) => a.num - b.num)

  return (
    <div>
      {/* Overall */}
      <div className="glass rounded-2xl p-6 mb-6 flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400 mb-1">Overall SDG Compliance</p>
          <p className="text-4xl font-black text-white">{overallScore}<span className="text-xl text-gray-500">/100</span></p>
        </div>
        <div className="relative w-20 h-20">
          <svg viewBox="0 0 80 80" className="w-full h-full -rotate-90">
            <circle cx="40" cy="40" r="34" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="6"/>
            <circle cx="40" cy="40" r="34" fill="none"
              stroke={overallScore > 60 ? '#4ade80' : overallScore > 40 ? '#facc15' : '#f87171'}
              strokeWidth="6"
              strokeDasharray={`${2*Math.PI*34}`}
              strokeDashoffset={`${2*Math.PI*34*(1-overallScore/100)}`}
              strokeLinecap="round"/>
          </svg>
          <span className="absolute inset-0 flex items-center justify-center text-sm font-bold">{overallScore}%</span>
        </div>
      </div>

      {/* SDG grid */}
      <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
        {scores.map(({ num, score }) => (
          <div key={num} className="glass rounded-xl p-3 text-center hover:scale-105 transition-transform cursor-default"
            title={`SDG ${num}: ${SDG_INFO[num]} — Score: ${score}/100`}>
            <div className="w-8 h-8 rounded-lg mx-auto mb-2 flex items-center justify-center text-white text-xs font-bold"
              style={{ backgroundColor: SDG_COLORS[num] || '#555' }}>
              {num}
            </div>
            <div className={`text-sm font-bold ${score > 60 ? 'text-green-400' : score > 40 ? 'text-yellow-400' : 'text-red-400'}`}>
              {score}
            </div>
            <div className="text-xs text-gray-600 leading-tight mt-1 truncate">{SDG_INFO[num]}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
