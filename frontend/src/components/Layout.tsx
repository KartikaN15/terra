import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  SquaresFour,
  FilmSlate,
  UploadSimple,
  Database,
  Gear,
  MagnifyingGlass,
  Leaf,
  CaretDown,
  SignOut,
  User,
  TrendUp,
  WarningCircle,
} from "@phosphor-icons/react";
import cityVignette from "../assets/illustrations/city-vignette.png";
import { useAuth } from "../contexts/AuthContext";
import NotificationCenter from "./NotificationCenter";

const PAGE_TITLES: Record<string, { title: string; subtitle: string }> = {
  "/": { title: "Dashboard", subtitle: "Your sustainability cockpit at a glance" },
  "/productions": { title: "Productions", subtitle: "Every title you're tracking" },
  "/forecast": { title: "Greenlight Forecast", subtitle: "Predict emissions before you shoot" },
  "/anomalies": { title: "Anomalies", subtitle: "Outliers flagged by Terra's engine" },
  "/documents": { title: "Documents", subtitle: "Upload, extract & review receipts" },
  "/upload": { title: "Upload CSV", subtitle: "Bulk import activity events" },
  "/factors": { title: "Emission Factors", subtitle: "Reference library & versions" },
  "/settings": { title: "Settings", subtitle: "Workspace preferences" },
};

function getPageMeta(pathname: string) {
  if (pathname.startsWith("/productions/")) {
    return { title: "Production detail", subtitle: "Footprint breakdown & events" };
  }
  return PAGE_TITLES[pathname] ?? { title: "Terra", subtitle: "" };
}

const nav = [
  {
    section: "GENERAL",
    items: [
      { path: "/", label: "Dashboard", icon: SquaresFour },
      { path: "/productions", label: "Productions", icon: FilmSlate },
    ],
  },
  {
    section: "DATA",
    items: [
      { path: "/forecast", label: "Greenlight", icon: TrendUp },
      { path: "/anomalies", label: "Anomalies", icon: WarningCircle },
      { path: "/documents", label: "Documents", icon: UploadSimple },
      { path: "/upload", label: "Upload CSV", icon: UploadSimple },
      { path: "/factors", label: "Emission Factors", icon: Database },
    ],
  },
  {
    section: "SETTINGS",
    items: [{ path: "/settings", label: "Settings", icon: Gear }],
  },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const loc = useLocation();
  const navigate = useNavigate();
  const meta = getPageMeta(loc.pathname);
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-60 shrink-0 p-4 sticky top-0 self-start h-screen">
        <div className="terra-card h-full p-4 flex flex-col overflow-y-auto sidebar-scroll">
          <div className="flex items-center gap-2 px-2 py-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-sm">
              <Leaf weight="fill" className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-slate-800 text-lg tracking-tight">
              Terra
            </span>
          </div>

          <nav className="mt-4 space-y-6 flex-1">
            {nav.map((group) => (
              <div key={group.section}>
                <div className="text-[10px] font-semibold tracking-wider text-slate-400 px-2 mb-2">
                  {group.section}
                </div>
                <div className="space-y-1">
                  {group.items.map((n) => {
                    const active =
                      n.path === "/"
                        ? loc.pathname === "/"
                        : loc.pathname.startsWith(n.path);
                    return (
                      <Link
                        key={n.path}
                        to={n.path}
                        className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                          active
                            ? "bg-emerald-50 text-emerald-700"
                            : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                        }`}
                      >
                        <n.icon
                          weight={active ? "duotone" : "regular"}
                          className="w-5 h-5"
                        />
                        {n.label}
                      </Link>
                    );
                  })}
                </div>
              </div>
            ))}
          </nav>

          <div className="mt-4 rounded-xl bg-gradient-to-br from-emerald-100 via-emerald-50 to-amber-50 p-4 border border-emerald-100 overflow-hidden relative">
            <div className="relative h-20 flex items-center justify-center">
              <img
                src={cityVignette}
                alt=""
                className="h-28 object-contain illus-shadow-soft"
              />
            </div>
            <div className="text-sm font-semibold text-emerald-900 mt-2">
              Upgrade to Pro
            </div>
            <p className="text-xs text-emerald-800/70 mt-1 leading-snug">
              Unlock anomaly detection & team collaboration.
            </p>
            <button className="mt-3 w-full bg-emerald-600 text-white text-xs font-semibold py-2 rounded-md hover:bg-emerald-700 shadow-sm shadow-emerald-600/20">
              Upgrade
            </button>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 min-w-0 flex flex-col">
        <header className="px-6 pt-4">
          <div className="terra-card px-4 py-3 flex items-center gap-4">
            {/* Left: page title */}
            <div className="min-w-0 flex-shrink">
              <h1 className="text-base font-semibold text-slate-900 tracking-tight truncate">
                {meta.title}
              </h1>
              {meta.subtitle && (
                <p className="text-xs text-slate-500 truncate">{meta.subtitle}</p>
              )}
            </div>

            {/* Middle: search */}
            <div className="hidden md:flex flex-1 justify-center min-w-0">
              <div className="flex items-center gap-2 w-full max-w-md min-w-0 bg-slate-50 hover:bg-slate-100 focus-within:bg-white focus-within:ring-2 focus-within:ring-emerald-100 focus-within:border-emerald-300 border border-transparent rounded-lg px-3 py-2 transition">
                <MagnifyingGlass className="w-4 h-4 text-slate-400 shrink-0" />
                <input
                  type="search"
                  className="bg-transparent outline-none text-sm flex-1 min-w-0 placeholder:text-slate-400"
                  placeholder="Search productions, events…"
                  aria-label="Search"
                />
                <kbd className="hidden lg:inline-flex text-[10px] font-mono text-slate-400 border border-slate-200 rounded px-1.5 py-0.5 bg-white">
                  ⌘K
                </kbd>
              </div>
            </div>

            {/* Right: actions */}
            <div className="ml-auto flex items-center gap-2 shrink-0">
              <NotificationCenter />

              {user ? (
                <div className="flex items-center gap-2">
                  <button
                    aria-label="Open user menu"
                    className="flex items-center gap-2 pl-2 pr-2.5 py-1 rounded-lg hover:bg-slate-100 transition"
                  >
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center text-white text-xs font-semibold shrink-0">
                      {(user.full_name || user.email).charAt(0).toUpperCase()}
                    </div>
                    <div className="hidden sm:block text-left leading-tight max-w-[140px]">
                      <div className="text-sm font-medium text-slate-800 truncate">
                        {user.full_name || user.email.split("@")[0]}
                      </div>
                      <div className="text-xs text-slate-500 truncate">
                        {user.email}
                      </div>
                    </div>
                    <CaretDown
                      weight="bold"
                      className="w-3 h-3 text-slate-400 hidden sm:block"
                    />
                  </button>
                  <button
                    aria-label="Logout"
                    onClick={() => { logout(); navigate("/login"); }}
                    className="p-2 rounded-lg hover:bg-slate-100 transition text-slate-500 hover:text-slate-700"
                    title="Logout"
                  >
                    <SignOut className="w-5 h-5" />
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => navigate("/login")}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-700 transition"
                >
                  <User className="w-4 h-4" />
                  Login
                </button>
              )}
            </div>
          </div>
        </header>

        <main className="flex-1 px-6 pt-5 pb-8 min-w-0">{children}</main>
      </div>
    </div>
  );
}
