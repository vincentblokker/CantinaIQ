import { Link, Route, Routes } from "react-router-dom";
import Overview from "./pages/Overview";
import Regions from "./pages/Regions";
import Producers from "./pages/Producers";
import Matrix from "./pages/Matrix";

export default function App() {
  return (
    <div className="min-h-screen">
      <header className="border-b border-stone-200 bg-cream">
        <div className="max-w-6xl mx-auto px-6 py-5 flex items-baseline gap-8">
          <h1 className="font-serif text-2xl text-ink">
            CantinaIQ
            <span className="ml-2 text-sm text-ink-2">— Slurpini Partner Intelligence</span>
          </h1>
          <nav className="ml-auto flex gap-6 text-sm">
            <Link to="/" className="hover:text-tuscan">Overview</Link>
            <Link to="/regions" className="hover:text-tuscan">Regions</Link>
            <Link to="/producers" className="hover:text-tuscan">Producers</Link>
            <Link to="/matrix" className="hover:text-tuscan">Matrix</Link>
          </nav>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-6 py-8">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/regions" element={<Regions />} />
          <Route path="/producers" element={<Producers />} />
          <Route path="/matrix" element={<Matrix />} />
        </Routes>
      </main>
    </div>
  );
}
