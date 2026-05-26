import { Link, NavLink, Route, Routes, useLocation } from "react-router-dom";
import { useEffect } from "react";
import Overview from "./pages/Overview";
import Recommendation from "./pages/Recommendation";
import Regions from "./pages/Regions";
import Producers from "./pages/Producers";
import Matrix from "./pages/Matrix";
import Bias from "./pages/Bias";
import Stability from "./pages/Stability";
import Methodology from "./pages/Methodology";
import ForEvaluators from "./pages/ForEvaluators";
import Wines from "./pages/Wines";

const NAV_ITEMS = [
  { to: "/", label: "Overview", end: true },
  { to: "/recommendation", label: "Recommendation" },
  { to: "/matrix", label: "Matrix" },
  { to: "/wines", label: "Wines" },
  { to: "/regions", label: "Regions" },
  { to: "/producers", label: "Producers" },
  { to: "/bias", label: "Bias" },
  { to: "/stability", label: "Stability" },
  { to: "/methodology", label: "Methodology" },
];

const PAGE_LABEL: Record<string, string> = {
  "/recommendation": "Recommendation",
  "/matrix": "Opportunity Matrix",
  "/wines": "Wines",
  "/regions": "Regions",
  "/producers": "Producers",
  "/bias": "Bias",
  "/stability": "Stability",
  "/methodology": "Methodology",
  "/for-evaluators": "For Evaluators",
};

const navLink = ({ isActive }: { isActive: boolean }) =>
  `relative pb-1 transition-colors ${
    isActive
      ? "text-tuscan font-semibold after:absolute after:left-0 after:right-0 after:-bottom-0.5 after:h-0.5 after:bg-tuscan after:rounded-full"
      : "text-ink-2 hover:text-tuscan"
  }`;

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
}

function Breadcrumb() {
  const { pathname } = useLocation();
  if (pathname === "/") return null;
  const label = PAGE_LABEL[pathname] ?? pathname.replace("/", "");
  return (
    <div className="bg-stone-50 border-b border-stone-200">
      <div className="max-w-6xl mx-auto px-6 py-3 flex items-center gap-2 text-sm">
        <Link
          to="/"
          className="text-tuscan font-semibold hover:underline inline-flex items-center gap-1"
        >
          <span aria-hidden>←</span> Overview
        </Link>
        <span className="text-stone-400" aria-hidden>/</span>
        <span className="text-ink-2">{label}</span>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <div className="min-h-screen">
      <ScrollToTop />
      <header className="sticky top-0 z-40 border-b border-stone-200 bg-cream/95 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-baseline gap-8 flex-wrap">
          <Link to="/" className="font-serif text-2xl text-ink hover:text-tuscan transition-colors">
            CantinaIQ
            <span className="ml-2 text-sm text-ink-2 font-sans">— Slurpini Partner Intelligence</span>
          </Link>
          <nav className="ml-auto flex items-baseline gap-x-5 gap-y-2 text-sm flex-wrap">
            {NAV_ITEMS.map((item) => (
              <NavLink key={item.to} to={item.to} end={item.end} className={navLink}>
                {item.label}
              </NavLink>
            ))}
            <NavLink
              to="/for-evaluators"
              className={({ isActive }) =>
                `relative px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider transition-colors border ${
                  isActive
                    ? "bg-tuscan text-white border-tuscan"
                    : "border-tuscan/40 text-tuscan hover:bg-tuscan/10"
                }`
              }
            >
              For Evaluators
            </NavLink>
          </nav>
        </div>
      </header>
      <Breadcrumb />
      <main key={useLocation().pathname} className="page-enter max-w-6xl mx-auto px-6 py-8">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/recommendation" element={<Recommendation />} />
          <Route path="/regions" element={<Regions />} />
          <Route path="/producers" element={<Producers />} />
          <Route path="/matrix" element={<Matrix />} />
          <Route path="/bias" element={<Bias />} />
          <Route path="/stability" element={<Stability />} />
          <Route path="/methodology" element={<Methodology />} />
          <Route path="/wines" element={<Wines />} />
          <Route path="/for-evaluators" element={<ForEvaluators />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

function Footer() {
  return (
    <footer className="border-t border-stone-200 bg-stone-50 mt-12">
      <div className="max-w-6xl mx-auto px-6 py-6 flex items-baseline gap-6 flex-wrap text-xs text-ink-2">
        <span className="font-semibold text-ink">CantinaIQ</span>
        <span>·</span>
        <Link to="/" className="hover:text-tuscan">Overview</Link>
        <Link to="/recommendation" className="hover:text-tuscan">Recommendation</Link>
        <Link to="/for-evaluators" className="hover:text-tuscan">For Evaluators</Link>
        <span className="ml-auto">
          <a
            href="https://github.com/vincentblokker/CantinaIQ"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-tuscan"
          >
            github.com/vincentblokker/CantinaIQ
          </a>
        </span>
      </div>
    </footer>
  );
}
