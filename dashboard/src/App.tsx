import { NavLink, Route, Routes } from "react-router-dom";
import Overview from "./pages/Overview";
import Recommendation from "./pages/Recommendation";
import Regions from "./pages/Regions";
import Producers from "./pages/Producers";
import Matrix from "./pages/Matrix";
import Bias from "./pages/Bias";
import Stability from "./pages/Stability";
import Methodology from "./pages/Methodology";

const navLink = ({ isActive }: { isActive: boolean }) =>
  `transition-colors ${isActive ? "text-tuscan font-semibold" : "text-ink-2 hover:text-tuscan"}`;

export default function App() {
  return (
    <div className="min-h-screen">
      <header className="border-b border-stone-200 bg-cream">
        <div className="max-w-6xl mx-auto px-6 py-5 flex items-baseline gap-8 flex-wrap">
          <h1 className="font-serif text-2xl text-ink">
            CantinaIQ
            <span className="ml-2 text-sm text-ink-2">— Slurpini Partner Intelligence</span>
          </h1>
          <nav className="ml-auto flex gap-5 text-sm flex-wrap">
            <NavLink to="/" end className={navLink}>Overview</NavLink>
            <NavLink to="/recommendation" className={navLink}>Recommendation</NavLink>
            <NavLink to="/matrix" className={navLink}>Matrix</NavLink>
            <NavLink to="/regions" className={navLink}>Regions</NavLink>
            <NavLink to="/producers" className={navLink}>Producers</NavLink>
            <NavLink to="/bias" className={navLink}>Bias</NavLink>
            <NavLink to="/stability" className={navLink}>Stability</NavLink>
            <NavLink to="/methodology" className={navLink}>Methodology</NavLink>
          </nav>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-6 py-8">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/recommendation" element={<Recommendation />} />
          <Route path="/regions" element={<Regions />} />
          <Route path="/producers" element={<Producers />} />
          <Route path="/matrix" element={<Matrix />} />
          <Route path="/bias" element={<Bias />} />
          <Route path="/stability" element={<Stability />} />
          <Route path="/methodology" element={<Methodology />} />
        </Routes>
      </main>
    </div>
  );
}
