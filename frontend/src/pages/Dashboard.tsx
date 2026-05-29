import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Leaf,
  ArrowRight,
} from "@phosphor-icons/react";
import heroPlanet from "../assets/illustrations/hero-planet.png";
import leafSwirl from "../assets/illustrations/leaf-swirl.png";
import kpiCarbon from "../assets/illustrations/kpi_carbon_vignette.png";
import kpiConfidence from "../assets/illustrations/kpi_confidence_vignette.png";
import kpiAnomalies from "../assets/illustrations/kpi_anomalies_vignette.png";
import kpiProductions from "../assets/illustrations/kpi_productions_vignette.png";
import {
  BarChart,
  Bar,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { ChartTooltip, PieTooltip } from "../components/ChartTooltip";
import { api, type Production, type ProductionSummary } from "../api";
import { CircleNotch as Loader2 } from "@phosphor-icons/react";

const SCOPE_COLORS: Record<string, string> = {
  SCOPE_1: "#10b981",
  SCOPE_2: "#34d399",
  SCOPE_3: "#f59e0b",
};

function KPI({
  label,
  value,
  unit,
  delta,
  positive,
  illustration,
  featured = false,
}: {
  label: string;
  value: string;
  unit?: string;
  delta: string;
  positive: boolean;
  illustration: string;
  featured?: boolean;
}) {
  return (
    <div className={`terra-card p-5 relative overflow-hidden group hover:shadow-xl transition-all duration-300 ${featured ? "terra-tile-emerald" : ""}`}>
      <div className="relative z-10">
        <div className="flex items-center justify-between">
          <div className={`text-sm font-medium ${featured ? "text-emerald-50" : "text-slate-500"}`}>{label}</div>
        </div>
        <div className="mt-3 flex items-end gap-1">
          <div className={`text-3xl font-black tracking-tight ${featured ? "text-white" : "text-slate-900"}`}>{value}</div>
          {unit && <div className={`text-xs font-bold mb-1.5 ${featured ? "text-emerald-100" : "text-slate-400"}`}>{unit}</div>}
        </div>
        <div className={`mt-3 inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full ${
          featured 
            ? "bg-white/20 text-white" 
            : positive ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"
        }`}>
          {delta}
        </div>
      </div>
      
      {/* Illustration vignette */}
      <div className="absolute -right-4 -bottom-4 w-20 h-20 opacity-80 group-hover:scale-110 group-hover:opacity-100 transition-all duration-500 pointer-events-none">
        <img src={illustration} alt="" className="w-full h-full object-contain drop-shadow-sm" />
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [productions, setProductions] = useState<Production[]>([]);
  const [summaries, setSummaries] = useState<Record<string, ProductionSummary>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const prods = await api.getProductions();
        if (cancelled) return;
        setProductions(prods);

        // Fetch summaries in parallel
        const summaryMap: Record<string, ProductionSummary> = {};
        await Promise.all(
          prods.map(async (p) => {
            try {
              const s = await api.getSummary(p.production_id);
              summaryMap[p.production_id] = s;
            } catch {
              // no events yet
            }
          })
        );
        if (!cancelled) setSummaries(summaryMap);
      } catch (e: any) {
        if (!cancelled) setError(e.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  // Compute aggregates
  const activeProductions = productions.filter((p) =>
    ["DEVELOPMENT", "PRE_PRODUCTION", "PRODUCTION", "POST_PRODUCTION", "DISTRIBUTION"].includes(p.status)
  );

  const totalTco2e = Object.values(summaries).reduce((sum, s) => sum + (s?.total_tco2e || 0), 0);
  const totalEvents = Object.values(summaries).reduce((sum, s) => sum + (s?.event_count || 0), 0);

  const scopeAgg: Record<string, number> = {};
  Object.values(summaries).forEach((s) => {
    Object.entries(s.scope_breakdown || {}).forEach(([k, v]) => {
      scopeAgg[k] = (scopeAgg[k] || 0) + (v as number);
    });
  });

  const scopeData = Object.entries(scopeAgg).map(([name, value]) => ({
    name,
    value: Math.round(value * 10) / 10,
    color: SCOPE_COLORS[name] || "#94a3b8",
  }));

  const phaseAgg: Record<string, number> = {};
  Object.values(summaries).forEach((s) => {
    Object.entries(s.phase_breakdown || {}).forEach(([k, v]) => {
      phaseAgg[k] = (phaseAgg[k] || 0) + (v as number);
    });
  });

  const phaseData = [
    { phase: "Dev", tco2e: Math.round((phaseAgg["DEVELOPMENT"] || 0) * 10) / 10 },
    { phase: "Pre-prod", tco2e: Math.round((phaseAgg["PRE_PRODUCTION"] || 0) * 10) / 10 },
    { phase: "Shoot", tco2e: Math.round((phaseAgg["PRODUCTION"] || 0) * 10) / 10 },
    { phase: "Post", tco2e: Math.round((phaseAgg["POST_PRODUCTION"] || 0) * 10) / 10 },
    { phase: "Dist", tco2e: Math.round((phaseAgg["DISTRIBUTION"] || 0) * 10) / 10 },
  ].filter((d) => d.tco2e > 0);

  // Weighted overall confidence
  let weightedConfidence = 0;
  let confWeight = 0;
  Object.values(summaries).forEach((s) => {
    if (s.total_tco2e > 0) {
      weightedConfidence += s.overall_confidence * s.total_tco2e;
      confWeight += s.total_tco2e;
    }
  });
  const overallConfidence = confWeight > 0 ? weightedConfidence / confWeight : 0;

  // Budget variance (average across productions that have budgets)
  let budgetVarSum = 0;
  let budgetVarCount = 0;
  Object.values(summaries).forEach((s) => {
    if (s.budget_variance_percent !== null) {
      budgetVarSum += s.budget_variance_percent;
      budgetVarCount++;
    }
  });
  const avgBudgetVar = budgetVarCount > 0 ? budgetVarSum / budgetVarCount : null;

  // Anomalies count (placeholder until we have real anomaly data)
  const anomalyCount = 0;

  // Fetch top recommendations from first production with data
  const [recommendations, setRecommendations] = useState<any[]>([]);
  useEffect(() => {
    async function loadRecs() {
      const ids = Object.keys(summaries);
      if (!ids.length) return;
      for (const id of ids.slice(0, 3)) {
        try {
          const data = await api.getRecommendations(id);
          if (data.recommendations.length) {
            setRecommendations(data.recommendations.slice(0, 3));
            break;
          }
        } catch {
          // ignore
        }
      }
    }
    if (!loading && Object.keys(summaries).length > 0) {
      loadRecs();
    }
  }, [loading, summaries]);

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="animate-spin w-6 h-6 text-emerald-500" />
      </div>
    );
  }

  if (error) {
    return <div className="terra-card p-6 text-red-600 text-sm">{error}</div>;
  }

  return (
    <div className="space-y-6">
      {/* Hero */}
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-8 terra-hero p-6 relative overflow-hidden">
          <div className="relative z-10 max-w-md">
            <div className="inline-flex items-center gap-2 bg-white/15 backdrop-blur px-3 py-1 rounded-full text-xs font-medium">
              <Leaf weight="fill" className="w-3 h-3" /> This quarter
            </div>
            <h2 className="mt-4 text-2xl font-semibold leading-tight">
              You're tracking{" "}
              <span className="text-amber-300">
                {avgBudgetVar !== null && avgBudgetVar <= 0
                  ? `${Math.abs(avgBudgetVar).toFixed(0)}% below`
                  : avgBudgetVar !== null
                  ? `${avgBudgetVar.toFixed(0)}% above`
                  : "—"}
              </span>{" "}
              your carbon budget 🌱
            </h2>
            <div className="mt-4 flex items-baseline gap-2">
              <span className="text-4xl font-bold">{totalTco2e.toFixed(1)}</span>
              <span className="text-emerald-100">tCO₂e emitted</span>
            </div>
            <p className="mt-1 text-sm text-emerald-50/80">
              Across {activeProductions.length} active production{activeProductions.length === 1 ? "" : "s"} · {totalEvents} logged event{totalEvents === 1 ? "" : "s"}
            </p>
            <Link
              to="/productions"
              className="mt-5 inline-flex items-center gap-2 bg-white text-emerald-700 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-emerald-50"
            >
              View report <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          <div className="absolute -right-16 -top-16 w-72 h-72 rounded-full bg-white/10 blur-2xl" />
          <div className="absolute right-8 bottom-0 w-48 h-24 rounded-full bg-amber-300/20 blur-2xl" />
          <img
            src={heroPlanet}
            alt=""
            className="hidden md:block absolute -right-2 -bottom-6 w-72 lg:w-80 pointer-events-none select-none illus-shadow"
          />
        </div>

        {/* Scope donut */}
        <div className="col-span-12 lg:col-span-4 terra-card p-5 flex flex-col">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">Scope mix</div>
              <div className="text-lg font-semibold text-slate-800 mt-0.5">{totalTco2e.toFixed(1)} tCO₂e</div>
            </div>
          </div>

          <div className="mt-2">
            <ResponsiveContainer width="100%" height={172}>
              <PieChart margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
                <Pie
                  data={scopeData.length ? scopeData : [{ name: "No data", value: 1, color: "#e2e8f0" }]}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={70}
                  paddingAngle={4}
                  dataKey="value"
                  strokeWidth={0}
                >
                  {(scopeData.length ? scopeData : [{ name: "No data", value: 1, color: "#e2e8f0" }]).map((s, i) => (
                    <Cell key={`cell-${i}`} fill={s.color} stroke="none" />
                  ))}
                </Pie>
                <Tooltip content={<PieTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2 mt-2">
            {scopeData.map((s) => (
              <div key={s.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ background: s.color }} />
                  <span className="text-sm text-slate-600">{s.name.replace(/_/g, " ")}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-20 h-1.5 rounded-full bg-slate-100 overflow-hidden">
                    <div className="h-full rounded-full" style={{ width: `${totalTco2e ? Math.min(100, (s.value / totalTco2e) * 100) : 0}%`, background: s.color }} />
                  </div>
                  <span className="text-sm font-semibold text-slate-800 w-8 text-right">{Math.round((s.value / totalTco2e) * 100) || 0}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPI label="Total tCO₂e" value={totalTco2e.toFixed(1)} delta="Across all productions" positive illustration={kpiCarbon} featured />
        <KPI label="Confidence" value={`${(overallConfidence * 100).toFixed(0)}%`} delta="Weighted avg" positive illustration={kpiConfidence} />
        <KPI label="Active productions" value={String(activeProductions.length)} delta="In progress" positive={activeProductions.length > 0} illustration={kpiProductions} />
        <KPI label="Anomalies open" value={String(anomalyCount)} delta="None detected" positive illustration={kpiAnomalies} />
      </div>

      {/* Phase breakdown + levers */}
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-8 terra-card p-5">
          <div className="flex items-center justify-between mb-6">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">Emissions by phase</div>
              <div className="text-lg font-semibold text-slate-900 mt-0.5">
                {phaseData.length ? `${phaseData.reduce((a, b) => (a.tco2e > b.tco2e ? a : b)).phase} is your hot spot` : "No phase data yet"}
              </div>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-slate-500">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block" />
              tCO₂e
            </div>
          </div>
          <div className="h-56">
            {phaseData.length > 0 ? (
              <ResponsiveContainer>
                <BarChart data={phaseData} barSize={36} margin={{ top: 4, right: 4, bottom: 0, left: -16 }}>
                  <defs>
                    <linearGradient id="bar-grad" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stopColor="#10b981" stopOpacity={1} />
                      <stop offset="100%" stopColor="#6ee7b7" stopOpacity={0.8} />
                    </linearGradient>
                    <linearGradient id="bar-grad-hot" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stopColor="#065f46" stopOpacity={1} />
                      <stop offset="100%" stopColor="#10b981" stopOpacity={0.9} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="#f1f5f9" />
                  <XAxis
                    dataKey="phase"
                    tickLine={false}
                    axisLine={false}
                    tick={{ fontSize: 12, fill: "#94a3b8", fontFamily: "inherit" }}
                  />
                  <YAxis
                    tickLine={false}
                    axisLine={false}
                    tick={{ fontSize: 11, fill: "#94a3b8", fontFamily: "inherit" }}
                    tickFormatter={(v) => `${v}`}
                  />
                  <Tooltip
                    content={<ChartTooltip unit="tCO₂e" />}
                    cursor={{ fill: "rgba(16,185,129,0.06)", radius: 8 }}
                  />
                  <Bar
                    dataKey="tco2e"
                    radius={[10, 10, 4, 4]}
                    label={false}
                  >
                    {phaseData.map((entry) => (
                      <Cell
                        key={entry.phase}
                        fill={entry.tco2e === Math.max(...phaseData.map((d) => d.tco2e)) ? "url(#bar-grad-hot)" : "url(#bar-grad)"}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-sm text-slate-400">
                Log activity events to see phase breakdowns
              </div>
            )}
          </div>
        </div>

        <div className="col-span-12 lg:col-span-4 terra-card terra-tile-cream p-5 relative overflow-hidden">
          <img
            src={leafSwirl}
            alt=""
            className="absolute -right-8 -top-8 w-40 pointer-events-none select-none illus-shadow-soft"
          />
          <div className="relative text-xs font-semibold uppercase tracking-wider text-slate-600">Reduction levers</div>
          <div className="relative text-lg font-semibold text-slate-900 mt-0.5 mb-4">Quick wins this week</div>
          <ul className="relative space-y-2">
            {recommendations.length > 0 ? (
              recommendations.map((r) => (
                <li key={r.id} className="flex items-start justify-between gap-3 p-3 rounded-lg bg-white/70 backdrop-blur-sm hover:bg-white transition">
                  <div>
                    <div className="text-sm text-slate-700 font-medium">{r.action}</div>
                    <div className="text-[11px] text-slate-500 mt-0.5">{r.playbook} · {r.effort} effort</div>
                  </div>
                  <span className="text-xs font-semibold text-emerald-700 whitespace-nowrap">
                    -{r.estimated_saving_tco2e.toFixed(1)} tCO₂e
                  </span>
                </li>
              ))
            ) : (
              <li className="text-sm text-slate-500 p-3">
                Log activity events to generate personalised reduction recommendations.
              </li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
