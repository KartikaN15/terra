import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api, type Production, type ProductionSummary } from "../api";
import {
  CircleNotch as Loader2,
  ArrowLeft,
  Leaf,
  Printer,
  ChartPieSlice,
  Stack,
  ListChecks,
  CheckCircle,
  CalendarBlank,
  Lightning,
} from "@phosphor-icons/react";
import mascot from "../assets/illustrations/mascot-terra.png";

const SCOPE_COLORS: Record<string, string> = {
  SCOPE_1: "#10b981",
  SCOPE_2: "#34d399",
  SCOPE_3: "#f59e0b",
};

export default function ProductionReport() {
  const { id } = useParams<{ id: string }>();
  const [prod, setProd] = useState<Production | null>(null);
  const [summary, setSummary] = useState<ProductionSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [recommendations, setRecommendations] = useState<any[]>([]);

  useEffect(() => {
    if (!id) return;
    Promise.all([
      api.getProduction(id),
      api.getSummary(id).catch(() => null),
      api.getRecommendations(id).catch(() => ({ recommendations: [] })),
    ])
      .then(([p, s, r]) => {
        setProd(p);
        setSummary(s);
        setRecommendations(r.recommendations || []);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  const handlePrint = () => window.print();

  if (loading)
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="animate-spin w-6 h-6 text-emerald-500" />
      </div>
    );
  if (error) return <div className="terra-card p-6 text-red-600 text-sm">{error}</div>;
  if (!prod) return <div className="terra-card p-6 text-slate-500 text-sm">Production not found</div>;

  const scopeEntries = summary
    ? Object.entries(summary.scope_breakdown).map(([k, v]) => ({ name: k, value: v as number }))
    : [];
  const catEntries = summary
    ? Object.entries(summary.category_breakdown).map(([k, v]) => ({ name: k, value: v as number }))
    : [];
  const totalScope = scopeEntries.reduce((a, b) => a + b.value, 0) || 1;

  return (
    <div className="space-y-6 print:space-y-4">
      {/* Toolbar (hidden in print) */}
      <div className="flex items-center justify-between print:hidden">
        <Link
          to={`/productions/${id}`}
          className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-emerald-700 font-medium"
        >
          <ArrowLeft className="w-4 h-4" /> Back to production
        </Link>
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrint}
            className="inline-flex items-center gap-2 bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-emerald-700 shadow-sm"
          >
            <Printer weight="duotone" className="w-4 h-4" /> Print / Save PDF
          </button>
        </div>
      </div>

      {/* Report Header */}
      <div className="terra-hero p-8 relative overflow-hidden print:bg-emerald-800 print:text-white">
        <div className="relative z-10 flex items-start justify-between gap-6 flex-wrap">
          <div>
            <div className="inline-flex items-center gap-2 bg-white/15 backdrop-blur px-3 py-1 rounded-full text-xs font-medium print:bg-white/20">
              <Leaf weight="fill" className="w-3 h-3" />
              Sustainability Report
            </div>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight">{prod.title}</h1>
            <p className="text-emerald-50/90 text-sm mt-1">
              {prod.type} · {prod.genre || "No genre"} ·{" "}
              {prod.budget_band?.replace(/_/g, " ") || "Unclassified budget"}
            </p>
            <p className="text-emerald-50/70 text-xs mt-2">
              <CalendarBlank className="w-3 h-3 inline mr-1" />
              Generated {new Date().toLocaleDateString()}
            </p>
          </div>
          {summary && (
            <div className="text-right">
              <div className="text-emerald-50/80 text-xs uppercase tracking-wider">Total footprint</div>
              <div className="text-5xl font-bold leading-none mt-1">{summary.total_tco2e.toFixed(1)}</div>
              <div className="text-emerald-50/90 text-sm mt-1">tCO₂e</div>
            </div>
          )}
        </div>
        <div className="absolute -right-16 -top-16 w-72 h-72 rounded-full bg-white/10 blur-2xl" />
        <img
          src={mascot}
          alt=""
          className="hidden md:block absolute right-12 -bottom-2 w-24 pointer-events-none select-none illus-shadow print:hidden"
        />
      </div>

      {/* KPIs */}
      {summary && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 print:grid-cols-4">
          <div className="terra-card p-4 print:border print:border-slate-200">
            <div className="text-xs text-slate-500">Confidence</div>
            <div className="text-2xl font-semibold text-slate-900 mt-1">
              {(summary.overall_confidence * 100).toFixed(0)}%
            </div>
          </div>
          <div className="terra-card p-4 print:border print:border-slate-200">
            <div className="text-xs text-slate-500">Events logged</div>
            <div className="text-2xl font-semibold text-slate-900 mt-1">{summary.event_count}</div>
          </div>
          <div className="terra-card p-4 print:border print:border-slate-200">
            <div className="text-xs text-slate-500">Budget variance</div>
            <div className="text-2xl font-semibold text-slate-900 mt-1">
              {summary.budget_variance_percent !== null
                ? `${summary.budget_variance_percent.toFixed(1)}%`
                : "—"}
            </div>
          </div>
          <div className="terra-card p-4 print:border print:border-slate-200">
            <div className="text-xs text-slate-500">Tier 1 data</div>
            <div className="text-2xl font-semibold text-slate-900 mt-1">
              {summary.tier_1_percent.toFixed(0)}%
            </div>
          </div>
        </div>
      )}

      {/* Scope + Category */}
      {summary && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 print:grid-cols-2">
          <div className="terra-card p-5 print:border print:border-slate-200">
            <div className="flex items-center gap-2 mb-4">
              <ChartPieSlice weight="duotone" className="w-5 h-5 text-emerald-600" />
              <h3 className="font-semibold text-slate-800">Scope breakdown</h3>
            </div>
            <div className="space-y-3">
              {scopeEntries.map((s) => {
                const pct = (s.value / totalScope) * 100;
                const color = SCOPE_COLORS[s.name] || "#94a3b8";
                return (
                  <div key={s.name}>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-slate-700">{s.name.replace(/_/g, " ")}</span>
                      <span className="font-semibold text-slate-900">{s.value.toFixed(1)} t ({pct.toFixed(0)}%)</span>
                    </div>
                    <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: `${pct}%`, background: color }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="terra-card p-5 print:border print:border-slate-200">
            <div className="flex items-center gap-2 mb-4">
              <Stack weight="duotone" className="w-5 h-5 text-emerald-600" />
              <h3 className="font-semibold text-slate-800">Category breakdown</h3>
            </div>
            <div className="space-y-2">
              {catEntries
                .sort((a, b) => b.value - a.value)
                .map((c) => (
                  <div key={c.name} className="flex items-center justify-between text-sm">
                    <span className="text-slate-700">{c.name.replace(/_/g, " ")}</span>
                    <span className="font-semibold text-slate-900">{c.value.toFixed(1)} t</span>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="terra-card p-5 print:border print:border-slate-200">
          <div className="flex items-center gap-2 mb-4">
            <Lightning weight="duotone" className="w-5 h-5 text-emerald-600" />
            <h3 className="font-semibold text-slate-800">OED Recommendations</h3>
          </div>
          <div className="space-y-3">
            {recommendations.slice(0, 5).map((r) => (
              <div key={r.id} className="flex items-start gap-3 p-3 rounded-lg bg-slate-50 print:bg-white print:border print:border-slate-200">
                <CheckCircle weight="duotone" className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm font-medium text-slate-800">{r.action}</div>
                  <div className="text-xs text-slate-500 mt-0.5">{r.description}</div>
                </div>
                <div className="text-right shrink-0">
                  <div className="text-sm font-semibold text-emerald-700">
                    -{r.estimated_saving_tco2e.toFixed(1)} tCO₂e
                  </div>
                  <div className="text-[10px] text-slate-400">{r.playbook}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Audit & certification footer */}
      <div className="terra-card p-5 print:border print:border-slate-200">
        <div className="flex items-center gap-2 mb-3">
          <ListChecks weight="duotone" className="w-5 h-5 text-emerald-600" />
          <h3 className="font-semibold text-slate-800">Audit Trail</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-600">
          <div>
            <span className="text-slate-400">Production ID:</span>{" "}
            <span className="font-mono text-xs">{prod.production_id}</span>
          </div>
          <div>
            <span className="text-slate-400">Status:</span>{" "}
            {prod.status.replace(/_/g, " ")}
          </div>
          <div>
            <span className="text-slate-400">Created:</span>{" "}
            {new Date(prod.created_at).toLocaleDateString()}
          </div>
          <div>
            <span className="text-slate-400">Report generated:</span>{" "}
            {new Date().toLocaleDateString()} {new Date().toLocaleTimeString()}
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-slate-100 text-xs text-slate-400">
          This report was generated automatically by Terra Sustainability Intelligence Platform.
          Emission calculations follow GHG Protocol Corporate Standard and BAFTA albert Calculator Methodology.
          Data quality tiers: Tier 1 = direct measurement, Tier 2 = benchmark/spend-based, Tier 3 = ML-imputed.
        </div>
      </div>
    </div>
  );
}
