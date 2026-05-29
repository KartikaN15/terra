import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type Production, type ProductionSummary } from "../api";
import { useToast } from "../contexts/ToastContext";
import { useConfirm } from "../contexts/ConfirmContext";
import {
  CircleNotch as Loader2,
  Trash as Trash2,
  Plus,
  FilmSlate,
  FunnelSimple,
  TrendUp,
  TrendDown,
  ArrowRight,
} from "@phosphor-icons/react";
import filmSet from "../assets/illustrations/film-set.png";
import NewProductionModal from "../components/NewProductionModal";

const STATUS_STYLES: Record<string, string> = {
  DEVELOPMENT: "bg-slate-100 text-slate-700",
  PRE_PRODUCTION: "bg-blue-50 text-blue-700",
  PRODUCTION: "bg-emerald-50 text-emerald-700",
  POST_PRODUCTION: "bg-violet-50 text-violet-700",
  DISTRIBUTION: "bg-amber-50 text-amber-700",
  COMPLETED: "bg-slate-100 text-slate-500",
};

function MiniBar({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-1.5 rounded-full bg-slate-100 overflow-hidden">
        <div
          className="h-full rounded-full bg-emerald-400 transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs font-semibold text-slate-700 tabular-nums">
        {value.toFixed(1)}
      </span>
    </div>
  );
}

