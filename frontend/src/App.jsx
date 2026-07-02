import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import CandidateDetail from './pages/CandidateDetail';
import Analytics from './pages/Analytics';
import Compare from './pages/Compare';
import CopilotChat from './components/CopilotChat';
import { Home, BarChart2, Users } from 'lucide-react';

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-background text-slate-100 overflow-hidden font-sans">
        {/* Sidebar */}
        <nav className="w-64 bg-surface border-r border-slate-700 flex flex-col p-4 space-y-4">
          <div className="font-bold text-xl text-primary mb-8 tracking-wide">Intelligent Platform</div>
          <Link to="/" className="flex items-center space-x-3 text-slate-300 hover:text-white p-2 rounded-lg hover:bg-slate-700 transition"><Home size={20}/> <span>Dashboard</span></Link>
          <Link to="/analytics" className="flex items-center space-x-3 text-slate-300 hover:text-white p-2 rounded-lg hover:bg-slate-700 transition"><BarChart2 size={20}/> <span>Analytics</span></Link>
          <Link to="/compare" className="flex items-center space-x-3 text-slate-300 hover:text-white p-2 rounded-lg hover:bg-slate-700 transition"><Users size={20}/> <span>Compare</span></Link>
        </nav>
        
        {/* Main Content */}
        <main className="flex-1 overflow-auto relative">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/candidate/:id" element={<CandidateDetail />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/compare" element={<Compare />} />
          </Routes>
        </main>
        
        {/* Global Copilot Widget */}
        <CopilotChat />
      </div>
    </Router>
  )
}

export default App;
