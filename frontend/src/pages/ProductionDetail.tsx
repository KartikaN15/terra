import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  api,
  type Production,
  type ProductionSummary,
  type ActivityEvent,
} from "../api";
import {
  CircleNotch as Loader2,
  ArrowLeft,
  Leaf,
  ChartPieSlice,
  Stack,
  Gauge,
  ListChecks,
  Target,
  Plus,
  CalendarBlank,
  FileCsv,
  Lightning,
  Printer,
} from "@phosphor-icons/react";
import mascot from "../assets/illustrations/mascot-terra.png";
import AddEventModal from "../components/AddEventModal";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";
import { ChartTooltip, PieTooltip } from "../components/ChartTooltip";

const SCOPE_COLORS: Record<string, string> = {
  SCOPE_1: "#10b981",
  SCOPE_2: "#34d399",
  SCOPE_3: "#f59e0b",
};

const CATEGORY_COLORS = [
  "#10b981",
  "#34d399",
  "#f59e0b",
  "#fbbf24",
  "#0ea5e9",
  "#8b5cf6",
  "#ec4899",
  "#06b6d4",
];

function KPI({
  icon: Icon,
  label,
  value,
  hint,
  tone = "emerald",
}: {
  icon: any;
  label: string;
  value: string;
  hint?: string;
  tone?: "emerald" | "amber" | "slate";
}) {
  const toneMap = {
    emerald: "bg-emerald-50 text-emerald-600",
    amber: "bg-amber-50 text-amber-600",
    slate: "bg-slate-100 text-slate-600",
  };
  return (
    <div className="terra-card p-5">
      <div className="flex items-center justify-between">
        <div className="text-sm text-slate-500">{label}</div>
        <div
          className={`w-8 h-8 rounded-lg flex items-center justify-center ${toneMap[tone]}`}
        >
          <Icon weight="duotone" className="w-5 h-5" />
        </div>
      </div>
      <div className="mt-2 text-2xl font-semibold text-slate-900">{value}</div>
      {hint && <div className="text-xs text-slate-400 mt-1">{hint}</div>}
    </div>
  );
}

