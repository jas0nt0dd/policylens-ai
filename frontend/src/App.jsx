import React from 'react'
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import Home from './pages/Home'
import Analyze from './pages/Analyze'
import Compare from './pages/Compare'
import { Scale, Search, GitCompare, Moon, Sun } from 'lucide-react'

function Navbar({ dark, setDark }) {
  const loc = useLocation()
  const link = (to, label, Icon) => (
    <Link to={to}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all
        ${loc.pathname === to
          ? 'bg-primary-600 text-white'
          : dark
            ? 'text-gray-300 hover:text-white hover:bg-white/10'
            : 'text-slate-700 hover:text-slate-900 hover:bg-slate-200'}`}>
      <Icon size={16}/>{label}
    </Link>
  )
  return (
    <nav className={`fixed top-0 inset-x-0 z-50 px-6 py-3 transition-colors duration-300
      ${dark ? 'glass border-b border-white/10' : 'bg-white/90 border-b border-slate-200/70 shadow-sm'}`}>
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
            <Scale size={18} className="text-white"/>
          </div>
          <span className={`font-bold tracking-tight ${dark ? 'text-white' : 'text-slate-950'}`}>
            PolicyLens <span className="text-primary-400">AI</span>
          </span>
        </Link>
        <div className="flex items-center gap-2">
          {link('/', 'Home', Scale)}
          {link('/analyze', 'Analyze', Search)}
          {link('/compare', 'Compare', GitCompare)}
          <button onClick={() => setDark(!dark)}
            className={`ml-2 p-2 rounded-lg transition-all ${dark ? 'text-gray-400 hover:text-white hover:bg-white/10' : 'text-slate-600 hover:text-slate-950 hover:bg-slate-200'}`}>
            {dark ? <Sun size={16}/> : <Moon size={16}/>} 
          </button>
        </div>
      </div>
    </nav>
  )
}

export default function App() {
  const [dark, setDark] = React.useState(true)

  React.useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
  }, [dark])

  return (
    <div className={dark ? 'dark' : 'light'}>
      <div className={`min-h-screen transition-colors duration-300 ${dark ? 'bg-gray-950 text-white' : 'bg-slate-50 text-slate-950'}`}>
        <BrowserRouter>
          <Navbar dark={dark} setDark={setDark}/>
          <div className="pt-16">
            <Routes>
              <Route path="/" element={<Home/>}/>
              <Route path="/analyze" element={<Analyze/>}/>
              <Route path="/compare" element={<Compare/>}/>
            </Routes>
          </div>
        </BrowserRouter>
      </div>
    </div>
  )
}
