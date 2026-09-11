import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import AnalyzePage from './pages/AnalyzePage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import BatchPage from './pages/BatchPage.jsx'

function NavBar() {
  const linkClass = ({ isActive }) =>
    `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
      isActive ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100'
    }`

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="max-w-4xl mx-auto px-4 py-3 flex items-center gap-2">
        <span className="font-semibold text-gray-900 mr-4">Content Moderation</span>
        <NavLink to="/" end className={linkClass}>
          Analyze
        </NavLink>
        <NavLink to="/dashboard" className={linkClass}>
          Dashboard
        </NavLink>
        <NavLink to="/batch" className={linkClass}>
          Batch
        </NavLink>
      </div>
    </nav>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <NavBar />
        <main className="max-w-4xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<AnalyzePage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/batch" element={<BatchPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