export default function ProductionDetail() {
  const { id } = useParams<{ id: string }>();
  const [prod, setProd] = useState<Production | null>(null);
  const [summary, setSummary] = useState<ProductionSummary | null>(null);
  const [events, setEvents] = useState<ActivityEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showEventModal, setShowEventModal] = useState(false);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const loadData = async (productionId: string) => {
    setLoading(true);
    try {
      const [p, e, s] = await Promise.all([
        api.getProduction(productionId),
        api.getEvents(productionId),
        api.getSummary(productionId).catch(() => null),
      ]);
      setProd(p);
      setEvents(e);
      setSummary(s);
      setError("");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!id) return;
    loadData(id);
  }, [id]);

  const handleEventCreated = (evt: ActivityEvent) => {
    setEvents((prev) => [evt, ...prev]);
    // Refresh summary so charts update
    if (id) {
      api.getSummary(id).then((s) => setSummary(s)).catch(() => {});
    }
  };

  useEffect(() => {
    if (!id || !summary) return;
    api.getRecommendations(id)
      .then((data) => setRecommendations(data.recommendations.slice(0, 4)))
      .catch(() => setRecommendations([]));
  }, [id, summary]);

  if (loading)
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="animate-spin w-6 h-6 text-emerald-500" />
      </div>
    );
  if (error)
    return (
      <div className="terra-card p-6 text-red-600 text-sm">{error}</div>
    );
  if (!prod)
    return (
      <div className="terra-card p-6 text-slate-500 text-sm">
        Production not found
      </div>
    );

  const scopeData = summary
    ? Object.entries(summary.scope_breakdown).map(([name, value]) => ({
        name,
        value,
      }))
    : [];
  const catData = summary
    ? Object.entries(summary.category_breakdown).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  return (
    <div className="space-y-6">
      <Link
        to="/productions"
        className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-emerald-700 font-medium"
      >
        <ArrowLeft className="w-4 h-4" /> Back to productions
      </Link>

      {/* Hero */}
      <div className="terra-hero p-7 relative overflow-hidden">
        <div className="relative z-10 flex items-start justify-between gap-6 flex-wrap">
          <div>
            <div className="inline-flex items-center gap-2 bg-white/15 backdrop-blur px-3 py-1 rounded-full text-xs font-medium">
              <Leaf weight="fill" className="w-3 h-3" />{" "}
              {prod.status.replace(/_/g, " ")}
            </div>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight">
              {prod.title}
            </h1>
            <p className="text-emerald-50/90 text-sm mt-1">
              {prod.type} · {prod.genre || "No genre"} ·{" "}
              {prod.budget_band?.replace(/_/g, " ") || "Unclassified budget"}
            </p>
          </div>
          {summary && (
            <div className="text-right">
              <div className="text-emerald-50/80 text-xs uppercase tracking-wider">
                Total emitted
              </div>
              <div className="text-5xl font-bold leading-none mt-1">
                {summary.total_tco2e.toFixed(1)}
              </div>
              <div className="text-emerald-50/90 text-sm mt-1">tCO₂e</div>
              <div className="mt-3 flex items-center gap-2">
                <button
                  onClick={() => api.downloadAlbertCSV(prod.production_id)}
                  className="inline-flex items-center gap-1.5 bg-white/20 hover:bg-white/30 backdrop-blur text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition"
                >
                  <FileCsv weight="duotone" className="w-3.5 h-3.5" /> Albert CSV
                </button>
                <Link
                  to={`/productions/${prod.production_id}/designer`}
                  className="inline-flex items-center gap-1.5 bg-white/20 hover:bg-white/30 backdrop-blur text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition"
                >
                  <CalendarBlank weight="duotone" className="w-3.5 h-3.5" /> Planner
                </Link>
                <Link
                  to={`/productions/${prod.production_id}/report`}
                  className="inline-flex items-center gap-1.5 bg-white/20 hover:bg-white/30 backdrop-blur text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition"
                >
                  <Printer weight="duotone" className="w-3.5 h-3.5" /> Report
                </Link>
              </div>
            </div>
          )}
        </div>
        <div className="absolute -right-16 -top-16 w-72 h-72 rounded-full bg-white/10 blur-2xl" />
        <div className="absolute -right-6 bottom-0 w-40 h-40 rounded-full bg-amber-300/20 blur-xl" />
        <img
          src={mascot}
          alt=""
          className="hidden md:block absolute right-48 lg:right-64 -bottom-2 w-32 pointer-events-none select-none illus-shadow"
        />
      </div>

      {summary && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <KPI
              icon={Gauge}
              label="Confidence"
              value={`${(summary.overall_confidence * 100).toFixed(0)}%`}
              hint="Weighted across all events"
            />
            <KPI
              icon={ListChecks}
              label="Events"
              value={String(summary.event_count)}
              hint="Logged activity records"
            />
            <KPI
              icon={Target}
              label="Budget variance"
              value={
                summary.budget_variance_percent !== null
                  ? `${summary.budget_variance_percent.toFixed(1)}%`
                  : "—"
              }
              hint="vs carbon budget"
              tone={
                (summary.budget_variance_percent ?? 0) > 0 ? "amber" : "emerald"
              }
            />
            <KPI
              icon={Leaf}
              label={summary.intensity_tco2e_per_episode !== null ? "tCO₂e / episode" : "tCO₂e / hr"}
              value={
                summary.intensity_tco2e_per_episode !== null
                  ? summary.intensity_tco2e_per_episode.toFixed(2)
                  : summary.intensity_tco2e_per_hour !== null
                  ? summary.intensity_tco2e_per_hour.toFixed(2)
                  : "—"
              }
              hint="Carbon intensity metric"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="terra-card p-5">
              <div className="flex items-center gap-2 mb-4">
                <ChartPieSlice weight="duotone" className="w-5 h-5 text-emerald-600" />
                <h3 className="font-semibold text-slate-800">Scope breakdown</h3>
              </div>
              <ResponsiveContainer width="100%" height={210}>
                <PieChart margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
                  <Pie
                    data={scopeData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={52}
                    outerRadius={72}
                    paddingAngle={4}
                    strokeWidth={0}
                  >
                    {scopeData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={SCOPE_COLORS[entry.name] || CATEGORY_COLORS[index % CATEGORY_COLORS.length]}
                        stroke="none"
                      />
                    ))}
                  </Pie>
                  <Tooltip content={<PieTooltip />} />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-2 mt-3">
                {scopeData.map((s, i) => {
                  const color = SCOPE_COLORS[s.name] || CATEGORY_COLORS[i % CATEGORY_COLORS.length];
                  const total = scopeData.reduce((a, b) => a + b.value, 0);
                  const pct = total ? Math.round((s.value / total) * 100) : 0;
                  return (
                    <div key={s.name} className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full shrink-0" style={{ background: color }} />
                      <span className="text-xs text-slate-600 flex-1">{s.name.replace(/_/g, " ")}</span>
                      <div className="w-24 h-1.5 rounded-full bg-slate-100 overflow-hidden">
                        <div className="h-full rounded-full" style={{ width: `${pct}%`, background: color }} />
                      </div>
                      <span className="text-xs font-semibold text-slate-700 w-12 text-right">
                        {s.value.toFixed(1)} t
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="terra-card p-5">
              <div className="flex items-center gap-2 mb-4">
                <Stack weight="duotone" className="w-5 h-5 text-emerald-600" />
                <h3 className="font-semibold text-slate-800">Category breakdown</h3>
              </div>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={catData} barSize={28} margin={{ top: 4, right: 4, bottom: 0, left: -16 }}>
                  <defs>
                    <linearGradient id="cat-bar" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stopColor="#10b981" />
                      <stop offset="100%" stopColor="#6ee7b7" stopOpacity={0.8} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="#f1f5f9" />
                  <XAxis
                    dataKey="name"
                    tick={{ fontSize: 10, fill: "#94a3b8", fontFamily: "inherit" }}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 10, fill: "#94a3b8", fontFamily: "inherit" }}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip
                    content={<ChartTooltip unit="tCO₂e" />}
                    cursor={{ fill: "rgba(16,185,129,0.06)", radius: 8 }}
                  />
                  <Bar dataKey="value" fill="url(#cat-bar)" radius={[8, 8, 4, 4]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}

      {recommendations.length > 0 && (
        <div className="terra-card p-5">
          <div className="flex items-center gap-2 mb-4">
            <Lightning weight="duotone" className="w-5 h-5 text-emerald-600" />
            <h3 className="font-semibold text-slate-800">OED Recommendations</h3>
            <span className="ml-auto text-xs text-slate-400">
              Potential saving: {recommendations.reduce((a, r) => a + (r.estimated_saving_tco2e || 0), 0).toFixed(1)} tCO₂e
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {recommendations.map((r) => (
              <div key={r.id} className="p-3 rounded-lg border border-slate-100 bg-slate-50/50 hover:bg-white hover:shadow-sm transition">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                    {r.playbook}
                  </span>
                  <span className="text-xs text-slate-500">{r.effort} effort</span>
                </div>
                <div className="mt-2 text-sm font-medium text-slate-800">{r.action}</div>
                <div className="mt-1 text-xs text-slate-500">{r.description}</div>
                <div className="mt-2 text-xs font-semibold text-emerald-700">
                  Save ~{r.estimated_saving_tco2e.toFixed(1)} tCO₂e
                  {r.estimated_cost_gbp !== null && (
                    <span className="text-slate-400 font-normal ml-1">
                      · {r.estimated_cost_gbp >= 0 ? `£${r.estimated_cost_gbp}` : `Save £${Math.abs(r.estimated_cost_gbp)}`}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="terra-card overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ListChecks
              weight="duotone"
              className="w-5 h-5 text-emerald-600"
            />
            <h3 className="font-semibold text-slate-800">Activity events</h3>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-500">
              {events.length} total · showing {Math.min(events.length, 20)}
            </span>
            <button
              onClick={() => setShowEventModal(true)}
              className="inline-flex items-center gap-1.5 bg-emerald-600 text-white px-3 py-1.5 rounded-lg text-xs font-semibold hover:bg-emerald-700 shadow-sm"
            >
              <Plus weight="bold" className="w-3.5 h-3.5" /> Log Event
            </button>
          </div>
        </div>
        <table className="w-full text-sm text-left">
          <thead className="bg-slate-50/60 text-slate-500 text-xs uppercase tracking-wider font-medium border-b border-slate-100">
            <tr>
              <th className="px-5 py-3">Date</th>
              <th className="px-5 py-3">Category</th>
              <th className="px-5 py-3">Subcategory</th>
              <th className="px-5 py-3">Value</th>
              <th className="px-5 py-3">kgCO₂e</th>
              <th className="px-5 py-3">Tier</th>
            </tr>
          </thead>
          <tbody>
            {events.slice(0, 20).map((e) => (
              <tr
                key={e.event_id}
                className="border-b border-slate-100 last:border-0 hover:bg-emerald-50/30"
              >
                <td className="px-5 py-3 text-slate-600">
                  {new Date(e.recorded_at).toLocaleDateString()}
                </td>
                <td className="px-5 py-3 text-slate-700 font-medium">
                  {e.category}
                </td>
                <td className="px-5 py-3 text-slate-600">{e.subcategory}</td>
                <td className="px-5 py-3 text-slate-600">
                  {e.value} {e.unit}
                </td>
                <td className="px-5 py-3 font-medium text-slate-800">
                  {Number(e.kgco2e).toFixed(1)}
                </td>
                <td className="px-5 py-3">
                  <span
                    className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      e.confidence_tier === "TIER_1_DIRECT"
                        ? "bg-emerald-50 text-emerald-700"
                        : e.confidence_tier === "TIER_2_BENCHMARK"
                        ? "bg-amber-50 text-amber-700"
                        : "bg-red-50 text-red-700"
                    }`}
                  >
                    {e.confidence_tier
                      .replace("TIER_1_", "T1 · ")
                      .replace("TIER_2_", "T2 · ")
                      .replace("TIER_3_", "T3 · ")}
                  </span>
                </td>
              </tr>
            ))}
            {events.length === 0 && (
              <tr>
                <td
                  colSpan={6}
                  className="px-5 py-12 text-center text-slate-500 text-sm"
                >
                  No events logged for this production yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showEventModal && id && (
        <AddEventModal
          productionId={id}
          onClose={() => setShowEventModal(false)}
          onCreated={handleEventCreated}
        />
      )}
    </div>
  );
}