export default function ProductionsList() {
  const [productions, setProductions] = useState<Production[]>([]);
  const [summaries, setSummaries] = useState<Record<string, ProductionSummary>>({});
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const toast = useToast();
  const { confirm } = useConfirm();

  const load = async () => {
    setLoading(true);
    try {
      const prods = await api.getProductions();
      setProductions(prods);
      const map: Record<string, ProductionSummary> = {};
      await Promise.all(
        prods.map(async (p) => {
          try {
            map[p.production_id] = await api.getSummary(p.production_id);
          } catch {
            // no events yet   — leave undefined
          }
        })
      );
      setSummaries(map);
    } catch (e: any) {
      toast.error("Failed to load productions", e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleDelete = async (id: string, title: string) => {
    const ok = await confirm({
      title: `Delete "${title}"?`,
      message: "All activity events and documents for this production will be permanently deleted.",
      confirmLabel: "Delete",
      danger: true,
    });
    if (!ok) return;
    try {
      await api.deleteProduction(id);
      setProductions((prev) => prev.filter((p) => p.production_id !== id));
      setSummaries((prev) => { const n = { ...prev }; delete n[id]; return n; });
      toast.success("Production deleted");
    } catch (e: any) {
      toast.error("Delete failed", e.message);
    }
  };

  const handleCreated = (prod: Production) => {
    setProductions((prev) => [prod, ...prev]);
  };

  const maxTco2e = Math.max(
    ...Object.values(summaries).map((s) => s?.total_tco2e || 0),
    1
  );

  if (loading)
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="animate-spin w-6 h-6 text-emerald-500" />
      </div>
    );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="text-sm text-slate-500">
          {productions.length} production{productions.length === 1 ? "" : "s"} tracked
        </div>
        <div className="flex items-center gap-2">
          <button className="inline-flex items-center gap-2 bg-white text-slate-700 px-3 py-2 rounded-lg text-sm font-medium border border-slate-200 hover:bg-slate-50">
            <FunnelSimple weight="duotone" className="w-4 h-4" /> Filter
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="inline-flex items-center gap-2 bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-emerald-700 shadow-sm"
          >
            <Plus weight="bold" className="w-4 h-4" /> New Production
          </button>
        </div>
      </div>

      <div className="terra-card overflow-hidden">
        <table className="w-full text-sm text-left">
          <thead className="bg-slate-50/60 text-slate-500 text-xs uppercase tracking-wider font-medium border-b border-slate-100">
            <tr>
              <th className="px-5 py-3">Title</th>
              <th className="px-5 py-3">Status</th>
              <th className="px-5 py-3">Type</th>
              <th className="px-5 py-3">tCO₂e</th>
              <th className="px-5 py-3">vs Budget</th>
              <th className="px-5 py-3">Events</th>
              <th className="px-5 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {productions.map((p) => {
              const s = summaries[p.production_id];
              const tco2e = s?.total_tco2e ?? null;
              const variance = s?.budget_variance_percent ?? null;
              const overBudget = variance !== null && variance > 0;

              return (
                <tr
                  key={p.production_id}
                  className="border-b border-slate-100 last:border-0 hover:bg-emerald-50/30 transition-colors"
                >
                  <td className="px-5 py-4">
                    <Link
                      to={`/productions/${p.production_id}`}
                      className="flex items-center gap-3 group"
                    >
                      <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-100 to-emerald-50 flex items-center justify-center shrink-0">
                        <FilmSlate weight="duotone" className="w-5 h-5 text-emerald-600" />
                      </div>
                      <div className="min-w-0">
                        <div className="font-medium text-slate-800 group-hover:text-emerald-700 truncate">
                          {p.title}
                        </div>
                        {p.genre && (
                          <div className="text-xs text-slate-400 truncate">{p.genre}</div>
                        )}
                      </div>
                    </Link>
                  </td>

                  <td className="px-5 py-4">
                    <span
                      className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        STATUS_STYLES[p.status] || "bg-slate-100 text-slate-700"
                      }`}
                    >
                      {p.status.replace(/_/g, " ")}
                    </span>
                  </td>

                  <td className="px-5 py-4 text-slate-500 text-xs">
                    {p.type}
                    {p.budget_band && (
                      <div className="text-slate-400">{p.budget_band.replace(/_/g, " ")}</div>
                    )}
                  </td>

                  <td className="px-5 py-4">
                    {tco2e !== null ? (
                      <MiniBar value={tco2e} max={maxTco2e} />
                    ) : (
                      <span className="text-xs text-slate-400">No events</span>
                    )}
                  </td>

                  <td className="px-5 py-4">
                    {variance !== null ? (
                      <span
                        className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full ${
                          overBudget
                            ? "bg-amber-50 text-amber-700"
                            : "bg-emerald-50 text-emerald-700"
                        }`}
                      >
                        {overBudget ? (
                          <TrendUp weight="bold" className="w-3 h-3" />
                        ) : (
                          <TrendDown weight="bold" className="w-3 h-3" />
                        )}
                        {overBudget ? "+" : ""}
                        {variance.toFixed(1)}%
                      </span>
                    ) : (
                      <span className="text-xs text-slate-400">—</span>
                    )}
                  </td>

                  <td className="px-5 py-4 text-slate-500">
                    {s ? (
                      <span className="tabular-nums">{s.event_count}</span>
                    ) : (
                      <span className="text-slate-400">0</span>
                    )}
                  </td>

                  <td className="px-5 py-4">
                    <div className="flex items-center justify-end gap-1">
                      <Link
                        to={`/productions/${p.production_id}`}
                        className="p-1.5 rounded-md text-slate-400 hover:text-emerald-600 hover:bg-emerald-50"
                        title="View detail"
                      >
                        <ArrowRight className="w-4 h-4" />
                      </Link>
                      <button
                        onClick={() => handleDelete(p.production_id, p.title)}
                        className="p-1.5 rounded-md text-slate-400 hover:text-red-600 hover:bg-red-50"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
            {productions.length === 0 && (
              <tr>
                <td colSpan={7} className="px-5 py-16 text-center">
                  <div className="inline-flex flex-col items-center gap-3">
                    <img
                      src={filmSet}
                      alt=""
                      className="w-56 h-44 object-contain illus-shadow-soft"
                    />
                    <div className="text-slate-600 font-medium">No productions yet</div>
                    <div className="text-xs text-slate-400 max-w-xs">
                      Create one or run the backend seed script to load sample data.
                    </div>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <NewProductionModal
          onClose={() => setShowModal(false)}
          onCreated={handleCreated}
        />
      )}
    </div>
  );
}
