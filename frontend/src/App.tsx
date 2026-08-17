import { Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import RunDetail from "./pages/RunDetail";
import TraceView from "./pages/TraceView";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="border-b border-gray-800 px-6 py-4">
        <Link to="/" className="text-xl font-bold tracking-tight text-white hover:text-blue-400 transition-colors">
          Multi-Agent Platform
        </Link>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/runs/:id" element={<RunDetail />} />
          <Route path="/runs/:id/traces" element={<TraceView />} />
        </Routes>
      </main>
    </div>
  );
}
